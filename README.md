# IBM Knowledge Fusion Platform

**Beyond Basic RAG** - A next-generation knowledge integration platform that provides intelligent routing, multi-source synthesis, advanced AI capabilities, and **enterprise-scale support case processing** through seamless integration with OpenWebUI.

## 🚀 **NEW: Enterprise Support Case Processing**

Transform thousands of diverse IBM support cases into actionable knowledge with:
- **Intelligent Case Clustering** - Groups similar issues automatically
- **Adaptive Pattern Recognition** - Handles varying case contexts and formats
- **Historical Case Context** - Enhances responses with proven solutions
- **Enterprise-Scale Processing** - Parallel processing for massive case collections
- **Seamless Integration** - No workflow changes required for existing users

## 📋 Complete Setup Guide

### Step 1: Installation & Environment Setup

```bash
# 1. Clone the repository
git clone git@github.com:jidemobell/atensaiknowledgebase.git
cd atensaiknowledgebase

# 2. Setup virtual environments (auto-creates if missing)
./bin/setup_environments.sh

# 3. Start all Knowledge Fusion services
./bin/start_server_mode.sh
```

### Step 2: OpenWebUI Integration

```bash
# 5. Install OpenWebUI (in separate terminal/environment)
pip install open-webui
open-webui serve --port 8080

# 6. Open browser: http://localhost:8080
# 7. Go to Admin Panel → Functions → Upload knowledge_fusion_function.py
```

### Step 3: Setup ASM Repositories (Enterprise-Friendly)

```bash
# 8. Initialize ASM repository structure for local analysis
./bin/manage_asm_repos.sh --init

# 9. Clone your ASM repositories (use SSH for enterprise environments):
git clone git@github.com:your-org/asm-core-services.git data/asm_repositories/core_services/
# Core services includes topology, merge, status, inventory services
git clone git@github.com:your-org/asm-observers.git data/asm_repositories/observers/  
git clone git@github.com:your-org/asm-ui-components.git data/asm_repositories/ui/
git clone git@github.com:your-org/asm-documentation.git data/asm_repositories/documentation/
# Add more ASM repos as needed...

# 10. Extract knowledge from your ASM repositories
./bin/asm_knowledge_extractor.py --repos-dir data/asm_repositories --output-dir data/knowledge_extracted

# 11. Setup automatic repository updates (optional)
./bin/manage_asm_repos.sh --setup-cron
```

### Step 4: Add Your Content

```bash
# Create case study structure
mkdir -p data/case_studies/case_001/{documents,images,logs}
mkdir -p data/case_studies/case_002/{documents,images,logs}

# Add your existing case files:
# - Text documents in documents/
# - Screenshots in images/  
# - Log files in logs/
# - Any other relevant files
```

## 🔄 Query Flow: From Question to Answer

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐    ┌─────────────────┐
│   User Query    │───▶│ Knowledge Fusion │───▶│ Core Backend   │───▶│  Knowledge      │
│   (OpenWebUI)   │    │   Function       │    │   Analysis     │    │  Sources        │
│                 │    │                  │    │                │    │                 │
│ "How to fix     │    │ • Route query    │    │ • ASM patterns │    │ • ASM repos     │
│  topology       │    │ • Context prep   │    │ • Case studies │    │ • Case files    │
│  sync issues?"  │    │ • Multi-source   │    │ • Best practices│    │ • Documentation │
└─────────────────┘    └──────────────────┘    └────────────────┘    └─────────────────┘
         ▲                        │                        │                        │
         │                        ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐    ┌─────────────────┐
