# rag.py - RAG Logic Module (FIXED VERSION)

import os
import time
import json
from typing import List, Dict, Any
from openai import OpenAI
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

# Environment variables
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/v1/")

# Initialize clients
qdrant_client = QdrantClient(QDRANT_URL)
openai_client = OpenAI(api_key=OPENAI_API_KEY)
ollama_client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")

# Initialize embedding model (matching your notebooks)
embedding_model = SentenceTransformer("jinaai/jina-embeddings-v2-small-en")

# Collection name for documents
COLLECTION_NAME = "travel-docs"

def qdrant_search(query: str, search_type: str = "semantic", limit: int = 5) -> List[Dict]:
    """
    Perform search using Qdrant vector database

    Args:
        query: Search query
        search_type: "semantic" or "hybrid"
        limit: Number of results to return

    Returns:
        List of search results
    """
    try:
        if search_type == "semantic":
            # Dense vector search (semantic) - FIXED: Added using parameter
            results = qdrant_client.query_points(
                collection_name=COLLECTION_NAME,
                query=models.Document(
                    text=query,
                    model="jinaai/jina-embeddings-v2-small-en"
                ),
                using="jina-small",  # FIXED: Specify the named vector to use
                limit=limit,
                with_payload=True
            )

            search_results = []
            for point in results.points:
                search_results.append({
                    "content": point.payload.get("content", ""),
                    "location": point.payload.get("location", ""),
                    "doc_id": point.payload.get("doc_id", ""),
                    "score": point.score
                })

        elif search_type == "hybrid":
            # Hybrid search using RRF (Reciprocal Rank Fusion) - FIXED
            results = qdrant_client.query_points(
                collection_name=COLLECTION_NAME,
                prefetch=[
                    # Dense vector prefetch
                    models.Prefetch(
                        query=models.Document(
                            text=query,
                            model="jinaai/jina-embeddings-v2-small-en"
                        ),
                        using="jina-small",  # FIXED: Specify named vector
                        limit=(5 * limit)
                    ),
                    # Sparse vector prefetch
                    models.Prefetch(
                        query=models.Document(
                            text=query,
                            model="Qdrant/bm25"
                        ),
                        using="bm25",  # FIXED: Specify named vector
                        limit=(5 * limit)
                    )
                ],
                # Apply RRF fusion
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                limit=limit,
                with_payload=True
            )

            search_results = []
            for point in results.points:
                search_results.append({
                    "content": point.payload.get("content", ""),
                    "location": point.payload.get("location", ""),
                    "doc_id": point.payload.get("doc_id", ""),
                    "score": point.score
                })

        return search_results

    except Exception as e:
        print(f"Search error: {e}")
        return []

def build_prompt(query: str, search_results: List[Dict]) -> str:
    """
    Build prompt for LLM using search results

    Args:
        query: User question
        search_results: Retrieved documents

    Returns:
        Formatted prompt string
    """
    prompt_template = """
You're a travel assistant bot that helps users plan their itinerary and discover amazing places to visit.
Answer the QUESTION based on the CONTEXT from the travel database.
Use only the facts from the CONTEXT when answering the QUESTION.

When answering, consider:
- Must-visit tourist attractions and landmarks
- Cultural experiences and local traditions
- Historical significance of places
- Best times to visit and travel tips
- Local cuisine and specialties (if mentioned in context)
- Transportation and accessibility information (if available)

QUESTION: {question}

CONTEXT:
{context}
""".strip()

    context = ""
    for doc in search_results:
        location = doc.get('location', 'Unknown')
        content = doc.get('content', doc.get('text', '')) # Handle both content and text fields
        context = context + f"location: {location}\ncontent: {content}\n\n"

    return prompt_template.format(question=query, context=context).strip()

