# 📚 QwenRoute Backend API Documentation

## 🎯 Overview

The QwenRoute backend provides a comprehensive REST API for IBM AIOps knowledge management and diagnostic support. It combines intelligent pattern matching, semantic search, document processing, and session management for enhanced troubleshooting capabilities.

**Base URL**: `http://localhost:8000`  
**API Documentation**: `http://localhost:8000/docs` (Interactive Swagger UI)  
**Health Check**: `http://localhost:8000/health`

---

## 🚀 **Core API Endpoints**

### 1. **Diagnostic Query Engine** 🔍

#### `POST /query`
**Purpose**: Main diagnostic endpoint that processes user queries and returns intelligent insights

**Request Body**:
```json
{
    "query": "topology-merge service timing out after 30 seconds",
    "session_id": "optional-session-uuid"
}
```

**Response**:
```json
{
    "response": "Based on symptoms analysis, 85% confidence this is a Kafka messaging issue...",
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

**How It Works**:
1. **Pattern Matching**: Identifies keywords and service names
2. **Semantic Search**: Uses embeddings to find conceptually similar cases
3. **Multi-Source Fusion**: Combines results from knowledge base, documents, and patterns
4. **Confidence Scoring**: Provides transparent confidence levels
5. **Session Management**: Maintains conversation context for follow-up queries

---

### 2. **Document Management** 📄

#### `POST /documents/ingest`
**Purpose**: Upload and process documents for knowledge base integration

**Request**: Multipart form data with files
```bash
curl -X POST "http://localhost:8000/documents/ingest" \
     -F "files=@troubleshooting_guide.pdf" \
     -F "files=@kafka_resolution_steps.txt"