│   Enhanced      │◀───│  Response        │◀───│   Knowledge    │◀───│   Search &      │
│   Answer        │    │  Synthesis       │    │   Matching     │    │   Analysis      │
│                 │    │                  │    │                │    │                 │
│ • Step-by-step  │    │ • Combine info   │    │ • Similar cases│    │ • Pattern match │
│ • Code examples │    │ • Add context    │    │ • Code patterns│    │ • Relevance     │
│ • ASM-specific  │    │ • Best practices │    │ • Solutions    │    │ • Ranking       │
└─────────────────┘    └──────────────────┘    └────────────────┘    └─────────────────┘
```

## �️ System Architecture & Component Roles

### **OpenWebUI → Knowledge Fusion Function → Gateway → CoreBackend**

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐    ┌─────────────────┐
│   OpenWebUI     │───▶│ Knowledge Fusion │───▶│ API Gateway    │───▶│  CoreBackend    │
│                 │    │   Function       │    │                │    │                │
│ • User interface│    │ • Query routing  │    │ • Intelligence │    │ • Diagnostics   │
│ • Chat UI       │    │ • Request format │    │ • Case matching│    │ • Pattern match │
│ • File upload   │    │ • Error handling │    │ • Enhancement  │    │ • Vector search │
│ • Response      │    │ • Status updates │    │ • Load balance │    │ • Knowledge KB  │
└─────────────────┘    └──────────────────┘    └────────────────┘    └─────────────────┘
```

### **Component Responsibilities:**

#### **🔗 Knowledge Fusion Function (`knowledge_fusion_function.py`)**
- **Role:** OpenWebUI integration point
- **What it does:**
  - Receives user queries from OpenWebUI chat interface
  - Routes requests to the API Gateway
  - Handles connection errors and timeouts
  - Provides real-time status updates to users
  - Formats responses for OpenWebUI display

#### **🚪 API Gateway (`knowledge_fusion_gateway.py`)**
- **Role:** Intelligent routing and enhancement layer
- **What it does:**
  - **NEW:** Loads processed support cases for similarity matching
  - **NEW:** Finds similar historical cases for each query
  - **NEW:** Enhances requests with proven resolution patterns
  - Routes enhanced requests to CoreBackend
  - **NEW:** Adds clustering insights to responses
  - Provides fallback handling between services

#### **🧠 CoreBackend (`corebackend/implementation/backend/`)**
- **Role:** Advanced diagnostic and analysis engine
- **What it does:**
  - **Diagnostic Analysis:** Pattern matching, hypothesis generation
  - **Semantic Search:** Vector-based similarity search across documents
  - **Knowledge Base Management:** Stores and retrieves cases, documents
  - **Document Processing:** Ingests and processes support case files
  - **Session Management:** Maintains conversation context
  - **Multi-turn Conversations:** Refines diagnoses over multiple queries

#### **📊 Enterprise Case Processor (`enterprise_case_processor.py`)**
- **Role:** Batch processing system for thousands of support cases
- **What it does:**
  - **Parallel Processing:** ThreadPoolExecutor for enterprise scale
  - **Adaptive Parsing:** Handles diverse JSON/TXT/CSV case formats
  - **Quality Assessment:** Confidence scoring and validation
  - **Error Handling:** Robust fallback mechanisms
  - **Progress Tracking:** Real-time processing statistics

#### **🔍 Case Clustering System (`simple_case_clustering.py`)**
- **Role:** Intelligent case grouping and similarity analysis
- **What it does:**
  - **Case Clustering:** Groups similar support cases automatically
  - **Pattern Recognition:** Identifies common service combinations
  - **Resolution Analysis:** Ranks effectiveness of solution patterns
  - **Similarity Matching:** Finds historical cases related to new queries
  - **Insight Generation:** Provides actionable recommendations

### **🔄 Enhanced Query Flow with New Intelligence:**

```
User Query → Function → Gateway (+ Smart Matching) → CoreBackend (+ Case Context) → Enhanced Response
     ↑                              ↓                           ↓                           ↓
📱 OpenWebUI              🧠 Historical Cases        🔍 Diagnostic Engine       ✨ Context-Rich Answer
```

## �🎯 What Happens Behind the Scenes

### When You Ask a Question:

