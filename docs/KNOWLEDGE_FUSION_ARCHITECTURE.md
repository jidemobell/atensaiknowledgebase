# IBM Knowledge Fusion Platform Architecture

## Overview

The IBM Knowledge Fusion Platform is a cutting-edge conversational AI system that goes beyond traditional RAG (Retrieval-Augmented Generation) approaches. It implements intelligent multi-source knowledge synthesis through a **pipe-based integration architecture** with OpenWebUI, providing seamless access to advanced knowledge capabilities without requiring modifications to existing OpenWebUI installations.

## System Architecture

### 🏗️ **Multi-Tier Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interface Layer                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              OpenWebUI (Port 8080)                         ││
│  │            • Chat Interface                                 ││
│  │            • Admin Panel                                    ││
│  │            • Function Management                            ││
│  │            • User Authentication                            ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────┬───────────────────────────────────────┘
                         │ Pipe Function Integration
┌─────────────────────────▼───────────────────────────────────────┐
│                  Knowledge Fusion Layer                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │        Knowledge Fusion Gateway (Port 9000)                ││
│  │        • Intelligent Routing                               ││
│  │        • Load Balancing                                    ││
│  │        • Fallback Management                               ││
│  │        • Request/Response Processing                       ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────┬───────────────────────────────────────┘
                         │ Smart Routing
┌─────────────────────────▼───────────────────────────────────────┐
│                   Processing Backends                          │
│                                                                 │
│  ┌─────────────────────┐        ┌─────────────────────────┐    │
│  │  Knowledge Fusion   │        │      CoreBackend        │    │
│  │  Backend (8002)     │◄──────►│      (Port 8001)        │    │
│  │                     │        │                         │    │
│  │ • Knowledge Synth   │        │ • Deep Analysis         │    │
│  │ • Vector Search     │        │ • Case Management       │    │
│  │ • Source Fusion     │        │ • Diagnostic Tools      │    │
│  │ • Context Awareness │        │ • Document Processing   │    │
│  └─────────────────────┘        └─────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────────┘
                         │ Data Access
┌─────────────────────────▼───────────────────────────────────────┐
│                    Knowledge Base Layer                        │
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────────┐│
│  │ ChromaDB    │ │ Case Data   │ │ Git Repos   │ │ Documents    ││
│  │ (Vectors)   │ │ (Files)     │ │ (Code)      │ │ (Knowledge)  ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 🔗 **Pipe-Based Integration Model**

Unlike traditional approaches that require OpenWebUI modification, our architecture uses a **Pipe Function** for seamless integration:
```
User Query → OpenWebUI Interface → Pipe Function → Gateway → Backends → Response
```

#### **1. Pipe Function (`knowledge_fusion_function.py`)**
- **Type**: OpenWebUI Pipe class
- **Purpose**: Routes queries from OpenWebUI to Knowledge Fusion Gateway
- **Features**:
  - Real-time status updates ("🔍 Routing to Knowledge Fusion...")
  - Error handling with user-friendly messages
  - Configurable gateway URL and timeouts
  - Full conversation context passing

#### **2. Knowledge Fusion Gateway (`knowledge_fusion_gateway.py`)**
- **Port**: 9000
- **Purpose**: Intelligent routing and load balancing
- **Capabilities**:
  - Smart backend selection based on query type
  - Graceful fallback when backends are unavailable
  - Request/response transformation
  - Health monitoring and circuit breaking

#### **3. Processing Backends**
- **Knowledge Fusion Backend** (8002): Advanced knowledge synthesis
- **CoreBackend** (8001): Deep analysis and case management
- **Intelligent Fallback**: Simulated responses when backends unavailable

## 🧠 **Intelligent Routing Logic**

### Query Classification and Routing

```python
class QueryRouter:
    def route_query(self, query: str) -> str:
        if self.is_synthesis_query(query):
            return "knowledge_fusion_backend"  # Port 8002
        elif self.is_analysis_query(query):
            return "core_backend"             # Port 8001
        else:
            return "fallback_handler"         # Intelligent simulation
```

### Backend Specialization

#### **Knowledge Fusion Backend (Port 8002)**
- **Specialization**: Knowledge synthesis and fusion
- **Use Cases**:
  - "How do microservices communicate?"
  - "What are best practices for debugging distributed systems?"
  - "Explain circuit breaker patterns with examples"
- **Capabilities**:
  - Multi-source knowledge fusion
  - Vector similarity search
  - Context-aware responses
  - Source attribution

#### **CoreBackend (Port 8001)**
- **Specialization**: Deep technical analysis
- **Use Cases**:
  - "Analyze this error log for root cause"
  - "Diagnose memory leak patterns"
  - "Compare this case with historical issues"