```

**Response**:
```json
[
    {
        "filename": "troubleshooting_guide.pdf",
        "status": "success",
        "chunks_processed": 15,
        "error": null
    },
    {
        "filename": "kafka_resolution_steps.txt", 
        "status": "success",
        "chunks_processed": 8,
        "error": null
    }
]
```

**Processing Pipeline**:
1. **File Reading**: Supports text, PDF, and structured formats
2. **Text Extraction**: Extracts content using appropriate parsers
3. **Chunking**: Splits documents into semantic chunks
4. **Embedding Generation**: Creates vector embeddings for semantic search
5. **Metadata Extraction**: Identifies services, symptoms, and categories
6. **Vector Storage**: Stores in Qdrant vector database

#### `GET /documents/search`
**Purpose**: Semantic search across ingested documents

**Parameters**:
- `query` (string): Search query
- `services` (list): Filter by specific services (optional)
- `chunk_types` (list): Filter by chunk types (optional)  
- `limit` (int): Maximum results (default: 5)

**Example**:
```bash
curl "http://localhost:8000/documents/search?query=kafka+timeout&services=kafka&limit=5"
```

**Response**:
```json
{
    "query": "kafka timeout",
    "results": [
        {
            "text": "When Kafka consumers experience timeouts...",
            "score": 0.92,
            "case_id": "case_001",
            "chunk_type": "resolution",
            "services": ["kafka"],
            "metadata": {
                "source_file": "kafka_troubleshooting.pdf",
                "page": 3
            }
        }
    ],
    "count": 1
}
```

---

### 3. **Case Management** 📋

#### `POST /cases/add`
**Purpose**: Add new diagnostic cases to the knowledge base

**Request Body**:
```json
{
    "id": "case_005",
    "title": "ElasticSearch cluster down",
    "description": "Complete cluster failure after node restart",
    "affected_services": ["elasticsearch", "logging"],
    "symptoms": ["cluster red", "node unreachable", "search failed"],
    "resolution_steps": [
        "Check cluster health API",
        "Restart master nodes",
        "Verify network connectivity",
        "Check disk space"
    ],
    "confidence": 0.9
}
```

**Response**:
```json
{
    "status": "success",
    "message": "Case case_005 added successfully"
}
```

#### `GET /cases/list`
**Purpose**: List all cases in the knowledge base

**Response**:
```json
{
    "cases": [
        {
            "id": "case_001",
            "title": "Topology Merge Service Timeout",
            "description": "Service experiencing timeout errors...",
            "affected_services": ["topology-merge", "kafka"],
            "created_at": "2025-09-11T10:30:00"
        }
    ],
    "count": 4,
    "last_updated": "2025-09-11T10:30:00"
}
```

#### `GET /cases/{case_id}`
**Purpose**: Retrieve detailed information for a specific case

**Example**: `GET /cases/case_001`

**Response**:
```json
{
    "case": {
        "id": "case_001",
        "title": "Topology Merge Service Timeout",
        "description": "Service experiencing timeout errors after 30 seconds...",
        "affected_services": ["topology-merge", "kafka"],
        "symptoms": ["timeout", "30 seconds", "slow response", "kafka lag"],
        "resolution_steps": [
            "Check Kafka consumer lag metrics",
            "Monitor partition assignments",
            "Scale consumer instances"
        ],
        "confidence": 0.95,
        "created_at": "2025-09-11T10:30:00"
    },
    "documents": [
        {
            "text": "Kafka consumer lag can cause timeouts...",
            "score": 0.89,
            "chunk_type": "diagnosis"
        }
    ],
    "document_count": 3
}
```

#### `POST /cases/load_samples`
**Purpose**: Load sample cases for testing and demonstration

**Response**:
```json
{
    "status": "success",
    "message": "Loaded 4 sample cases",
    "total_cases": 4
}
```

**Sample Cases Included**:
- Topology Merge Service Timeout (Kafka-related)
- Cassandra Connection Issues
- Redis Cache Performance Issues  
- Observer Resource Consumption

---

### 4. **Session Management** 🔄

#### `GET /session/{session_id}`
**Purpose**: Retrieve session state for debugging and context analysis

**Response**:
```json
{
    "session_id": "uuid-session-id",
    "created_at": "2025-09-11T10:30:00",
    "last_activity": "2025-09-11T10:35:00",
    "query_count": 3,
    "hypotheses": [
        {
            "category": "messaging",
            "confidence": 0.8,
            "refinement_count": 2
        }
    ],
    "context": {
        "recent_queries": ["kafka timeout", "consumer lag", "partition assignment"],
        "focus_services": ["kafka", "topology-merge"]
    }
}
```

#### `DELETE /session/{session_id}`
**Purpose**: Delete a session and its associated data

**Response**:
```json
{
    "status": "success",
    "message": "Session deleted"
}
```

**Session Features**:
- **Stateful Conversations**: Maintains context across multiple queries
- **Hypothesis Refinement**: Builds and refines diagnostic hypotheses over time
- **Learning Context**: Adapts responses based on conversation history

---

### 5. **System Status & Health** 🏥

#### `GET /health`
**Purpose**: Simple health check for monitoring

**Response**:
```json
{
    "status": "healthy",
    "timestamp": "2025-09-11T10:30:00",
    "version": "2.0.0"
}
```

#### `GET /status`
**Purpose**: Comprehensive system status and component health

**Response**:
```json
{
    "api_version": "2.0.0",
    "timestamp": "2025-09-11T10:30:00",
    "features": {
        "pattern_matching": true,
        "semantic_search": true,
        "document_processing": true,
        "session_management": true
    },
    "components": {
        "knowledge_base": {
            "cases": 4,
            "documents": 15,
            "status": "ready"
        },
        "vector_store": {
            "embeddings_available": true,
            "vector_count": 127,
            "status": "connected"
        },
        "embedder": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "status": "loaded"
        }
    },
    "performance": {
        "avg_query_time": "0.234s",
        "cache_hit_rate": "0.67"
    }
}
```

---

### 6. **Advanced Search** 🔍

#### `POST /search/advanced`
**Purpose**: Advanced search combining multiple methods with filtering

**Request Body**:
```json
{
    "query": "database connection timeout",
    "include_pattern_matching": true,
    "include_semantic_search": true,
    "services_filter": ["cassandra", "elasticsearch"],
    "confidence_threshold": 0.7
}
```

**Response**:
```json
{
    "query": "database connection timeout",
    "pattern_matches": [
        {
            "case_id": "case_002",
            "title": "Cassandra Connection Issues",
            "score": 0.89,
            "matched_terms": ["database", "connection", "timeout"]
        }
    ],
    "semantic_matches": [
        {
            "text": "Database connectivity issues often manifest as timeouts...",
            "score": 0.85,
            "case_id": "case_002",
            "chunk_type": "diagnosis"
        }
    ],
    "filters": {
        "services": ["cassandra", "elasticsearch"],
        "confidence_threshold": 0.7
    }
}
```

---

## 🏗️ **Backend Architecture**

### **Core Components**

1. **EnhancedDiagnosticAgent** (`enhanced_agent.py`)
   - Main intelligence engine
   - Multi-source knowledge fusion
   - Hypothesis generation and refinement
   - Session state management

2. **Document Processor** (`document_processor.py`)
   - File parsing and text extraction
   - Intelligent chunking strategies
   - Metadata extraction
   - Content classification

3. **Vector Store** (`vector_store.py`)
   - Qdrant vector database integration
   - Embedding storage and retrieval
   - Similarity search operations
   - Filtering and ranking

4. **Multi-Source Manager** (`multi_source_manager.py`)
   - Combines pattern matching, semantic search, and knowledge graphs
   - Confidence scoring and result fusion
   - Learning from user feedback

### **Knowledge Processing Pipeline**

```
Query Input → Pattern Analysis → Semantic Search → Knowledge Graph
                     ↓                ↓               ↓
            Hypothesis Generation → Result Fusion → Confidence Scoring
                                         ↓
                     Response Generation → Session Update