def llm(prompt: str, model_choice: str) -> Dict[str, Any]:
    """
    Get response from LLM

    Args:
        prompt: Input prompt
        model_choice: Model to use (ollama/phi3, openai/gpt-3.5-turbo, etc.)

    Returns:
        Dictionary with answer, tokens, and response_time
    """
    start_time = time.time()

    try:
        if model_choice.startswith('ollama/'):
            response = ollama_client.chat.completions.create(
                model=model_choice.split('/')[-1],
                messages=[{"role": "user", "content": prompt}]
            )

            answer = response.choices[0].message.content
            tokens = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }

        elif model_choice.startswith('openai/'):
            response = openai_client.chat.completions.create(
                model=model_choice.split('/')[-1],
                messages=[{"role": "user", "content": prompt}]
            )

            answer = response.choices[0].message.content
            tokens = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }

        else:
            raise ValueError(f"Unknown model choice: {model_choice}")

    except Exception as e:
        print(f"LLM error: {e}")
        answer = f"Sorry, I encountered an error: {str(e)}"
        tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

    end_time = time.time()
    response_time = end_time - start_time

    return {
        'answer': answer,
        'tokens': tokens,
        'response_time': response_time
    }

def evaluate_relevance(question: str, answer: str) -> Dict[str, Any]:
    """
    Evaluate relevance of the generated answer

    Args:
        question: Original question
        answer: Generated answer

    Returns:
        Dictionary with relevance score and explanation
    """
    prompt_template = """
You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}

Generated Answer: {answer}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{
    "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
    "Explanation": "[Provide a brief explanation for your evaluation]"
}}
""".strip()

    prompt = prompt_template.format(question=question, answer=answer)

    try:
        eval_response = llm(prompt, 'openai/gpt-4o-mini')
        json_eval = json.loads(eval_response['answer'])

        return {
            'relevance': json_eval['Relevance'],
            'explanation': json_eval['Explanation'],
            'eval_tokens': eval_response['tokens']
        }

    except:
        return {
            'relevance': "UNKNOWN",
            'explanation': "Failed to parse evaluation",
            'eval_tokens': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        }

def calculate_openai_cost(model_choice: str, tokens: Dict) -> float:
    """
    Calculate OpenAI API costs

    Args:
        model_choice: Model used
        tokens: Token usage dictionary

    Returns:
        Cost in USD
    """
    openai_cost = 0

    if model_choice == 'openai/gpt-3.5-turbo':
        openai_cost = (tokens['prompt_tokens'] * 0.0015 + tokens['completion_tokens'] * 0.002) / 1000
    elif model_choice in ['openai/gpt-4o', 'openai/gpt-4o-mini']:
        openai_cost = (tokens['prompt_tokens'] * 0.03 + tokens['completion_tokens'] * 0.06) / 1000

    return openai_cost

def get_answer(query: str, model_choice: str, search_type: str = "semantic") -> Dict[str, Any]:
    """
    Main RAG function to get answer for a query

    Args:
        query: User question
        model_choice: LLM model to use
        search_type: "semantic" or "hybrid"

    Returns:
        Dictionary with answer and metadata
    """
    # Search for relevant documents
    search_results = qdrant_search(query, search_type)

    # Build prompt
    prompt = build_prompt(query, search_results)

    # Get LLM response
    llm_response = llm(prompt, model_choice)

    # Evaluate relevance
    relevance_data = evaluate_relevance(query, llm_response['answer'])

    # Calculate costs
    openai_cost = calculate_openai_cost(model_choice, llm_response['tokens'])

    return {
        'answer': llm_response['answer'],
        'response_time': llm_response['response_time'],
        'relevance': relevance_data['relevance'],
        'relevance_explanation': relevance_data['explanation'],
        'model_used': model_choice,
        'search_type': search_type,
        'prompt_tokens': llm_response['tokens']['prompt_tokens'],
        'completion_tokens': llm_response['tokens']['completion_tokens'],
        'total_tokens': llm_response['tokens']['total_tokens'],
        'eval_prompt_tokens': relevance_data['eval_tokens']['prompt_tokens'],
        'eval_completion_tokens': relevance_data['eval_tokens']['completion_tokens'],
        'eval_total_tokens': relevance_data['eval_tokens']['total_tokens'],
        'openai_cost': openai_cost,
        'search_results_count': len(search_results)
    }