1. **OpenWebUI** receives your query
2. **Knowledge Fusion Function** processes the request:
   - Identifies query type (ASM topology, observer config, etc.)
   - Determines which knowledge sources to search
3. **Core Backend** performs analysis:
   - Searches ASM repository patterns
   - Matches against case studies
   - Finds relevant documentation
4. **Knowledge Sources** provide data:
   - Local ASM repositories (code patterns, configs)
   - Case study files (similar problems, solutions)
   - Documentation (best practices, guides)
5. **Response Synthesis** creates answer:
   - Combines multiple knowledge sources
   - Provides ASM-specific context
   - Includes code examples and step-by-step solutions

## 🏗️ Service Architecture

```
Port 8080: OpenWebUI (Your Interface)
    ↓
Port 9000: Knowledge Fusion Gateway (Request Router)
    ↓
Port 8002: Knowledge Fusion Backend (AI Processing)
    ↓
Port 8001: Core Backend (Knowledge Search & Analysis)
    ↓
Local Data: ASM Repos + Case Studies + Documentation
```

## 🗂️ Knowledge Sources Structure

```
data/
├── asm_repositories/          # Your cloned ASM repos
│   ├── core/                 # ASM core services
│   ├── observers/            # Observer implementations  
│   ├── ui/                   # UI components
│   └── services/             # Backend services
├── case_studies/             # Your case files
│   ├── case_001/
│   │   ├── documents/        # Text files, PDFs
│   │   ├── images/          # Screenshots, diagrams
│   │   └── logs/            # Log files, traces
│   └── case_002/
└── documentation/            # Additional docs
```

## 📊 **NEW: Support Case Processing Workflow**

### **Step 1: Prepare Your Support Cases**

```bash
# Create support cases directory
mkdir -p data/support_cases

# Add your IBM support case files (JSON, TXT, or CSV format)
# Examples:
cp /path/to/your/cases/*.json data/support_cases/
cp /path/to/your/cases/*.txt data/support_cases/
```

### **Step 2: Process Cases at Enterprise Scale**

```bash
# Process thousands of cases with parallel processing
python enterprise_case_processor.py

# Or process specific directory
python enterprise_case_processor.py --input-dir data/support_cases --output enterprise_knowledge_base.json

# Monitor processing with real-time progress
python enterprise_case_processor.py --batch-size 50 --workers 8 --progress
```

### **Step 3: Analyze Case Patterns (Optional)**

```bash
# Run clustering analysis to understand case patterns
python simple_case_clustering.py

# View clustering results
cat simple_case_clustering_analysis.json
```

### **What You Get:**

#### **🔍 Intelligent Query Enhancement**
When you ask: *"How to fix topology sync issues?"*

**Before:** Generic troubleshooting steps

**After:** 
```
How to fix topology sync issues...

📊 Context from Similar Cases:
Found 3 similar historical cases:
• Case TS019888217: topology merge failing in OpenShift...
• Case TS020145893: composite topology sync timeout...

🎯 Common Resolution Patterns:
• Apply hotfix image digest update  
• Restart topology service pods
• Update RBAC permissions

🔧 Related Services: nasm-topology, ui-content, hdm-analytics
```

#### **📈 Processing Statistics**
- **Thousands of cases** processed in parallel
- **Adaptive parsing** handles diverse formats automatically
- **Quality scoring** identifies cases needing better documentation
- **Pattern recognition** finds common service combinations
- **Resolution effectiveness** ranking based on historical success

### **Supported Case Formats:**

- **IBM Support Case JSON** - Direct export from IBM support systems
- **Salesforce Case Export** - Standard Salesforce case format  
- **Text Files** - Plain text case descriptions
- **CSV Files** - Structured case data in spreadsheet format
- **Mixed Formats** - Automatic format detection and processing

## ✅ Startup Checklist

