# Simple Startup Guide

> **Quick start for busy developers**: Get Knowledge Fusion running in minutes and understand what makes it different.

## 🚀 Super Quick Start (5 minutes)

```bash
# 1. Start Knowledge Fusion services
./bin/start_server_mode.sh

# 2. Install OpenWebUI separately (if not already installed)
pip install open-webui
open-webui serve --port 8080

# 3. Get function code
cat knowledge_fusion_function.py

# 4. Upload to OpenWebUI Admin → Functions → Create Function
# 5. Enable the function in OpenWebUI
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
📊 Logs accessible via ./bin/view_logs.sh
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
./bin/view_logs.sh          # Advanced monitoring with service health checks
tail -f logs/knowledge_fusion.log  # Basic log monitoring
```

### Health Checks
```bash
# Check all services status
curl localhost:9000/health  # Gateway health
curl localhost:8001/health  # Core Backend health  
curl localhost:8002/health  # Knowledge Fusion Backend health
curl localhost:8080/health  # OpenWebUI health
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

Ready to transform how your team accesses and synthesizes knowledge? Start with `./bin/start_server_mode.sh` and follow this guide!

## 🚀 Complete Setup Guide

### Prerequisites
```bash
# System Requirements
- Python 3.8+
- Git
- 4GB+ RAM recommended
- OpenWebUI (can be installed separately)
```

### 1. Start Knowledge Fusion Platform
```bash
# Start all services in one command
./bin/start_server_mode.sh
```

This script will:
- ✅ Set up Python virtual environment (`openwebui_venv/`)
- ✅ Install required dependencies
- ✅ Start Core Backend (Port 8001)
- ✅ Start Knowledge Fusion Backend (Port 8002) 
- ✅ Start Knowledge Fusion Gateway (Port 9000)
- ✅ Configure ChromaDB vector database

### 2. Install OpenWebUI (if not already installed)
```bash
# Install OpenWebUI separately
pip install open-webui
open-webui serve --port 8080
```

### 3. Upload Function to OpenWebUI
1. Open OpenWebUI at `http://localhost:8080`
2. Go to **Admin Panel → Functions**
3. Click **Create Function**
4. Copy content from `knowledge_fusion_function.py`
5. Paste and save the function
6. **Enable** the function in your settings

### 4. Verify Services
```bash
# Check all services are running
curl http://localhost:8001/health  # Core Backend
curl http://localhost:8002/health  # Knowledge Fusion Backend  
curl http://localhost:9000/health  # Gateway
curl http://localhost:8080/health  # OpenWebUI
```

## 📊 Testing the System

### Basic Test
Ask in OpenWebUI chat: *"What are microservices best practices?"*

### Advanced Test  
```bash
# Direct API test
curl -X POST http://localhost:9000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I debug memory leaks in containerized applications?"}'
```

## 🔧 Platform Management

### View Logs and Monitor
```bash
./bin/view_logs.sh          # Advanced monitoring dashboard
tail -f logs/knowledge_fusion.log  # Basic log viewing
```

### Add Knowledge Sources
```bash
./bin/add_knowledge_source.sh      # Add GitHub repositories
./bin/manage_hybrid_sources.sh     # Add web, API, database sources
```

### Automated Updates
```bash
./bin/automated_scheduler.sh       # Set up automatic updates
```

### Platform Demo
```bash
./bin/demo_platform.sh            # Comprehensive platform demonstration
```

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check for port conflicts
lsof -i :8001,8002,9000,8080

# Restart services
pkill -f "knowledge_fusion\|uvicorn"
./bin/start_server_mode.sh
```

### Function Won't Upload
- Ensure OpenWebUI is running on port 8080
- Copy the entire content of `knowledge_fusion_function.py`
- Don't upload as a ZIP file, paste the code directly
- Enable the function after saving

### Connection Issues
```bash
# Test Knowledge Fusion Gateway
curl http://localhost:9000/health

# Check OpenWebUI connection
curl http://localhost:8080/health
```

## 📚 Additional Resources

- **[Integration Flow Guide](INTEGRATION_FLOW.md)** - Detailed setup instructions
- **[Architecture Overview](KNOWLEDGE_FUSION_ARCHITECTURE.md)** - System design
- **[AI Agent Architecture](AI_AGENT_ARCHITECTURE.md)** - Multi-agent system details
- **[Platform Status](PLATFORM_COMPLETION_SUMMARY.md)** - Current capabilities
- **[Scripts Documentation](../bin/README.md)** - All available tools

---

*This system represents a novel approach to enterprise AI, going beyond traditional RAG to implement true knowledge fusion with temporal awareness and predictive capabilities.*
