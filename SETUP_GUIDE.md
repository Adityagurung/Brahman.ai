# Complete Setup Guide for RAG Travel Assistant

## 🎯 Overview
This guide provides step-by-step instructions to set up your complete RAG Travel Assistant system from scratch, based on your existing document processing pipeline and requirements.

## 📁 Project Structure
```
rag-travel-assistant/
├── app.py                          # Streamlit UI with feedback
├── rag.py                          # RAG logic module
├── database.py                     # PostgreSQL interactions
├── setup.py                        # System initialization
├── test_system.py                  # System testing
├── requirements.txt                # Python dependencies
├── docker-compose.yaml             # Docker orchestration
├── Dockerfile                      # Streamlit container
├── .env.template                   # Environment template
├── .env                           # Your environment (create this)
├── README.md                      # Documentation
├── grafana/                       # Grafana configuration
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── postgres.yaml
│   │   └── dashboards/
│   │       └── dashboard.yaml
│   └── dashboards/
│       └── rag-monitoring.json
└── data/processed/                # Your documents (optional)
    └── documents-with-ids.json    # From your notebooks
```

## 🚀 Step-by-Step Setup

### Step 1: Create Project Directory and Copy Files

```bash
# Create project directory
mkdir rag-travel-assistant
cd rag-travel-assistant

# Create required subdirectories
mkdir -p grafana/provisioning/datasources
mkdir -p grafana/provisioning/dashboards  
mkdir -p grafana/dashboards
mkdir -p data/processed
```

Copy all the files I provided:
- `app.py` (Streamlit application)
- `rag.py` (RAG logic)
- `database.py` (Database operations)
- `setup.py` (System setup)
- `test_system.py` (Testing)
- `requirements.txt` (Dependencies)
- `docker-compose.yaml` (Services)
- `Dockerfile` (Container)
- `README.md` (Documentation)
- `.env.template` (Environment template)
- All Grafana configuration files

### Step 2: Environment Configuration

```bash
# Copy environment template
cp .env.template .env

# Edit environment file
nano .env  # or use your preferred editor
```

Update `.env` with your settings:
```env
# REQUIRED: OpenAI API Key (if using OpenAI models)
OPENAI_API_KEY=sk-your_actual_openai_api_key_here

# Database Configuration
POSTGRES_DB=rag_assistant
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password

# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=admin

# Other settings (defaults should work)
QDRANT_URL=http://localhost:6333
OLLAMA_URL=http://localhost:11434/v1/
STREAMLIT_PORT=8501
GRAFANA_PORT=3000
```

### Step 3: Prepare Your Documents (Optional)

If you have processed documents from your notebooks:

```bash
# Copy your processed documents
cp path/to/your/documents-with-ids.json data/processed/

# Or if you have the semantic chunks from your notebooks:
cp path/to/your/semantic_chunks.json data/processed/documents-with-ids.json
```

**Note**: If you don't have documents ready, the setup script will create sample documents for testing.

### Step 4: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Initialize System

```bash
# Run setup script
python setup.py
```

This script will:
- Initialize PostgreSQL database with proper schema
- Create Qdrant collection for vector storage
- Index your documents (or create sample ones)
- Verify all connections

### Step 6: Start Docker Services

```bash
# Start all services in background
docker-compose up -d

# Check that all services are running
docker-compose ps

# You should see:
# - qdrant (vector database)
# - postgres (relational database)  
# - ollama (local LLM)
# - streamlit (web app)
# - grafana (monitoring)
```

### Step 7: Download Ollama Model (Optional)

```bash
# Download Phi3 model for local inference
docker-compose exec ollama ollama pull phi3

# Or download other models:
# docker-compose exec ollama ollama pull llama2
# docker-compose exec ollama ollama pull codellama
```

### Step 8: Test the System

```bash
# Run comprehensive system test
python test_system.py
```

This will test:
- Database connectivity
- Qdrant vector search
- RAG pipeline
- Complete workflow
- Ollama models (optional)

### Step 9: Access Applications

Once everything is running:

1. **Streamlit App**: http://localhost:8501
   - Your main RAG interface
   - Ask questions and provide feedback
   
2. **Grafana Dashboard**: http://localhost:3000
   - Login: admin / admin
   - View monitoring metrics
   