- **Capabilities**:
  - Case-based reasoning
  - Diagnostic workflows
  - Pattern recognition
  - Hypothesis generation

## 🔄 **Knowledge Fusion Flow**

### Complete Request Lifecycle

```
1. User Input → OpenWebUI Chat Interface
   ↓
2. Pipe Function → Captures query + conversation context
   ↓  
3. Gateway (9000) → Analyzes query type + selects backend
   ↓
4a. Knowledge Fusion Backend (8002) → Synthesis queries
4b. CoreBackend (8001) → Analysis queries  
4c. Fallback Handler → When backends unavailable
   ↓
5. Response Processing → Source attribution + formatting
   ↓
6. User Response → Enhanced answer in OpenWebUI
```

### Advanced Features

#### **Multi-Source Knowledge Synthesis**
```python
sources = {
    "cases": query_case_database(query),
    "docs": search_documentation(query), 
    "code": analyze_repositories(query),
    "conversations": find_similar_chats(query)
}
synthesized_response = fuse_knowledge_sources(sources)
```

#### **Graceful Degradation**
```python
async def handle_backend_failure():
    try:
        return await primary_backend.query(request)
    except ConnectionError:
        try:
            return await secondary_backend.query(request)
        except ConnectionError:
            return intelligent_fallback_response(request)
```

## 🏗️ **Component Deep Dive**

### **1. OpenWebUI Pipe Function**

**Location**: `knowledge_fusion_function.py`
**Class**: `Pipe` (not Function - critical for OpenWebUI recognition)

```python
class Pipe:
    def __init__(self):
        self.type = "pipe"
        self.id = "ibm_knowledge_fusion"
        self.name = "IBM Knowledge Fusion"
        
    async def pipe(self, body, __user__, __request__, __event_emitter__):
        # Routes to Knowledge Fusion Gateway
        # Provides real-time UI feedback
        # Handles errors gracefully
```

### **2. Knowledge Fusion Gateway**

**Location**: `knowledge_fusion_gateway.py`
**Purpose**: Central routing and orchestration

```python
@app.post("/knowledge-fusion/query")
async def query_handler(request: QueryRequest):
    # 1. Analyze query characteristics
    backend = determine_optimal_backend(request.query)
    
    # 2. Route to appropriate backend
    response = await route_to_backend(backend, request)
    
    # 3. Handle fallbacks if needed
    if not response:
        response = await intelligent_fallback(request)
        
    return response
```

### **3. Knowledge Fusion Backend**

**Location**: `knowledge-fusion-template/start_server.py`
**Specialization**: Knowledge synthesis and multi-source fusion

```python
class KnowledgeFusionServer:
    async def synthesize_knowledge(self, query: str):
        # Multi-source information gathering
        # Vector similarity search
        # Context-aware response generation
        # Source attribution and confidence scoring
```

### **4. CoreBackend** 

**Location**: `corebackend/implementation/backend/main.py`
**Specialization**: Deep analysis and case management

```python
class CoreBackendAPI:
    async def analyze_case(self, query: str):
        # Pattern recognition across historical cases
        # Diagnostic hypothesis generation  
        # Root cause analysis
        # Confidence assessment
```

## 🎯 **What Makes This Architecture Different**

### Traditional RAG Limitations
```
Query → Document Search → Generate Response
```
- Single knowledge source
- No intelligent routing
- Brittle failure modes
- Limited context awareness

### Knowledge Fusion Advantages
```
Query → Intelligent Analysis → Multi-Backend Synthesis → Enhanced Response
```
- **Multi-Source Intelligence**: Cases + Docs + Code + Conversations
- **Adaptive Routing**: Query-specific backend selection
- **Graceful Degradation**: Intelligent fallbacks maintain service
- **Decoupled Integration**: No OpenWebUI modification required
- **Enterprise Scalability**: Designed for corporate environments

## 🚀 **Deployment Architecture**

### Development Mode (Server Mode)
```bash
./bin/start_server_mode.sh
```
- Direct Python execution
- Easy debugging and development
- Corporate network friendly
- Fast iteration cycles

### Production Mode (Container Mode)  
```bash
./start_docker_mode.sh
```
- Containerized services
- Scalable deployment
- Production hardening
- Environment isolation

### Service Dependencies
```
Prerequisites: OpenWebUI running (any port)
├── CoreBackend (8001) ← Case analysis and diagnostics
├── Knowledge Fusion Backend (8002) ← Knowledge synthesis  
├── Knowledge Fusion Gateway (9000) ← Intelligent routing
└── OpenWebUI Integration ← Pipe function upload
```
- **Session Continuity**: Maintains diagnostic context across multiple queries

