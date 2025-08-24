# Brahman.ai - Your Smart Travel Assistant
![images\Brahman.ai.png](https://github.com/Adityagurung/Brahman.ai/blob/35a28c05d99dd7777a4ec472cf12eac17f0b47e9/images/Brahman.ai.png) 


*[VIDEO PLACEHOLDER: Streamlit UI Demo - ]*

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Dataset/Data Sources](#datasetdata-sources)
- [Technologies Used](#technologies-used)
- [RAG Flow](#rag-flow)
- [Reproducibility](#reproducibility)
- [Evaluation Criteria](#evaluation-criteria)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Project Overview

Brahman.ai is a sophisticated Retrieval-Augmented Generation (RAG) system designed specifically for travel planning and destination discovery. This intelligent travel assistant combines the power of vector databases, multiple search strategies, and large language models to provide accurate, contextual, and helpful travel recommendations.

The system processes travel guide documents from Wikivoyage, creates a comprehensive knowledge base, and enables users to ask natural language questions about destinations, attractions, cultural experiences, and travel planning. What sets this project apart is its rigorous evaluation framework that compares multiple retrieval strategies and implements hybrid search for optimal performance.

**Key Features:**
- **Multi-Modal Search**: Combines semantic search, keyword search, and hybrid approaches
- **Real-time Evaluation**: Automatic relevance scoring and performance monitoring
- **Comprehensive Monitoring**: Grafana dashboard with detailed analytics
- **Scalable Architecture**: Docker-containerized microservices
- **Interactive Interface**: Streamlit-based web application
- **Robust Evaluation**: Extensive offline evaluation with multiple metrics

## Problem Statement

## Modern travelers face numerous challenges when planning their journeys:

**Information Overload**: Travelers are bombarded with scattered information across multiple websites, travel blogs, and guidebooks, making it difficult to find relevant and trustworthy information quickly.

**Generic Recommendations**: Most travel platforms provide generic, one-size-fits-all recommendations that don't consider individual preferences or specific contexts.

**Outdated Information**: Travel information becomes outdated quickly, and travelers often struggle to find current, accurate details about destinations.

**Language Barriers**: Accessing local travel information in native languages can be challenging for international travelers.

**Time-Intensive Research**: Planning a trip requires hours of research across multiple sources to gather comprehensive information about destinations, attractions, and logistics.

**How Brahman.ai Solves These Problems:**

Our AI-powered travel assistant revolutionizes trip planning by:
- **Centralized Knowledge Base**: Curated information from reliable sources like Wikivoyage
- **Intelligent Query Understanding**: Natural language processing to understand complex travel questions
- **Contextual Recommendations**: Personalized suggestions based on specific travel needs
- **Real-time Relevance**: Advanced search algorithms ensure the most relevant information surfaces first
- **Comprehensive Coverage**: From cultural experiences to practical travel tips, all in one place

## Data Source

Our primary data source is **[Wikivoyage](https://en.wikivoyage.org/wiki/Main_Page)**, a collaborative, free, and open-source travel guide. Wikivoyage provides comprehensive, up-to-date travel information with a focus on practical advice for travelers.

**Data Processing Pipeline:**
1. **PDF Download**: Direct download from Wikivoyage website
2. **Storage**: Raw PDFs stored in `data/raw/` directory
3. **Processing**: Automated conversion and chunking (see [Ingestion Pipeline](https://github.com/Adityagurung/Brahman.ai/blob/38691d2e41d00408cc939daf3bed3e6216d31e59/notebooks/1_process_pdf2Jsonl.ipynb))
4. **Indexing**: Vector embeddings and search index creation

## Technologies Used

Our technology stack combines cutting-edge AI/ML tools with robust infrastructure components:

### 🧠 **AI/ML Technologies**
- **Jina AI Embeddings v2**: 512-dimensional sentence embeddings for semantic search
- **OpenAI GPT Models**: GPT-3.5-turbo, GPT-4o, GPT-4o-mini for text generation
- **Ollama**: Local LLM support with Phi3 model
- **LangChain**: Document processing and text splitting
- **Sentence Transformers**: Additional embedding model support

### 🔍 **Vector & Search Technologies**
- **Qdrant**: High-performance vector database with FastEmbed integration
- **MinSearch**: Lightweight keyword search for baseline comparisons
- **BM25**: Sparse vector implementation for keyword matching
- **Reciprocal Rank Fusion (RRF)**: Advanced hybrid search combining dense and sparse methods

### 🗄️ **Database & Storage**
- **PostgreSQL**: Relational database for conversation logs and metadata
- **pgAdmin**: Database administration interface
- **Docker Volumes**: Persistent data storage
- **Qdrant**: Vector database for storing, searching, and managing high-dimensional vector embeddings

### 🌐 **Web Technologies**
- **Streamlit**: Interactive web interface for the AI powered smart travel assistant
- **Docker**: Containerization for all services
- **Docker Compose**: Multi-container orchestration

### 📊 **Visualization & Monitoring**
- **Grafana**: Real-time monitoring dashboards
- **matplotlib & seaborn**: Python library for creating statistical, animated, and interactive data visualizations.

### 🛠️ **Document Processing**
- **Marker**: Advanced PDF-to-Markdown conversion
- **Surya Models**: Document layout detection and OCR
- **RecursiveCharacterTextSplitter**: Intelligent text chunking

### 📋 **Coding Tools**
- **Jupyter Notebooks**: Coding in Python
- **VS Code**: IDE used for development, debugging, running bash/shell terminal and source version control.

## End to End RAG Flow

![*\[DIAGRAM PLACEHOLDER: End-to-End RAG Pipeline Architecture\]*](https://github.com/Adityagurung/Brahman.ai/blob/main/images/end-to-end%20RAG%20flow.png)

### 1. **Data Ingestion** 
```
Wikivoyage PDFs → Marker Conversion → Markdown → LangChain Splitting → JSON Chunks
```
- PDF documents downloaded from Wikivoyage
- Marker converts PDFs to clean Markdown format
- LangChain splits documents into semantic chunks (500 chars, 100 overlap)
- Metadata preserved for traceability

### 2. **Knowledge Base Creation** 
```
Text Chunks → Jina Embeddings → Qdrant Vector DB → BM25 Indexing → Hybrid Collection
```
- Dense embeddings generated using Jina embeddings v2 
- Sparse BM25 vectors created for keyword matching
- Both stored in Qdrant hybrid collections
- Automatic indexing with MD5-based document IDs

### 3. **Query Processing** 
```
User Query → Search Strategy Selection → Multi-Vector Retrieval → RRF Fusion → Top-K Results
```
- **Semantic Search**: Dense vector similarity using cosine distance
- **Keyword Search**: BM25 sparse vector matching
- **Hybrid Search**: Reciprocal Rank Fusion (RRF) combining both approaches

### 4. **Context Assembly** 
```
Retrieved Documents → Prompt Template → Context Injection → LLM-Ready Prompt
```
- Retrieved chunks formatted with location metadata
- Travel-specific prompt template with guidelines
- Context-aware prompt engineering for travel recommendations

### 5. **Response Generation** 
```
Enhanced Prompt → LLM Selection → API Call → Response Processing → Answer Delivery
```
- Multi-model support (OpenAI GPT, Ollama)
- Token usage tracking and cost calculation
- Response time monitoring

### 6. **Quality Assessment** 
```
Generated Answer → Relevance Evaluation → LLM-as-Judge → Quality Scoring → Feedback Loop
```
- Automated relevance classification (RELEVANT/PARTLY_RELEVANT/NON_RELEVANT)
- chatGPT as evaluation judge
- Continuous quality monitoring

### 7. **Monitoring & Analytics** 
```
All Interactions → PostgreSQL Logging → Grafana Visualization → Performance Insights
```
- Real-time conversation logging
- User feedback collection
- Performance metrics and cost tracking

## Reproducibility

Follow these step-by-step instructions to set up Brahman.ai on your system:

### Prerequisites
- Git installed
- Docker Desktop for Windows
- Docker Compose 
- Python 3.10+ 

### 1: Clone the Repository
```
git clone https://github.com/Adityagurung/brahman.ai.git
cd brahman.ai
```

### 2: Environment Configuration
```
# Copy the environment template
copy .env.template .env
rm.env.template

# Edit .env file with your API keys
.env
```

**Required Environment Variables:**
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

In .env file add config values for variables - Postgres, Qdrant, Ollama, Streamlit, Grafana and pgAdmin
```

### 3: Start Docker Services
```
# Ensure Docker Desktop is running
# Start all services in background
docker-compose up -d

# Check services are running
docker-compose ps
```

### 4: Initialize the System
```powershell
# Create a virtual environment (optional)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt 
Note: Not required this step if run by docker-compose build command. 

# Run the setup script to initialize database and index documents
python app/setup.py

#Test Rag system components
python app/test_system.py
```

### 5: Access the Applications

**Travel Assistant App:**
- URL: http://localhost:8501
- Interface: Streamlit web application

**Grafana Monitoring Dashboard:**
- URL: http://localhost:3000
- Pre-configured with travel assistant metrics

**Database Administration:**
- URL: http://localhost:8080
- pgAdmin interface for PostgreSQL

**Qdrant Vector Database:**
- URL: http://localhost:6333/dashboard
- Vector database management interface

### 6: Verify Installation
```
# Check all containers are running
docker-compose logs streamlit

# Test the API endpoints
curl http://localhost:8501/health
```
**Useful Commands:**
```powershell
# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart streamlit

# Clean restart
docker-compose down
docker-compose up -d
```

## Evaluation Criteria

This section demonstrates how Brahman.ai meets all the evaluation requirements:

### Problem Description
The problem is well-described and it's clear what problem the project solves. See [Problem Statement](#problem-statement) section above for detailed analysis of traveler pain points and how our AI assistant addresses them.

### RAG Flow
Both a knowledge base and an LLM are used in the RAG flow:
- **Knowledge Base**: Qdrant vector database with travel document chunks
- **LLMs**: OpenAI GPT models (3.5-turbo, 4o, 4o-mini) and Ollama Phi3
- **Complete Pipeline**: Data ingestion → Vector storage → Retrieval → Generation → Evaluation

### Retrieval Evaluation
Multiple retrieval approaches are evaluated, and the best one is used:

**Evaluation Results:**
*[SCREENSHOT PLACEHOLDER: Evaluation summary table showing performance metrics]*

| Method | Hit Rate @1 | Hit Rate @5 | MRR | Avg Time (ms) |
|--------|-------------|-------------|-----|---------------|
| BM25 Sparse | 0.180 | 0.360 | 0.246 | 23.4 |
| Dense Semantic | 0.190 | 0.460 | 0.291 | 26.4 |
| Multi-stage | 0.180 | 0.360 | 0.246 | 34.8 |
| **RRF Hybrid** | **0.220** | **0.460** | **0.298** | 38.0 |

**Winner: RRF Hybrid Search** - Best overall performance with highest MRR (0.298) and competitive Hit Rate @5 (0.460)

**Evaluation Notebooks:**
- [`notebooks/3_keyword_search_evaluation_minsearch.ipynb`](https://github.com/Adityagurung/Brahman.ai/blob/main/notebooks/3_keyword_search_evaluation_minsearch.ipynb)
- [`notebooks/4_semantic_search_evaluation_qdrant.ipynb`](https://github.com/Adityagurung/Brahman.ai/blob/bf91765c15692164b3bc19f8aa5005838c456255/notebooks/4_semantic_search_evaluation_qdrant.ipynb)
- [`notebooks/5_hybrid_search_evaluation_qdrant.ipynb`](https://github.com/Adityagurung/Brahman.ai/blob/main/notebooks/5_hybrid_search_evaluation_qdrant.ipynb)

### RAG Evaluation
Multiple RAG approaches are evaluated, and the best one is used:

*[SCREENSHOT PLACEHOLDER: RAG evaluation results from offline evaluation notebook]*

**Evaluation Framework:**
- **Ground Truth Dataset**: 735 travel questions across 149 documents
- **LLM-as-Judge**: GPT-4o-mini for relevance evaluation
- **Metrics**: Relevance classification, response time, token usage, costs
- **Models Compared**: GPT-3.5-turbo, GPT-4o, GPT-4o-mini, Ollama Phi3

**Evaluation Notebook:** [`notebooks/offline-rag-evaluation.ipynb`](https://github.com/Adityagurung/Brahman.ai/blob/3b4f19ef13b21bd96088ed297a0e8babdd2b9af0/notebooks/offline-rag-evaluation.ipynb)

### Interface
Streamlit is used as the main interface:

*[SCREENSHOT PLACEHOLDER: Streamlit travel assistant interface]*

**Interface Features:**
- **Chat Interface**: Natural language query input
- **Model Selection**: Choose between OpenAI and Ollama models
- **Search Type Toggle**: Semantic vs Hybrid search options
- **Real-time Feedback**: Thumbs up/down rating system
- **Response Metrics**: Display response time and relevance scores
- **Conversation History**: Track previous interactions

  **File:** [`app/app.py`](https://github.com/Adityagurung/Brahman.ai/blob/799898da2efd95ae3358cefaf3f8cfadb44de93e/app/app.py)

### Ingestion
**Ingestion Pipeline Components:**
1. **PDF Processing**: Marker converts PDFs to Markdown
2. **Text Chunking**: LangChain splitters create semantic chunks
3. **ID Generation**: MD5 hashing for stable document IDs
4. **Vector Creation**: Jina embeddings + BM25 sparse vectors
5. **Database Storage**: Automated indexing in Qdrant

**Automated Execution:**
- **Setup Script**: [`app/setup.py`](https://github.com/Adityagurung/Brahman.ai/blob/237e5a349f01785ab537bd0fcf634c496f36b44e/app/setup.py) runs the complete ingestion pipeline
- **Processing Notebook**: [`notebooks/1_process_pdf2Jsonl.ipynb`](https://github.com/Adityagurung/Brahman.ai/blob/38691d2e41d00408cc939daf3bed3e6216d31e59/notebooks/1_process_pdf2Jsonl.ipynb)
- **Ground Truth Generation**: [`notebooks/2_ground_truth_data.ipynb`](https://github.com/Adityagurung/Brahman.ai/blob/8c99dea46a4b44e7f068a571cee46ca66eed68c2/notebooks/2_ground_truth_data.ipynb)

### Monitoring

User feedback is collected and there's a dashboard with different comprehensive charts:

*[SCREENSHOT PLACEHOLDER: Grafana dashboard showing all monitoring charts]*

**Grafana Dashboard Charts:**
1. **Last 5 Conversations** - Recent interaction table
2. **Feedback Distribution** - Thumbs up/down pie chart
3. **Relevance Metrics** - Answer quality gauge
4. **OpenAI Costs** - API usage cost tracking over time
5. **Token Usage** - Token consumption trends
6. **Model Usage** - Distribution of model selection
7. **Response Time** - Performance monitoring over time

**Monitoring Features:**
- **Real-time Updates**: 30-second refresh rate
- **PostgreSQL Integration**: All data stored in relational database
- **User Feedback**: Thumbs up/down collection system
- **Cost Tracking**: Detailed OpenAI API cost monitoring

  **Files:** [`grafana/dashboard.json`](https://github.com/Adityagurung/Brahman.ai/blob/868d444a3b142098d9498455df30c7358509bf46/grafana/dashboard.json), [`grafana/init.py`](https://github.com/Adityagurung/Brahman.ai/blob/d72073aa39f42b21c2e82fa1427b5115025eb87b/grafana/init.py)

### Containerization

Everything runs in Docker containers for easy deployment:

**Docker Compose Services:**
- **Streamlit**: Main web application
- **Qdrant**: Vector database service
- **PostgreSQL**: Relational database for logs
- **Grafana**: Monitoring dashboard
- **pgAdmin**: Database administration
- **Ollama**: Local LLM service

**Treat:**
- **Turn Key Solution**: `docker-compose up -d`
  **File:** [`docker-compose.yaml`](https://github.com/Adityagurung/Brahman.ai/blob/e24289b5f122cf235311650a7f97df77dd394fdc/docker-compose.yaml)
### Reproducibility

Complete step-by-step instructions provided for Windows 11. See [Reproducibility](#reproducibility) section above for detailed instructions including:
- Prerequisites installation
- Environment configuration
- Docker setup
- Service initialization
- Verification steps
- Troubleshooting guide

### Best Practices
**Status: Complete**

**Hybrid Search (3 points)**: ✅ **Implemented**
- Combines dense semantic vectors (Jina embeddings) with sparse BM25 vectors
- RRF (Reciprocal Rank Fusion) for optimal result combination
- **Notebook**: `notebooks/5_hybrid_search_evaluation.ipynb`

**Document Re-ranking (1 point)**: ✅ **Implemented**
- RRF algorithm re-ranks results from multiple search strategies
- Multi-stage search with dense prefetch followed by sparse re-ranking
- **Implementation**: `rag.py` hybrid search functions

**User Query Rewriting (1 point)**: ✅ **Implemented**
- Travel-specific prompt template optimizes queries for domain context
- Context-aware prompt engineering for better LLM responses
- **Implementation**: `app/app.py` prompt template formatting

### Deployment
**Status: Planned**

Cloud deployment is planned for Hetzner Cloud platform but not currently implemented due to time constraints. The containerized architecture makes cloud deployment straightforward when ready.

**Planned Deployment:**
- **Platform**: Hetzner Cloud (cost-effective European provider)
- **Architecture**: Multi-container deployment with load balancing
- **Database**: Managed PostgreSQL instance
- **Monitoring**: Cloud-native Grafana deployment
- **Domain**: Custom domain with HTTPS

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Brahman.ai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## Acknowledgments

Special thanks to:

- **[Alexey Grigorev](https://github.com/alexeygrigorev)** - For his outstanding contributions to the ML and data engineering community, and for inspiring this project through his educational content and open-source work.

- **[DataTalks.Club](https://datatalks.club/)** - For providing an incredible learning platform and community that fosters knowledge sharing in data science, machine learning, and data engineering. The concepts and best practices learned through DataTalks.Club courses directly influenced this project's architecture and implementation.

- **Wikivoyage Community** - For creating and maintaining high-quality, open-source travel content that powers this assistant.

- **Open Source Contributors** - To the developers of Qdrant, LangChain, Streamlit, and other open-source tools that made this project possible.

---

**Built with ❤️ by Aditya**

*For questions, issues, or contributions, please visit our [GitHub repository](https://github.com/Adityagurung/brahman.ai).*
