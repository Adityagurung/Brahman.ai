# setup.py - Initialize Database and Index Documents
import os
import json
import uuid
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv()

from db import init_db
from qdrant_client import QdrantClient, models

def setup_qdrant():
    """Setup Qdrant collection for documents"""
    print("🔧 Setting up Qdrant vector database...")
    
    # Initialize Qdrant client
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    client = QdrantClient(qdrant_url)
    
    collection_name = "travel-docs"  
    
    try:
        # Delete existing collection if it exists
        client.delete_collection(collection_name=collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except:
        pass
    
    # Create new collection with hybrid vector configuration
    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            # Dense vector configuration for semantic search
            "jina-small": models.VectorParams(
                size=512,  # Jina embeddings v2 small dimension
                distance=models.Distance.COSINE,
            ),
        },
        sparse_vectors_config={
            # Sparse vector configuration for keyword search  
            "bm25": models.SparseVectorParams(
                modifier=models.Modifier.IDF,
            )
        }
    )
    
    print(f"✅ Created Qdrant collection: {collection_name}")
    return client, collection_name

def load_documents():
    """Load processed documents from your pipeline"""
    print("📄 Loading documents...")
    
    # Check if documents-with-ids.json exists (from your notebooks)
    doc_paths = [
        "data/processed/documents-with-ids.json",
        "../data/processed/documents-with-ids.json",
        "documents-with-ids.json"
    ]
    
    documents = None
    for doc_path in doc_paths:
        if os.path.exists(doc_path):
            print(f"Loading documents from: {doc_path}")
            with open(doc_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            break
    
    if documents is None:
        print("⚠️  No processed documents found. Please run your document processing pipeline first.")
        print("Expected file: data/processed/documents-with-ids.json")
        return []
    
    print(f"✅ Loaded {len(documents)} documents")
    return documents

def index_documents(client, collection_name, documents):
    """Index documents in Qdrant"""
    print("🔍 Indexing documents in Qdrant...")
    
    if not documents:
        print("❌ No documents to index")
        return
    
    points = []
    for doc in tqdm(documents, desc="Preparing documents"):
        # Generate UUID from document ID for Qdrant
        doc_id = doc.get('id', doc.get('doc_id', str(uuid.uuid4())))
        hash_object = hashlib.md5(doc_id.encode())
        uuid_string = str(uuid.UUID(hash_object.hexdigest()))
        
        point = models.PointStruct(
            id=uuid_string,
            vector={
                # Dense vector using Jina model
                "jina-small": models.Document(
                    text=doc['content'],
                    model="jinaai/jina-embeddings-v2-small-en",
                ),
                # Sparse vector using BM25
                "bm25": models.Document(
                    text=doc['content'], 
                    model="Qdrant/bm25",
                ),
            },
            payload={
                "content": doc['content'],
                "location": doc.get('location', ''),
                "doc_id": doc.get('doc_id', ''),
                "id": doc_id
            }
        )
        points.append(point)
    
    # Upload in batches
    batch_size = 50
    for i in tqdm(range(0, len(points), batch_size), desc="Uploading batches"):
        batch = points[i:i+batch_size]
        client.upsert(collection_name=collection_name, points=batch)
    
    print(f"✅ Indexed {len(points)} documents successfully")

def generate_sample_data():
    """Generate sample travel documents for testing"""
    print("🧪 Generating sample travel documents...")
    
    sample_docs = [
        {
            "id": "sample_001",
            "content": "Karnataka is a state in Southern India known for its rich cultural heritage. Bangalore, the capital, is called the Silicon Valley of India. Other notable cities include Mysore, famous for its palaces, and Hampi, a UNESCO World Heritage Site with ancient ruins.",
            "location": "Karnataka",
            "doc_id": "sample_001"
        },
        {
            "id": "sample_002", 
            "content": "Andhra Pradesh is located on the southeastern coast of India. Visakhapatnam is a major port city, while Tirupati is famous for the Venkateswara Temple. The state is known for its spicy cuisine and classical dance forms.",
            "location": "Andhra_Pradesh",
            "doc_id": "sample_002"
        },
        {
            "id": "sample_003",
            "content": "Tamil Nadu offers diverse attractions from ancient temples in Madurai to hill stations like Ooty. Chennai is the capital and a major cultural center. The state is renowned for its Dravidian architecture and classical music tradition.",
            "location": "Tamil_Nadu", 
            "doc_id": "sample_003"
        },
        {
            "id": "sample_004",
            "content": "Kerala is known as God's Own Country, famous for its backwaters, hill stations like Munnar, and beautiful beaches in Kovalam. The state is renowned for Ayurvedic treatments and spice plantations in Thekkady.",
            "location": "Kerala",
            "doc_id": "sample_004"
        },
        {
            "id": "sample_005",
            "content": "Rajasthan is the land of kings with majestic forts and palaces. Jaipur is the Pink City, Udaipur is the City of Lakes, and Jaisalmer is famous for its golden sandstone architecture in the Thar Desert.",
            "location": "Rajasthan",
            "doc_id": "sample_005"
        }
    ]
    
    print(f"✅ Generated {len(sample_docs)} sample documents")
    return sample_docs

def main():
    """Main setup function"""
    print("🚀 Starting RAG Travel Assistant Setup...")
    print("=" * 50)
    
    # 1. Initialize database
    print("\n1️⃣ Initializing PostgreSQL database...")
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return
    
    # 2. Setup Qdrant
    print("\n2️⃣ Setting up Qdrant vector database...")
    try:
        client, collection_name = setup_qdrant()
    except Exception as e:
        print(f"❌ Qdrant setup failed: {e}")
        return
    
    # 3. Load and index documents
    print("\n3️⃣ Loading and indexing documents...")
    try:
        documents = load_documents()
        
        # If no documents found, use sample data
        if not documents:
            print("📝 Using sample documents for demonstration...")
            documents = generate_sample_data()
        
        index_documents(client, collection_name, documents)
        
    except Exception as e:
        print(f"❌ Document indexing failed: {e}")
        return
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Copy .env.template to .env and update with your API keys")
    print("2. Run: docker-compose up -d")
    print("3. Access the application at http://localhost:8501")
    print("4. Access Grafana at http://localhost:3000 (admin/admin)")
    print("\n🎉 Your RAG Travel Assistant is ready!")

if __name__ == "__main__":
    main()