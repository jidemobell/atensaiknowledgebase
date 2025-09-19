# Simple Startup Guide

> **Quick start for busy developers**: Get Knowledge Fusion running in minutes and understand what makes it different.

## 🚀 Super Quick Start (5 minutes)

```bash
# 1. Setup (one-time)
./setup_ibm.sh          # or ./setup.sh for non-IBM

# 2. Start services  
./bin/start_server_mode.sh

# 3. Check status
./status_ibm.sh

# 4. Get function code
cat knowledge_fusion_function.py

# 5. Upload to OpenWebUI Admin → Functions
# 6. Test in chat: "How do I debug memory leaks in microservices?"
```

## 🎯 What This System Expects After Setup

### ✅ Running Services Checklist
```
Port 8001: CoreBackend                     ← Deep analysis engine
Port 8002: Knowledge Fusion Backend        ← Knowledge synthesis  
Port 9000: Knowledge Fusion Gateway        ← Intelligent routing
Port 8080: OpenWebUI (external)           ← Your existing UI
```

### ✅ Integration Checklist
```
📁 knowledge_fusion_function.py → Uploaded to OpenWebUI
🔧 Function enabled in OpenWebUI Admin Panel
🔗 Gateway accessible from OpenWebUI environment
📊 Logs accessible via ./view_logs.sh
```

### ✅ Data Structure
```
data/
├── cases/          ← Put your case studies here
├── repos/          ← Git submodules with code examples  
└── chromadb/       ← Automatic vector database
```

## 🧠 How We're Different

### Traditional RAG Approach
```
Question → Search Documents → Generate Answer
```
**Problems:**
- Single knowledge source
- No intelligent routing
- Brittle when sources are unavailable
- No synthesis across different types of knowledge

### Knowledge Fusion Approach
```
Question → Gateway Intelligence → Multi-Backend Synthesis → Enhanced Answer
```
**Advantages:**
- **Intelligent Routing**: Automatically chooses best knowledge source
- **Graceful Fallbacks**: System adapts when services are unavailable  
- **Multi-Source Synthesis**: Combines different types of knowledge
- **Decoupled Integration**: Works with existing OpenWebUI without changes
- **Enterprise Ready**: Built for corporate networks and scaling

## 🔄 The Knowledge Fusion Flow

### User Perspective
1. **Ask question** in OpenWebUI chat
2. **Get enhanced answer** with intelligent source attribution
3. **See real-time status** ("🔍 Routing to Knowledge Fusion...")

### System Perspective  
1. **OpenWebUI** receives user query
2. **Pipe Function** routes to Knowledge Fusion Gateway (9000)
3. **Gateway** intelligently routes to:
   - Knowledge Fusion Backend (8002) for synthesis
   - CoreBackend (8001) for deep analysis
   - Intelligent fallback if services unavailable
4. **Response** synthesized and returned with source attribution

## 📁 Where To Put Your Data

### Case Studies
```bash
mkdir -p data/cases/microservices
echo "# Circuit Breaker Pattern
When dealing with distributed systems..." > data/cases/microservices/circuit_breaker.md
```

### Git Repositories
```bash
# Add your code repositories as knowledge sources
git submodule add https://github.com/your-org/microservices-patterns.git data/repos/patterns

# The system will automatically index and learn from them
```

### Documentation
```bash
# Link your existing docs
ln -s /path/to/your/docs data/cases/documentation
```

## 🎛️ Operation Modes

### Development Mode (Server Mode)
```bash
./bin/start_server_mode.sh
```
- **Best for**: Development, testing, customization
- **Pros**: Easy debugging, direct Python execution, fast iteration
- **Cons**: Not containerized

### Production Mode (Container Mode)
```bash  
./start_docker_mode.sh
```
- **Best for**: Production deployment, scaling
- **Pros**: Isolated environments, scalable, reproducible
- **Cons**: Slightly more complex debugging

## 🔍 Monitoring Your System

### Real-time Logs
```bash
./view_logs.sh              # All logs in terminal
python web_logs.py          # Web interface at :8005
```