3. **Qdrant Dashboard**: http://localhost:6333/dashboard
   - Vector database management
   
4. **PostgreSQL**: localhost:5432
   - Direct database access if needed

## 🔧 Configuration Options

### Model Selection

In the Streamlit app, you can choose from:
- **OpenAI Models**: gpt-3.5-turbo, gpt-4o, gpt-4o-mini (require API key)
- **Ollama Models**: phi3 (or any model you install locally)

### Search Types

- **Semantic**: Dense vector search using Jina embeddings (better for meaning)
- **Hybrid**: Combines dense + sparse BM25 vectors (balanced performance)

### Document Processing

If you want to add your own documents:

1. **Use your existing pipeline** (from notebooks):
   ```python
   # Process PDFs with Marker
   # Chunk with LangChain
   # Save as documents-with-ids.json
   # Run setup.py to re-index
   ```

2. **Add individual documents**:
   ```python
   # Add to your documents array in setup.py
   # Or directly index in Qdrant
   ```

## 📊 Monitoring Setup

### Grafana Dashboard Panels

The included dashboard provides:
1. **Conversations Over Time**: Usage trends
2. **Model Usage Statistics**: Performance comparison  
3. **User Feedback Distribution**: Satisfaction metrics
4. **Response Time Tracking**: Performance monitoring
5. **Relevance Distribution**: Quality metrics
6. **Token Usage**: Cost tracking
7. **OpenAI Costs**: Budget monitoring
8. **Search Type Usage**: Feature adoption

### Custom Monitoring

Add custom panels using these SQL queries:

```sql
-- High-cost conversations
SELECT question, model_used, openai_cost, timestamp
FROM conversations 
WHERE openai_cost > 0.01 
ORDER BY timestamp DESC;

-- User satisfaction by model
SELECT 
    c.model_used,
    COUNT(f.feedback) as total_feedback,
    AVG(CASE WHEN f.feedback > 0 THEN 1.0 ELSE 0.0 END) as satisfaction_rate
FROM conversations c
LEFT JOIN feedback f ON c.id = f.conversation_id
GROUP BY c.model_used;
```

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**:
   ```bash
   # Check what's using ports
   lsof -i :8501  # Streamlit
   lsof -i :6333  # Qdrant
   lsof -i :5432  # PostgreSQL
   lsof -i :3000  # Grafana
   ```

2. **Docker services not starting**:
   ```bash
   # Check logs
   docker-compose logs service_name
   
   # Restart specific service
   docker-compose restart service_name
   ```

3. **Database connection errors**:
   ```bash
   # Verify PostgreSQL is running
   docker-compose ps postgres
   
   # Check database credentials in .env
   ```

4. **Qdrant indexing fails**:
   ```bash
   # Check Qdrant service
   curl http://localhost:6333/health
   
   # Re-run setup
   python setup.py
   ```

5. **OpenAI API errors**:
   ```bash
   # Verify API key in .env
   echo $OPENAI_API_KEY
   
   # Test API key
   curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
   ```

### Health Checks

```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs streamlit
docker-compose logs qdrant
docker-compose logs postgres

# Test system components
python test_system.py
```

## 🎉 Success Checklist

✅ All Docker services running (`docker-compose ps`)  
✅ Streamlit app accessible at http://localhost:8501  
✅ Grafana dashboard at http://localhost:3000  
✅ System tests passing (`python test_system.py`)  
✅ Sample query returns response  
✅ Feedback buttons working  
✅ Monitoring data visible in Grafana  

## 🔄 Next Steps

1. **Customize the UI**: Modify `app.py` for your specific needs
2. **Add more documents**: Use your document processing pipeline
3. **Tune search**: Adjust parameters in `rag.py`
4. **Add features**: Extend functionality as needed
5. **Monitor performance**: Use Grafana dashboards
6. **Scale up**: Deploy to production environment

## 💡 Tips for Success

1. **Start with sample data**: Let the setup script create sample documents first
2. **Test incrementally**: Use `test_system.py` after each step
3. **Monitor resources**: Ensure adequate RAM for all services
4. **Check logs regularly**: Use `docker-compose logs` to debug issues
5. **Backup your data**: PostgreSQL data persists in Docker volumes

Your RAG Travel Assistant is now ready to serve travel queries with full monitoring and feedback capabilities! 🌍✈️