# test_system.py - Test RAG System Components
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test PostgreSQL database connection"""
    print("🧪 Testing Database Connection...")
    try:
        from db import get_db_connection
        
        conn = get_db_connection()
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_qdrant_connection():
    """Test Qdrant vector database connection"""
    print("🧪 Testing Qdrant Connection...")
    try:
        from qdrant_client import QdrantClient
        
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        client = QdrantClient(qdrant_url)
        
        # Test connection by getting collections
        collections = client.get_collections()
        print(f"✅ Qdrant connection successful. Collections: {[c.name for c in collections.collections]}")
        return True
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        return False

def test_rag_pipeline():
    """Test the complete RAG pipeline"""
    print("🧪 Testing RAG Pipeline...")
    try:
        from rag import get_answer
        
        # Test query
        test_query = "What are some famous places to visit?"
        
        print(f"Sending test query: '{test_query}'")
        start_time = time.time()
        
        result = get_answer(
            query=test_query,
            model_choice="openai/gpt-3.5-turbo",  # Change if you prefer Ollama
            search_type="semantic"
        )
        
        end_time = time.time()
        
        print(f"✅ RAG pipeline successful!")
        print(f"   Response time: {end_time - start_time:.2f}s")
        print(f"   Answer length: {len(result['answer'])} characters")
        print(f"   Relevance: {result['relevance']}")
        print(f"   Search results: {result['search_results_count']}")
        
        return True
    except Exception as e:
        print(f"❌ RAG pipeline failed: {e}")
        return False

def test_full_workflow():
    """Test the complete workflow including database storage"""
    print("🧪 Testing Full Workflow...")
    try:
        import uuid
        from rag import get_answer
        from db import save_conversation, save_feedback
        
        # Generate test conversation
        conversation_id = str(uuid.uuid4())
        test_query = "Tell me about Karnataka's tourist attractions"
        
        # Get RAG response
        answer_data = get_answer(
            query=test_query,
            model_choice="openai/gpt-3.5-turbo",
            search_type="semantic"
        )
        
        # Save conversation
        save_conversation(conversation_id, test_query, answer_data)
        
        # Save positive feedback
        save_feedback(conversation_id, 1)
        
        print("✅ Full workflow successful!")
        print(f"   Conversation ID: {conversation_id}")
        print("   Conversation and feedback saved to database")
        
        return True
    except Exception as e:
        print(f"❌ Full workflow failed: {e}")
        return False

def test_ollama_model():
    """Test Ollama local model (optional)"""
    print("🧪 Testing Ollama Model (optional)...")
    try:
        from openai import OpenAI
        
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/v1/")
        ollama_client = OpenAI(base_url=ollama_url, api_key="ollama")
        
        response = ollama_client.chat.completions.create(
            model="phi3:mini",
            messages=[{"role": "user", "content": "Hello, this is a test."}]
        )
        
        print("✅ Ollama model test successful!")
        print(f"   Model response: {response.choices[0].message.content[:100]}...")
        
        return True
    except Exception as e:
        print(f"⚠️  Ollama model test failed: {e}")
        print("   (This is optional - you can still use OpenAI models)")
        return False

def main():
    """Run all tests"""
    print("🚀 RAG Travel Assistant System Test")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Qdrant Connection", test_qdrant_connection),
        ("RAG Pipeline", test_rag_pipeline),
        ("Full Workflow", test_full_workflow),
        ("Ollama Model (Optional)", test_ollama_model)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed >= 4:  # Allow Ollama to fail
        print("\n🎉 System is ready! You can now:")
        print("   1. Run: streamlit run app.py")
        print("   2. Access the app at: http://localhost:8501")
        print("   3. View Grafana at: http://localhost:3000")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        print("   Make sure Docker services are running: docker-compose up -d")

if __name__ == "__main__":
    main()