```

### **Data Sources Integration**

- **Knowledge Base**: Structured cases with symptoms and resolutions
- **Document Corpus**: Unstructured documentation and guides
- **Vector Embeddings**: Semantic similarity search
- **Session Context**: Conversational memory and hypothesis tracking

---

## 🔧 **Configuration & Dependencies**

### **Required Dependencies**
- **FastAPI**: Web framework and API documentation
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for FastAPI

### **Optional Dependencies** (for enhanced features)
- **sentence-transformers**: Semantic embeddings
- **qdrant-client**: Vector database
- **unstructured**: Document parsing
- **tiktoken**: Token counting for LLMs

### **Environment Configuration**
```bash
# Optional Vector Database
QDRANT_URL=http://localhost:6333

# Optional OpenAI Integration
OPENAI_API_KEY=your-key-here

# Embedding Model Selection
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

## 🧪 **Testing & Usage Examples**

### **Basic Diagnostic Query**
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "kafka consumer lag detected in topology-merge service"}'
```

### **Document Upload**
```bash
curl -X POST "http://localhost:8000/documents/ingest" \
     -F "files=@kafka_troubleshooting.pdf"
```

### **Case Management**
```bash
# Add a case
curl -X POST "http://localhost:8000/cases/add" \
     -H "Content-Type: application/json" \
     -d '{
       "id": "case_new",
       "title": "New Issue",
       "description": "Description here",
       "affected_services": ["service1"],
       "symptoms": ["symptom1"],
       "resolution_steps": ["step1"]
     }'

# List all cases
curl "http://localhost:8000/cases/list"

# Get specific case
curl "http://localhost:8000/cases/case_001"
```

### **System Monitoring**
```bash
# Health check
curl "http://localhost:8000/health"

# Detailed status
curl "http://localhost:8000/status"
```

---

## 🚀 **Key Features & Advantages**

### **✅ Intelligent Diagnostics**
- **Multi-source Knowledge Fusion**: Combines pattern matching, semantic search, and structured knowledge
- **Confidence Scoring**: Transparent confidence levels for all recommendations
- **Hypothesis Refinement**: Builds and improves diagnostic hypotheses through conversation

### **✅ Stateful Session Management**
- **Conversation Context**: Maintains context across multiple queries
- **Learning Adaptation**: Adapts responses based on conversation history
- **Session Analytics**: Provides insights into diagnostic sessions

### **✅ Advanced Document Processing**
- **Intelligent Chunking**: Semantically meaningful document segmentation
- **Metadata Extraction**: Automatic identification of services, symptoms, and categories
- **Multi-format Support**: Text, PDF, and structured document processing

### **✅ Production-Ready Design**
- **Error Handling**: Comprehensive error handling and logging
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Monitoring**: Health checks and system status endpoints
- **Scalability**: Designed for horizontal scaling and load balancing

### **✅ Graceful Degradation**
- **Optional Components**: Works without vector database or embeddings
- **Fallback Modes**: Basic pattern matching when advanced features unavailable
- **Progressive Enhancement**: Adds features as dependencies become available

---

## 📋 **API Response Codes**

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid request format or parameters |
| 404 | Not Found | Resource (case, session) not found |
| 500 | Internal Error | Server error during processing |
| 503 | Service Unavailable | Optional component (embeddings) not available |

---

## 🔍 **Interactive API Documentation**

The backend provides interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to:
- 🧪 **Test API endpoints** directly from the browser
- 📖 **View detailed schemas** for requests and responses  
- 📋 **Copy curl commands** for integration
- 🔍 **Explore all available endpoints** with examples

**Perfect for development, testing, and integration!** 🚀