### Services Running?
```bash
curl http://localhost:8001/health  # ✅ Core Backend
curl http://localhost:8002/health  # ✅ Knowledge Fusion  
curl http://localhost:9000/health  # ✅ Gateway
curl http://localhost:8080/health  # ✅ OpenWebUI
```

### Knowledge Sources Ready?
- [ ] ASM repositories cloned in `data/asm_repositories/`
- [ ] Case studies organized in `data/case_studies/`
- [ ] **NEW:** Support cases added to `data/support_cases/`
- [ ] Documentation added to `data/documentation/`
- [ ] Knowledge Fusion function uploaded to OpenWebUI
- [ ] **NEW:** Enterprise case processing completed (`enterprise_knowledge_base.json` exists)

### Test Your Setup
In OpenWebUI, try these questions:
- "What ASM services handle topology data?"
- "How does Kafka message flow work in ASM?"
- "Show me observer configuration patterns"
- **NEW:** "How to fix topology sync issues?" *(tests support case integration)*
- **NEW:** "What are common resolution patterns for performance issues?"*

**Expected Response**: Detailed answers with ASM-specific context, code examples, references to your actual repositories, **and historical case context with proven solutions**.

## � **NEW: Project Structure with Enhanced Components**

```
📦 IBM Knowledge Fusion Platform
├── 🔧 Core Components
│   ├── knowledge_fusion_function.py          # OpenWebUI integration
│   ├── knowledge_fusion_gateway.py          # Enhanced with case matching  
│   └── corebackend/implementation/backend/   # Diagnostic engine
│
├── 🆕 Enterprise Case Processing  
│   ├── enterprise_case_processor.py         # Batch processing system
│   ├── case_clustering_system.py            # Advanced clustering (ML)
│   ├── simple_case_clustering.py            # Basic clustering (built-in)
│   ├── process_support_cases.py             # Case processing workflows
│   └── test_case_extraction.py             # Testing & validation
│
├── 📊 Enhanced Knowledge Extraction
│   ├── asm_knowledge_domains.yml           # Enhanced with case patterns
│   ├── corebackend/.../knowledge_extractor.py  # Adaptive processing (+400 lines)
│   └── corebackend/.../multi_source_manager.py # Case integration methods
│
├── 🗃️ Data Structure  
│   ├── data/
│   │   ├── asm_repositories/               # Your ASM codebases
│   │   ├── case_studies/                   # Traditional case files  
│   │   ├── support_cases/                  # 🆕 IBM support cases (JSON/TXT)
│   │   └── documentation/                  # Additional docs
│   │
│   ├── 🆕 Generated Knowledge Bases
│   │   ├── enterprise_knowledge_base.json   # Processed support cases
│   │   ├── simple_case_clustering_analysis.json  # Clustering insights
│   │   └── knowledge_base.json              # Core diagnostic KB
│
├── 🛠️ Management Scripts
│   ├── bin/
│   │   ├── start_server_mode.sh            # Start all services
│   │   ├── setup_environments.sh           # Environment setup
│   │   ├── manage_asm_repos.sh             # ASM repository management
│   │   └── asm_knowledge_extractor.py      # Enhanced knowledge extraction
│
├── 📋 Configuration & Requirements
│   ├── requirements.txt                    # Core dependencies
│   ├── requirements_clustering.txt         # 🆕 ML clustering dependencies
│   ├── asm_knowledge_domains.yml          # Enhanced pattern definitions
│   └── scheduler_config.json              # Automated processing
│
└── 📚 Documentation
    ├── README.md                          # This comprehensive guide
    ├── docs/COMPLETE_DOCUMENTATION.md     # Full technical details
    ├── docs/STARTUP_GUIDE.md             # Quick start guide
    └── docs/CORE_BACKEND_TROUBLESHOOTING.md  # Troubleshooting
```

### **🆕 New Files Added:**

