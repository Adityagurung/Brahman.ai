# Let's analyze the key components from the attached files to understand the structure
import json

# Key components I need to adapt:
project_components = {
    "Current RAG Pipeline (from notebooks)": [
        "PDF processing with Marker",
        "Document chunking and embedding", 
        "Qdrant vector database with Jina embeddings",
        "Keyword, semantic, and hybrid search",
        "Ground truth evaluation"
    ],
    "Existing Infrastructure (from attached files)": [
        "Streamlit UI framework",
        "PostgreSQL database with feedback tracking",
        "Docker setup with Grafana",
        "OpenAI integration for LLM responses"
    ],
    "Required Modifications": [
        "Replace Elasticsearch with Qdrant vector search",
        "Add thumbs up/down feedback buttons",
        "Extract RAG logic to rag.py module", 
        "Adapt database schema for RAG conversations",
        "Setup Grafana monitoring dashboards"
    ]
}

for category, items in project_components.items():
    print(f"\n{category}:")
    for item in items:
        print(f"  • {item}")


# Create directory structure for Grafana configuration
import os

grafana_dirs = [
    "grafana",
    "grafana/provisioning",
    "grafana/provisioning/datasources", 
    "grafana/provisioning/dashboards",
    "grafana/dashboards"
]

for directory in grafana_dirs:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")

print("\n✅ Grafana directory structure created")