#### 2. **Structured Case Management System**

**Case Data Model:**
```json
{
  "id": "case_001",
  "title": "Topology Merge Service Timeout", 
  "description": "Service experiencing timeout errors after 30 seconds",
  "affected_services": ["topology-merge", "kafka"],
  "symptoms": ["timeout", "30 seconds", "slow response", "kafka lag"],
  "resolution_steps": [
    "Check Kafka consumer lag metrics",
    "Monitor partition assignments",
    "Scale consumer instances"
  ],
  "confidence": 0.95,
  "metadata": {
    "created_at": "2025-09-08T10:30:00Z",
    "severity": "high",
    "category": "performance"
  }
}
```

**Operations:**
- **CRUD Operations**: Full lifecycle management of technical cases
- **Bulk Data Loading**: Import cases from external systems (Salesforce, JIRA)
- **Relationship Mapping**: Links cases to affected services and symptoms
- **Historical Tracking**: Maintains resolution effectiveness over time

#### 3. **Advanced Document Processing Pipeline**

**Document Ingestion Workflow:**
```
Upload Document → Text Extraction → Chunking → Metadata Extraction → Embedding Generation → Vector Storage
```

**Processing Capabilities:**
- **Multi-format Support**: PDFs, text files, Salesforce cases, structured data
- **Intelligent Chunking**: Breaks documents into semantically meaningful segments
- **Metadata Extraction**: Automatically identifies services, symptoms, and solutions
- **Vector Embeddings**: Creates semantic representations for similarity search
- **Quality Assessment**: Validates document processing and embedding quality

#### 4. **Semantic Search & Vector Operations**

**Search Endpoints:**
- **`/documents/search`**: Semantic similarity search across knowledge base
- **`/search/advanced`**: Combined pattern matching and semantic search
- **`/cases/{case_id}`**: Retrieval with associated document context

**Search Features:**
- **Multi-modal Matching**: Combines keyword and semantic similarity
- **Service Filtering**: Scope searches to specific technical domains
- **Confidence Thresholding**: Filter results by reliability scores
- **Context Preservation**: Maintains search context for iterative refinement

#### 5. **System Monitoring & Analytics**

**Health Monitoring:**
```json
{
  "status": "healthy",
  "components": {
    "embeddings_available": true,
    "processor_available": true, 
    "vector_store_healthy": true,
    "knowledge_base_loaded": true
  },
  "performance": {
    "avg_query_time": "250ms",
    "success_rate": 0.97,
    "total_cases": 1247,
    "total_documents": 3891
  }
}
```

**Analytics Capabilities:**
- **Performance Metrics**: Query response times, success rates, resource usage
- **Knowledge Growth**: Tracks knowledge base expansion and quality
- **Usage Patterns**: Identifies common query types and resolution paths
- **System Health**: Monitors all components for optimal performance

### How It Powers the Conversational System

## Original Backend API Endpoints & Functions

### Core Diagnostic APIs

| Endpoint | Method | Purpose | Used By |
|----------|--------|---------|---------|
| **`/query`** | POST | Main diagnostic endpoint - processes technical queries with AI analysis | React Dashboard, Enhanced Backend |
| **`/search/advanced`** | POST | Advanced search combining pattern matching and semantic similarity | Power users, automated systems |
| **`/documents/search`** | GET | Semantic search across document knowledge base | Enhanced Backend, search features |

### Case Management APIs

| Endpoint | Method | Purpose | Used By |
|----------|--------|---------|---------|
| **`/cases/add`** | POST | Add new cases to knowledge base with structured metadata | Admin interfaces, data import |
| **`/cases/list`** | GET | List all cases with filtering and pagination | Dashboard, reporting |
| **`/cases/{case_id}`** | GET | Retrieve specific case with associated documents | Case details, link resolution |
| **`/cases/load_samples`** | POST | Load sample data for testing and demonstration | Development, demos |

### Document Processing APIs

| Endpoint | Method | Purpose | Used By |
|----------|--------|---------|---------|
| **`/documents/ingest`** | POST | Upload and process documents (PDFs, text files) | Content management, data import |
| **`/documents/search`** | GET | Search processed documents with semantic similarity | Enhanced Backend, research |

### Session & System Management

