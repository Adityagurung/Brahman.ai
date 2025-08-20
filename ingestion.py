
import json
import os
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams
from tqdm import tqdm

def load_documents_to_qdrant():
    """Load your processed documents into Qdrant for vector search"""
    
    print("🚀 Starting document loading process...")
    
    # Initialize Qdrant client
    client = QdrantClient("http://localhost:6333")
    print("✅ Connected to Qdrant")
    
    # Load your processed documents from notebook 2
    documents_path = 'data/processed/documents-with-ids.json'
    
    # Check if file exists
    if not os.path.exists(documents_path):
        print(f"❌ Documents file not found: {documents_path}")
        print("Make sure you have run notebook 2 (ground truth data generation)")
        return False
    
    with open(documents_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    print(f"📄 Loaded {len(documents)} documents from {documents_path}")
    
    # Show sample document structure
    print("\n📋 Sample document structure:")
    if documents:
        sample_doc = documents[0]
        for key, value in sample_doc.items():
            print(f"  {key}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
    
    # Collection configuration
    collection_name = "travel_docs"
    
    # Delete existing collection if it exists
    try:
        client.delete_collection(collection_name)
        print(f"🗑️ Deleted existing collection: {collection_name}")
    except:
        print(f"ℹ️ Collection {collection_name} doesn't exist, creating new one")
    
    # Create collection with FastEmbed support
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=512,  # jinaai/jina-embeddings-v2-small-en dimension
            distance=models.Distance.COSINE
        )
    )
    print(f"✅ Created collection: {collection_name}")
    
    # Prepare points for upload using FastEmbed
    points = []
    print("\n🔄 Preparing documents for upload...")
    
    for idx, doc in enumerate(tqdm(documents, desc="Processing documents")):
        point = models.PointStruct(
            id=idx,
            vector=models.Document(
                text=doc['content'],
                model="jinaai/jina-embeddings-v2-small-en"  # FastEmbed will auto-generate embeddings
            ),
            payload={
                "content": doc['content'],
                "location": doc.get('location', ''),
                "doc_id": doc.get('doc_id', ''),
                "id": doc.get('id', ''),  # Your generated ID from notebook
            }
        )
        points.append(point)
    
    # Upload documents in batches
    batch_size = 50
    print(f"\n⬆️ Uploading {len(points)} documents in batches of {batch_size}...")
    
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        client.upsert(collection_name=collection_name, points=batch)
        print(f"  Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
    
    # Verify upload
    collection_info = client.get_collection(collection_name)
    print(f"\n✅ Upload complete! Collection now has {collection_info.points_count} documents")
    
    return True

def test_vector_search():
    """Test the vector search functionality"""
    print("\n🔍 Testing vector search...")
    
    client = QdrantClient("http://localhost:6333")
    collection_name = "travel_docs"
    
    # Test queries
    test_queries = [
        "What are the best temples to visit in Karnataka?",
        "Which beaches are good in Andhra Pradesh?",
        "What is Hampi famous for?",
        "Tell me about Mysore palace",
        "What are the UNESCO heritage sites?"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Query: '{query}'")
        
        try:
            results = client.query_points(
                collection_name=collection_name,
                query=models.Document(
                    text=query,
                    model="jinaai/jina-embeddings-v2-small-en"
                ),
                limit=3,
                with_payload=True
            )
            
            if results.points:
                print(f"  Found {len(results.points)} results:")
                for i, result in enumerate(results.points, 1):
                    print(f"    {i}. Score: {result.score:.4f}")
                    print(f"       Location: {result.payload.get('location', 'N/A')}")
                    print(f"       Content: {result.payload['content'][:150]}...")
                    print()
            else:
                print("  No results found")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    # Load documents
    success = load_documents_to_qdrant()
    
    if success:
        # Test search
        test_vector_search()
        print("\n🎉 Document loading and testing completed successfully!")
    else:
        print("\n❌ Document loading failed!")