#### **Enterprise Processing:**
- `enterprise_case_processor.py` - **523 lines** of enterprise-scale batch processing
- `case_clustering_system.py` - **661 lines** of advanced ML-based clustering  
- `simple_case_clustering.py` - **533 lines** of clustering with built-in libraries
- `requirements_clustering.txt` - Additional ML dependencies

#### **Enhanced Core Systems:**
- `knowledge_extractor.py` - **+400 lines** of adaptive case processing capabilities
- `knowledge_fusion_gateway.py` - **+120 lines** of intelligent case matching
- `asm_knowledge_domains.yml` - **+50 lines** of support case patterns

#### **Testing & Validation:**
- `test_case_extraction.py` - Comprehensive testing framework
- `data/support_cases/case_TS019888217.json` - Sample IBM support case

### **🎯 Capability Matrix:**

| Component | Traditional | Enhanced | New Capabilities |
|-----------|-------------|----------|-----------------|
| **Knowledge Fusion** | Basic routing | ✅ Smart matching | Historical case context |
| **Case Processing** | Manual | ✅ Enterprise batch | Thousands of cases, parallel processing |
| **Pattern Recognition** | Static patterns | ✅ Adaptive patterns | 30+ services, 20+ error patterns |
| **Clustering** | None | ✅ ML clustering | Automatic case grouping, similarity analysis |
| **Response Quality** | Generic | ✅ Context-rich | Proven resolution patterns, related cases |

## �🚨 Common Issues & Solutions

**"Services won't start"**
```bash
./bin/cleanup_platform.sh --soft  # Stop everything
./bin/start_server_mode.sh         # Fresh start
```

**"OpenWebUI can't connect"**  
- Check function is uploaded in Admin → Functions
- Verify Gateway is running on port 9000
- Check logs: `./bin/view_logs.sh --service gateway`

**"No ASM knowledge in responses"**
- Ensure ASM repos are cloned in correct structure
- Run initial analysis: `./bin/manage_asm_repos.sh --analyze`
- Check Core Backend has access to data directory

> 📚 **Detailed troubleshooting**: [`docs/COMPLETE_DOCUMENTATION.md`](docs/COMPLETE_DOCUMENTATION.md)

## 🧠 Theory: How Knowledge Fusion Works

### Traditional RAG vs Knowledge Fusion

**❌ Traditional RAG Problems:**
- Single knowledge source (one database)  
- Simple similarity matching only
- No context between different types of information
- Generic responses without domain expertise

**✅ Knowledge Fusion Solution:**
- **Multi-Source Intelligence**: ASM repos + case studies + documentation
- **Domain-Aware Processing**: Understands ASM architecture patterns
- **Context Synthesis**: Combines code patterns with case solutions
- **Intelligent Routing**: Routes queries to appropriate knowledge sources

### Why This Matters for ASM

Your ASM questions need answers that combine:
- **Code Patterns** (from repositories): How things are implemented
- **Case Studies** (from your experience): What problems occurred and solutions
- **Architecture Knowledge** (from docs): How components interact

Traditional AI can't connect these - Knowledge Fusion can.

## 🏗️ Architecture: The Complete Picture

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐
│   OpenWebUI     │───▶│ Knowledge Fusion │───▶│ Core Backend   │
│  (Your Chat)    │    │   Gateway        │    │ (ASM Analysis) │
│   Port 8080     │    │   Port 9000      │    │   Port 8001    │
└─────────────────┘    └──────────────────┘    └────────────────┘
                                │                        │
                                │                        ▼
                                ▼                ┌─────────────────┐
                         ┌──────────────┐       │ Knowledge Base  │
                         │ Knowledge    │       │                 │
                         │  Fusion      │       │ • ASM Repos     │
                         │ Backend      │       │ • Case Studies  │
                         │ Port 8002    │       │ • Documentation │
                         └──────────────┘       └─────────────────┘