| Endpoint | Method | Purpose | Used By |
|----------|--------|---------|---------|
| **`/session/{session_id}`** | GET | Retrieve diagnostic session state for debugging | Development, troubleshooting |
| **`/session/{session_id}`** | DELETE | Clean up diagnostic sessions | Session management |
| **`/status`** | GET | Comprehensive system health and component status | Monitoring, Enhanced Backend |
| **`/health`** | GET | Simple health check for load balancers | Infrastructure monitoring |

### Detailed Function Breakdown

#### **`/query` - The Heart of the System**

**Input:**
```json
{
  "query": "topology-merge service is timing out after 30 seconds",
  "session_id": "optional-session-id"
}
```

**Processing:**
1. **Intent Analysis**: Determines query type (troubleshooting, information, configuration)
2. **Pattern Matching**: Searches cases using keyword matching and similarity algorithms
3. **Semantic Search**: Uses vector embeddings to find conceptually similar issues
4. **Hypothesis Generation**: AI creates diagnostic theories based on symptoms
5. **Confidence Scoring**: Assigns reliability metrics to each result
6. **Response Synthesis**: Combines all sources into structured diagnostic response

**Output:**
```json
{
  "response": "Based on similar cases, this appears to be a Kafka consumer lag issue...",
  "session_id": "abc-123",
  "hypotheses": [
    {
      "theory": "Kafka consumer group rebalancing causing delays",
      "confidence": 0.85,
      "supporting_evidence": ["case_001", "doc_234"]
    }
  ],
  "similar_cases": [
    {
      "id": "case_001",
      "title": "Topology Merge Service Timeout", 
      "confidence": 0.95,
      "relevance_score": 0.89
    }
  ],
  "similar_documents": [
    {
      "filename": "kafka_troubleshooting_guide.pdf",
      "chunk": "Consumer lag monitoring and resolution steps...",
      "confidence": 0.82
    }
  ],
  "confidence": 0.89,
  "analysis": "Pattern analysis suggests this is a known issue with resolution precedent",
  "data_sources": {
    "cases_searched": true,
    "documents_searched": true,
    "embeddings_used": true
  },
  "reasoning_trace": {
    "steps": ["keyword_extraction", "pattern_matching", "semantic_search", "confidence_calculation"],
    "timing": {"total_ms": 245, "embedding_ms": 89, "search_ms": 156}
  }
}
```

#### Data Flow from Original Backend to Enhanced Backend:

```
User: "Kafka service timing out"
    ↓
Enhanced Backend (8001) → API Call → Original Backend (8000)
    ↓
Original Backend Processing:
├── EnhancedDiagnosticAgent.diagnose_issue()
├── Pattern matching against case database
├── Semantic search across documents  
├── Confidence scoring and ranking
└── Structured response generation
    ↓
Enhanced Backend Receives:
{
  "similar_cases": [case_001, case_004],
  "similar_documents": [doc_234, doc_567],
  "hypotheses": ["kafka consumer lag", "network timeout"],
  "confidence": 0.89,
  "analysis": "Pattern suggests consumer group rebalancing issue"
}
    ↓
Enhanced Backend Synthesis:
├── Combines with conversation context
├── Formats for natural language response
├── Adds source attribution
└── Returns conversational response
    ↓
User sees: "Based on similar cases, this appears to be a Kafka consumer 
           lag issue. Historical resolution suggests checking partition 
           assignments and scaling consumer instances..."
```

### Why This Architecture Is Powerful

1. **Separation of Intelligence vs Interface**: 
   - Original backend = sophisticated AI processing
   - Enhanced backend = natural conversation management

2. **Reusable Knowledge Engine**:
   - Same diagnostic intelligence serves both interfaces
   - No duplication of complex AI logic
   - Consistent analysis across all user touchpoints

3. **Independent Evolution**:
   - Can enhance conversational capabilities without touching core AI
   - Can improve diagnostic engine without affecting chat interface
   - Different scaling strategies for different workloads

4. **Comprehensive Coverage**:
   - Power users get full diagnostic capabilities through React dashboard
   - End users get streamlined experience through chat interface
   - System administrators get monitoring and management tools

The original backend is essentially the "brain" that provides the intelligence, while the enhanced backend is the "voice" that makes that intelligence conversational and accessible.

### Complementary Roles

