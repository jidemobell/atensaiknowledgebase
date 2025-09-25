# IBM Knowledge Fusion Platform

**Beyond Basic RAG** - A next-generation knowledge integration platform that provides intelligent routing, multi-source synthesis, and advanced AI capabilities through seamless integration with OpenWebUI.

> 🎯 **Recently Organized**: Platform now features clean architecture with all scripts in `bin/`, comprehensive documentation in `docs/`, and streamlined setup process.

## Quick Start (5 minutes)

```bash
# 1. Setup virtual environments (auto-creates if missing)
./bin/setup_environments.sh

# 2. Setup GitHub authentication (SSH or token)
./bin/setup_github_token.sh

# 3. Start Knowledge Fusion services
./bin/start_server_mode.sh

# 4. Install OpenWebUI separately  
pip install open-webui
open-webui serve --port 8080

# 5. Upload knowledge_fusion_function.py to OpenWebUI Admin Panel → Functions
# 6. Start chatting with enhanced AI capabilities!
```

> 📚 **Need detailed instructions?** See [`docs/COMPLETE_DOCUMENTATION.md`](docs/COMPLETE_DOCUMENTATION.md) for comprehensive script reference, troubleshooting, and advanced usage.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐    ┌─────────────────┐
│   OpenWebUI     │───▶│ Knowledge Fusion │───▶│ Core Backend   │───▶│     Ollama      │
│  (External)     │    │   Gateway        │    │    Engine      │    │   Models        │
│   Port 8080     │    │   Port 9000      │    │   Port 8001    │    │  Port 11434     │
└─────────────────┘    └──────────────────┘    └────────────────┘    └─────────────────┘
                                │
                                │
                         ┌──────▼──────┐
                         │ Knowledge   │
                         │  Fusion     │
                         │ Backend     │
                         │ Port 8002   │
                         └─────────────┘
```

This **pipe-based integration** approach allows OpenWebUI to leverage advanced Knowledge Fusion capabilities while maintaining its familiar interface.

## Why Knowledge Fusion?

### Traditional RAG Limitations:
- **Single-source limitation**: Can only query one database at a time
- **Context fragmentation**: Loses connections between related information  
- **Static responses**: No dynamic knowledge synthesis
- **Limited reasoning**: Simple similarity matching only

### Knowledge Fusion Solution:
- **Multi-source intelligence**: Queries multiple knowledge bases simultaneously
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