```

**Each Service's Role:**
- **OpenWebUI**: Your familiar chat interface
- **Gateway (9000)**: Routes requests and manages responses  
- **Knowledge Fusion (8002)**: AI processing with domain awareness
- **Core Backend (8001)**: Searches and analyzes your ASM knowledge
- **Knowledge Base**: Your local ASM repos, cases, and docs

## 📊 Visual Flow Diagram

```
🧑 User: "Why is ASM topology sync failing?"
│
├─ 🔍 Query Analysis
│  ├─ Identifies: ASM topology issue
│  ├─ Domain: Infrastructure/Services  
│  └─ Type: Troubleshooting
│
├─ 🎯 Knowledge Source Selection
│  ├─ ASM Core Repositories (topology service patterns)
│  ├─ Case Studies (similar sync failures)
│  └─ Documentation (sync troubleshooting guides)
│
├─ 🔎 Parallel Search & Analysis
│  ├─ Code Pattern Search: "topology sync" in repos
│  ├─ Case Study Match: Previous sync issues
│  └─ Best Practice Lookup: Sync troubleshooting
│
├─ 🧠 Intelligence Synthesis
│  ├─ Combines code patterns with case solutions
│  ├─ Adds ASM-specific context
│  └─ Provides step-by-step resolution
│
└─ 📝 Enhanced Response
   ├─ Root cause analysis (Kafka topic issues?)
   ├─ Specific ASM service logs to check
   ├─ Code examples from your repos
   ├─ Similar cases and their solutions  
   └─ Step-by-step resolution guide
```

## 💡 Key Insight: The Python Extractor Role

**You asked why run the Python extractor?** Here's the clarity:

- **Knowledge Fusion Function** = Real-time query processing (always running)
- **Python ASM Extractor** = One-time setup to analyze your repos and build knowledge index

Think of it like:
- **Building a library** (Python extractor) vs **Using the library** (Knowledge Fusion)
- You only run the extractor when you add new repos or want to update the knowledge base
- The Knowledge Fusion system uses the pre-analyzed knowledge for fast responses
- **Dynamic synthesis**: Combines information from different sources contextually
- **Intelligent routing**: Automatically selects best knowledge sources
- **Advanced reasoning**: Uses embedding similarity + semantic understanding

## Core Services

### 1. Knowledge Fusion Gateway (Port 9000)
**The Smart Router**: Receives requests from OpenWebUI and intelligently routes them through the knowledge pipeline.

### 2. Core Backend Engine (Port 8001)  
**The Knowledge Processor**: Handles semantic search, embedding management, and core knowledge operations.

### 3. Knowledge Fusion Backend (Port 8002)
**The Intelligence Layer**: Provides advanced knowledge synthesis and multi-source reasoning.

### 4. Ollama Integration (Port 11434)
**The AI Engine**: Provides local LLM capabilities with models like Llama2, CodeLlama, and custom models.

## Integration Methods

### Method 1: Function Upload (Recommended)
1. Start Knowledge Fusion services: `./bin/start_server_mode.sh`
2. Install OpenWebUI separately: `pip install open-webui && open-webui serve`  
3. Upload `knowledge_fusion_function.py` to Admin Panel → Functions
4. Enable the function and start chatting!

### Method 2: API Integration
Direct API calls to `http://localhost:9000` for custom integrations.

## Service Management

```bash
# Start all Knowledge Fusion services
./bin/start_server_mode.sh

# Monitor logs
tail -f logs/knowledge_fusion.log

# Check service health
curl http://localhost:9000/health
curl http://localhost:8001/health
curl http://localhost:8002/docs
```

## Scripts & Tools

All platform scripts are organized in the `bin/` directory:

- **🚀 [start_server_mode.sh](bin/start_server_mode.sh)** - Main platform launcher
- **📚 [add_knowledge_source.sh](bin/add_knowledge_source.sh)** - GitHub repository management
- **🔄 [manage_hybrid_sources.sh](bin/manage_hybrid_sources.sh)** - Multi-source knowledge management
- **📊 [view_logs.sh](bin/view_logs.sh)** - Advanced monitoring system
- **⏰ [automated_scheduler.sh](bin/automated_scheduler.sh)** - Update scheduling
- **🎭 [demo_platform.sh](bin/demo_platform.sh)** - Platform demonstration
- **🧹 [cleanup_platform.sh](bin/cleanup_platform.sh)** - Platform cleanup