1. **Original Backend (8000)** - Structured Analysis & Case Management:
   
   **Core Diagnostic Engine:**
   - **EnhancedDiagnosticAgent**: Advanced AI agent that processes technical queries with pattern matching and semantic analysis
   - **Multi-layered Analysis**: Combines keyword matching, semantic similarity, and confidence scoring
   - **Session Management**: Maintains diagnostic session state for complex troubleshooting workflows
   
   **Knowledge Base Operations:**
   - **Case CRUD Operations**: Create, read, update, delete cases with structured metadata
   - **Document Ingestion**: Upload and process technical documents (PDFs, text files, Salesforce cases)
   - **Vector Storage**: Semantic embeddings for advanced similarity search
   - **Advanced Search**: Combines pattern matching and semantic search with filtering capabilities
   
   **Data Processing Pipeline:**
   - **Document Chunking**: Breaks down large documents into searchable segments
   - **Metadata Extraction**: Extracts services, symptoms, resolution steps from unstructured text
   - **Confidence Scoring**: Assigns reliability scores to matches and recommendations
   - **Pattern Recognition**: Identifies similar issues based on technical fingerprints
   
   **Administrative Functions:**
   - **System Health Monitoring**: Real-time status of all components (vector store, embeddings, processors)
   - **Performance Analytics**: Query response times, success rates, knowledge base growth
   - **Data Management**: Bulk operations for cases, document management, sample data loading
   - **API Debugging**: Session inspection, error tracking, system diagnostics
   
   **Integration Capabilities:**
   - **Salesforce Integration**: Direct case import and processing from Salesforce systems
   - **GitHub Code Analysis**: Repository scanning for code-related issues
   - **External API Support**: Extensible framework for additional data sources

2. **Enhanced Backend (8001)** - Conversational Intelligence:
   - Natural language interactions
   - Context-aware responses
   - Multi-source knowledge synthesis
   - Real-time chat support
   - Intelligent routing

### Data Flow

```
User Question: "topology-merge service is timing out"

1. OpenWebUI Chat Interface
   ↓
2. ibm_knowledge_fusion.py (Custom Function)
   ↓
3. Enhanced Backend (Port 8001)
   ├── KnowledgeRouter: Analyzes intent
   ├── SourceFusion: Queries multiple sources
   │   ├── knowledge_base.json
   │   ├── cases/ directory
   │   ├── GitHub repositories
   │   └── Documentation
   ├── ConversationManager: Maintains context
   └── Response Synthesis
   ↓
4. Formatted Response with Sources
   ↓
5. OpenWebUI Chat Display
```

### Example Response Flow

```json
{
  "response": "Documentation suggests: Configure timeout settings in config.yaml\nFrom code analysis: def merge_topology(timeout=30)...\nHistorical cases show: Case #123 resolved by increasing timeout to 60s",
  "sources_used": ["documentation", "github_code", "cases"],
  "confidence": 0.85,
  "conversation_context": "troubleshooting_timeout"
}
```

## Benefits of This Architecture

### 1. **Separation of Concerns**
- **Case Management**: Formal workflows and structured data (Original Backend)
- **Conversational AI**: Natural interactions and knowledge synthesis (Enhanced Backend)

### 2. **Flexible Usage Patterns**
- **Power Users**: Access original backend for detailed analysis
- **End Users**: Use OpenWebUI for quick conversational support
- **Hybrid Workflows**: Combine both interfaces as needed

### 3. **Scalability**
- **Independent Scaling**: Each backend can scale based on usage patterns
- **Service Isolation**: Issues in one backend don't affect the other
- **Technology Flexibility**: Different optimization strategies per service

### 4. **Knowledge Amplification**
- **Context Preservation**: Enhanced backend maintains conversation history
- **Source Integration**: Combines structured and unstructured knowledge
- **Intelligence Layer**: Adds conversational AI capabilities to existing knowledge base

## Deployment Strategy

### Shared Resources
- **Virtual Environment**: `projectvenv/` used by both backends
- **Knowledge Base**: `knowledge_base.json` accessed by both systems
- **Case Data**: `cases/` directory shared between systems

### Port Allocation
- **Port 8000**: Original backend (case management)
- **Port 8001**: Enhanced backend (conversational AI)
- **Port 3000**: React frontend (original dashboard)
- **Port 8080**: OpenWebUI interface

## Future Evolution

This dual-backend architecture provides a migration path:

1. **Current State**: Both backends operating independently
2. **Integration Phase**: Cross-backend communication and data sharing
3. **Unified Platform**: Potential consolidation with preserved capabilities
4. **AI Enhancement**: Advanced ML models and knowledge graph integration

## Conclusion

The IBM Knowledge Fusion Platform represents an evolution from traditional case management to intelligent conversational AI. By maintaining both the original structured backend and adding an enhanced conversational layer, the system provides flexibility, scalability, and comprehensive knowledge access through multiple interaction paradigms.

The placement within OpenWebUI enables seamless chat-based interactions while preserving the analytical capabilities of the original system, creating a comprehensive knowledge platform that serves both technical experts and end users effectively.