### Health Checks
```bash
./status_ibm.sh            # Full system status
curl localhost:9000/health # Gateway health
```

### Testing Integration
```bash
# Test the complete pipeline
curl -X POST http://localhost:9000/knowledge-fusion/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do microservices communicate?"}'
```

## 🛠️ Customization Points

### Gateway Logic (`knowledge_fusion_gateway.py`)
- **Modify routing rules**: Which backend for which types of questions?
- **Add new backends**: Connect additional knowledge sources
- **Custom fallbacks**: Define intelligent degradation paths

### Knowledge Sources (`knowledge-fusion-template/`)
- **Add data processors**: Handle new file types or knowledge formats
- **Custom embeddings**: Use domain-specific embedding models
- **Integration APIs**: Connect to enterprise knowledge systems

### OpenWebUI Integration (`knowledge_fusion_function.py`)
- **Custom UI feedback**: Change status messages and progress indicators
- **Request preprocessing**: Modify queries before routing
- **Response postprocessing**: Format answers for your domain

## 🎯 Success Indicators

You've successfully achieved the "different approach" when:

✅ **Questions get smarter answers** than basic RAG  
✅ **System adapts** when knowledge sources are unavailable  
✅ **Multiple knowledge types** contribute to single answers  
✅ **Source attribution** shows where information came from  
✅ **Corporate integration** works seamlessly with your network  
✅ **Scaling** happens without OpenWebUI modification  

## 🆘 Quick Troubleshooting

### Services won't start?
```bash
# Check for port conflicts
lsof -i :8001,8002,9000,8080

# Restart clean
pkill -f "knowledge_fusion\|uvicorn"
./bin/start_server_mode.sh
```

### Function won't upload?
```bash
# Verify function syntax
python -c "exec(open('knowledge_fusion_function.py').read())"

# Check you're admin in OpenWebUI
# Ensure proper function format (Pipe class)
```

### No intelligent responses?
```bash
# Test gateway directly
curl -X POST localhost:9000/knowledge-fusion/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'

# Check logs for routing decisions
tail -f logs/knowledge_fusion.log
```

## 📚 What's Next?

1. **Add your knowledge sources** to `data/cases/` and `data/repos/`
2. **Customize routing logic** in the gateway for your domain
3. **Scale up** by adding more specialized backends
4. **Enterprise integration** with your existing knowledge systems

---

**The bottom line**: You now have a knowledge synthesis platform that goes beyond simple retrieval-generation to provide intelligent, adaptive, multi-source knowledge fusion. 

Ready to transform how your team accesses and synthesizes knowledge? Start with `./setup_ibm.sh` and follow this guide!

### ✅ Working Components:
- **OpenWebUI Frontend**: Svelte-based production interface
- **Novel Knowledge Fusion Engine**: Advanced temporal synthesis (Port 8003)
- **Multi-Agent Backend**: Research and synthesis capabilities (Port 8001)
- **Basic Service**: Health monitoring and simple queries (Port 8000)

### 🔄 Mock/Demo Components:
- **AI Models**: Currently using simulated responses
- **Knowledge Integration**: Mock synthesis engines
- **Data Sources**: Placeholder implementations

### 🎯 Production Ready Features:
- Real-time temporal knowledge synthesis
- Multi-source data fusion framework
- Predictive analytics engine
- Dynamic knowledge evolution
- Confidence-weighted responses

## 🚀 Quick Start Guide

### Prerequisites
```bash
# System Requirements
- Python 3.8+
- Node.js 16+ (for OpenWebUI frontend)
- Docker (optional, for containerized deployment)
- Git
- 8GB+ RAM recommended
```

### 1. Clone and Setup
```bash
# Clone the repository
cd /your/workspace/directory
git clone <your-repo-url>
cd TOPOLOGYKNOWLEDGE

# Create Python virtual environment
python3 -m venv projectvenv
source projectvenv/bin/activate  # On Windows: projectvenv\Scripts\activate

# Install Python dependencies
pip install fastapi uvicorn aiohttp jinja2 pydantic pytest
```

### 2. Start Backend Services