📋 **Complete script documentation**: See [bin/README.md](bin/README.md)

## Documentation

### Getting Started
- **� [Startup Guide](docs/STARTUP_GUIDE.md)** - Quick 5-minute getting started  
- **�📖 [Integration Flow](docs/INTEGRATION_FLOW.md)** - Step-by-step setup and integration guide

### Architecture & Design
- **🏗️ [Knowledge Fusion Architecture](docs/KNOWLEDGE_FUSION_ARCHITECTURE.md)** - Core platform architecture
- **🤖 [AI Agent Architecture](docs/AI_AGENT_ARCHITECTURE.md)** - Multi-agent system design
- **📋 [API Documentation](docs/API_DOCUMENTATION_SUMMARY.md)** - Complete API reference

### Platform Status
- **✅ [Platform Completion Summary](docs/PLATFORM_COMPLETION_SUMMARY.md)** - Current capabilities overview
- **🧹 [Platform Cleanup Summary](docs/PLATFORM_CLEANUP_SUMMARY.md)** - Optimization and cleanup details

### Advanced Documentation
- **📚 [Core Backend Architecture](docs/corebackend/ADVANCED_ARCHITECTURE.md)** - Backend system details
- **⚙️ [Implementation Guide](docs/implementation/COREBACKEND_README.md)** - Technical implementation details
- **📋 [Planning Documents](docs/planning/)** - Project roadmaps and technical plans
- **📖 [Reference Materials](docs/reference/)** - Data models, query examples, and technical reference

## Key Features

### Intelligent Query Routing
```python
# Automatically routes queries to appropriate knowledge sources
query = "How do I implement authentication in our React app?"
# → Routes to: Engineering docs + Code examples + Security policies
```

### Multi-Source Synthesis  
```python
# Combines information from multiple knowledge bases
query = "What's our company policy on remote work and related tools?"
# → Synthesizes: HR policies + IT guidelines + Manager resources
```

### Dynamic Context Management
```python
# Maintains conversation context across knowledge sources
follow_up = "What about international employees?"
# → Builds on previous response with relevant international policies
```

## API Examples

### Basic Knowledge Query
```bash
curl -X POST http://localhost:9000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning best practices", "max_results": 5}'
```

### Advanced Multi-Source Query
```bash
curl -X POST http://localhost:9000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"query": "project management tools", "sources": ["docs", "wikis", "code"]}'
```

## Troubleshooting

### Common Issues

**Services won't start**:
```bash
# Check logs
./bin/view_logs.sh

# Verify ports
lsof -i :8001,8002,9000,8080

# Restart services  
./bin/start_server_mode.sh
```

**OpenWebUI connection issues**:
```bash
# Test Knowledge Fusion Gateway  
curl http://localhost:9000/health

# Check OpenWebUI status
curl http://localhost:8080/health
```

**Function upload problems**:
- Ensure OpenWebUI is running on port 8080
- Upload `knowledge_fusion_function.py` (not as ZIP)
- Enable the function after upload

## Future Roadmap

- **Watson.ai Integration**: Enterprise-grade AI capabilities
- **Advanced Vector Search**: Hybrid search with multiple embedding models
- **Real-time Collaboration**: Multi-user knowledge sharing
- **Custom Knowledge Connectors**: Easy integration with enterprise systems

---

**Ready to experience "Beyond Basic RAG"?** Start with the [5-minute Quick Start Guide](docs/STARTUP_GUIDE.md)!

📚 **Complete Documentation Index**: See [docs/](docs/) for all documentation organized by category.