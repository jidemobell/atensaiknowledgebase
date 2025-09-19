# 🚀 Implementation Directory - Legacy Components

⚠️ **Note**: This directory contains legacy implementation components. 

## 📚 Current Documentation

For the latest **Novel Knowledge Fusion Platform**, please see:

- **[Main Startup Guide](../STARTUP_GUIDE.md)** - Start here for current system
- **[Knowledge Fusion Architecture](../KNOWLEDGE_FUSION_ARCHITECTURE.md)** - Complete architecture overview
- **[AI Agent Architecture](../AI_AGENT_ARCHITECTURE.md)** - Multi-agent system design
- **[API Documentation](../API_DOCUMENTATION_SUMMARY.md)** - Complete API reference
- **[Complete Documentation](../README.md)** - Full documentation index

## 🏗️ Current Architecture

The system has evolved to use:
- **Novel Knowledge Fusion Engine** (Port 8003) - Advanced temporal synthesis
- **Multi-Agent Research System** (Port 8001) - Enhanced collaboration
- **OpenWebUI Interface** (Port 8080) - Production frontend

## � Legacy Components in This Directory

- `backend/` - Legacy backend implementation (basic service on port 8000)
- `frontend/` - **REMOVED** - Old React frontend (no longer needed)

---

*For the latest features and deployment instructions, use the main documentation guides above.*

### 💬 **Session Management**
- **Stateful Conversations**: Maintains context across multiple queries
- **Hypothesis Tracking**: Builds and refines diagnostic hypotheses
- **Conversation History**: Preserves chat history for better context

---

## 🚀 **Quick Start**

### **1. Installation**
```bash
cd qwenroute/implementation
./start.sh
```

### **2. Test the System**
```bash
python test_system.py
```

### **3. Access the API**
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📋 **API Endpoints**

### **Core Diagnostics**
```bash
# Main diagnostic query
POST /query
{
    "query": "topology-merge service timing out",
    "session_id": "optional-session-id"
}

# Get system status
GET /status
```

### **Document Management**
```bash
# Upload documents
POST /documents/ingest
# (Multipart form data with files)

# Semantic search
GET /documents/search?query=kafka+timeout&services=kafka&limit=5
```

### **Case Management**
```bash
# List all cases
GET /cases/list

# Get specific case
GET /cases/{case_id}

# Add new case
POST /cases/add
{
    "id": "case_001",
    "title": "Service timeout issue",
    "description": "...",
    "affected_services": ["kafka"],
    "symptoms": ["timeout"],
    "resolution_steps": ["Check connectivity"]
}

# Load sample cases
POST /cases/load_samples
```

### **Session Management**
```bash
# Get session state
GET /session/{session_id}

# Delete session
DELETE /session/{session_id}
```

---

## 🔧 **Configuration**

### **Required Dependencies**
- **Python 3.8+**
- **FastAPI** (web framework)
- **Pydantic** (data validation)

### **Optional Dependencies**
- **sentence-transformers** (for semantic search)
- **qdrant-client** (for vector database)
- **tiktoken** (for token counting)
- **unstructured** (for document parsing)

### **Optional Services**
- **Qdrant Vector DB**: `docker run -p 6333:6333 qdrant/qdrant`

---

## 🧪 **Testing**

### **Basic Test Suite**
```bash
python test_system.py
```

### **Manual Testing Examples**
```bash
# Test diagnostic query
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "kafka consumer lag detected"}'

# Test document upload
curl -X POST "http://localhost:8000/documents/ingest" \
     -F "files=@case_example.txt"

# Test semantic search
curl "http://localhost:8000/documents/search?query=timeout&services=kafka"
```

---

## 📁 **File Structure**

```
implementation/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── enhanced_agent.py       # Main diagnostic agent
│   ├── document_processor.py   # Document intelligence
│   ├── vector_store.py         # Qdrant vector database
│   └── knowledge_graph.py      # (Legacy - optional)
├── requirements.txt            # Python dependencies
├── start.sh                   # Startup script
├── test_system.py             # Test suite
└── README.md                  # This file
```

---

## 🎯 **Sample Test Queries**

Try these queries to test the system:

### **Service-Specific Issues**
- `"topology-merge service timing out after 30 seconds"`
- `"cassandra database connection failed"`
- `"kafka consumer lag detected"`
- `"high cpu usage in observer services"`

### **General Symptoms**
- `"slow response times"`
- `"connection timeouts"`
- `"memory usage high"`
- `"service unavailable"`

---

## 📊 **Response Format**

```json
{
    "response": "Based on symptoms, 85% confidence this is Kafka messaging issue...",
    "session_id": "uuid-session-id",
    "confidence": 0.85,
    "hypotheses": [
        {
            "category": "messaging",
            "description": "Potential Kafka messaging issue",
            "confidence": 0.8,
            "next_steps": ["Check consumer lag", "Verify connectivity"]
        }
    ],
    "similar_cases": [
        {
            "id": "case_001",
            "title": "Kafka timeout issue",
            "confidence": 0.9
        }
    ],
    "similar_documents": [
        {
            "text": "Resolution: Check Kafka consumer lag...",
            "score": 0.87,
            "case_id": "case_001",
            "chunk_type": "resolution"
        }
    ],
    "data_sources": {
        "pattern_matching": true,
        "semantic_search": true,
        "knowledge_graph": true
    },
    "reasoning_trace": {
        "pattern_confidence": 0.75,
        "semantic_confidence": 0.82,
        "fusion_method": "weighted_combination"
    }
}
```

---

## 🔮 **Next Steps - Phase 2**

1. **🌐 Frontend**: Build React UI for better user experience
2. **🔗 GitHub Integration**: Code-aware diagnostics with repository analysis
3. **📈 Advanced Analytics**: Trend analysis and predictive diagnostics
4. **🤖 Auto-Learning**: System learns from resolution outcomes
5. **🔐 Enterprise Security**: Authentication, audit trails, PII redaction

---

## 💡 **Key Advantages Over Basic RAG**

✅ **Domain-Specific Intelligence**: Understands IBM AIOps services and topology  
✅ **Multi-Source Fusion**: Combines pattern matching + semantic search + graphs  
✅ **Stateful Reasoning**: Maintains conversation context and builds hypotheses  
✅ **Confidence Scoring**: Provides transparent confidence levels for recommendations  
✅ **Graceful Degradation**: Works without optional components (embeddings, vector DB)  
✅ **Production Ready**: Proper error handling, logging, and API design  

---

**Built with ❤️ for IBM AIOps Support Teams**