#### Option A: Start Novel Fusion Engine (Recommended)
```bash
# Terminal 1: Novel Knowledge Fusion Platform (Port 8003)
cd openwebuibase/knowledge-fusion/enhanced_backend
python main_novel_architecture.py
```

#### Option B: Start Multi-Agent System
```bash
# Terminal 2: Enhanced Multi-Agent Backend (Port 8001)
cd openwebuibase/knowledge-fusion/enhanced_backend  
python main_multi_agent.py
```

#### Option C: Start Basic Service
```bash
# Terminal 3: Basic Health/Query Service (Port 8000)
cd qwenroute/implementation/backend
python main_minimal.py
```

### 3. Start Frontend Interface
```bash
# Terminal 4: OpenWebUI Frontend (Port 8080)
cd openwebuibase
npm install
npm run dev
```

### 4. Verify Installation
```bash
# Check backend services
curl http://localhost:8003/health    # Novel Fusion Engine
curl http://localhost:8001/health    # Multi-Agent System  
curl http://localhost:8000/health    # Basic Service

# Access web interface
open http://localhost:8080
```

## 🧪 Demo the System

### 1. Basic Query Test
```bash
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the current trends in microservices architecture?"}'
```

### 2. Temporal Analysis Test
```bash
curl -X POST http://localhost:8003/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "topology-merge service performance over time", "enable_temporal": true}'
```

### 3. Knowledge Fusion Test
```bash
curl -X POST http://localhost:8003/synthesize \
  -H "Content-Type: application/json" \
  -d '{"sources": ["github", "docs", "cases"], "query": "debugging containerization issues"}'
```

### 4. Multi-Agent Research Test  
```bash
curl -X POST http://localhost:8001/research \
  -H "Content-Type: application/json" \
  -d '{"query": "best practices for Kubernetes troubleshooting", "depth": "comprehensive"}'
```

## 📊 Expected Demo Outputs

### Novel Fusion Engine Response:
```json
{
  "response": "Based on temporal analysis of microservices patterns...",
  "confidence": 0.85,
  "temporal_insights": {
    "historical_trends": "...",
    "current_state": "...", 
    "predictions": "..."
  },
  "sources_fusion": {
    "github_patterns": "...",
    "case_insights": "...",
    "documentation_synthesis": "..."
  }
}
```

### Multi-Agent Research Response:
```json
{
  "research_plan": {
    "steps": [
      {"agent": "researcher", "action": "gather_sources"},
      {"agent": "analyzer", "action": "pattern_analysis"},
      {"agent": "synthesizer", "action": "generate_insights"}
    ]
  },
  "findings": "...",
  "confidence": 0.92
}
```

## 🔄 Next Steps: Model Integration

The current system uses **mock responses** for demonstration. See the following guides for production deployment:

1. **[Model Integration Guide](./MODEL_INTEGRATION.md)** - Adding real AI models
2. **[OpenWebUI Setup Guide](./OPENWEBUI_SETUP.md)** - Model management through OpenWebUI
3. **[Docker Deployment Guide](./DOCKER_DEPLOYMENT.md)** - Containerized deployment
4. **[Migration Guide](./MIGRATION_GUIDE.md)** - Moving to production environment

## 🐛 Troubleshooting

### Port Conflicts
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9  
lsof -ti:8003 | xargs kill -9
lsof -ti:8080 | xargs kill -9
```

### Missing Dependencies
```bash
# Reinstall Python packages
pip install -r requirements.txt

# Reinstall Node packages
cd openwebuibase && npm install
```

### Service Not Starting
```bash
# Check Python environment
which python
pip list | grep fastapi

# Check logs
python main_novel_architecture.py --verbose
```

## 📚 Related Documentation

- **[Architecture Overview](./KNOWLEDGE_FUSION_ARCHITECTURE.md)**
- **[Research Foundation](./qwenroute/plan/RESEARCH_PAPERS.md)** 
- **[Project Vision](./PROJECT_VISION.md)**
- **[Advanced Features](./ADVANCED_ARCHITECTURE.md)**

---

*This system represents a novel approach to enterprise AI, going beyond traditional RAG to implement true knowledge fusion with temporal awareness and predictive capabilities.*
