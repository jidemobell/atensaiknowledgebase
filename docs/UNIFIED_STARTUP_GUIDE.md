# 🚀 TOPOLOGY KNOWLEDGE PLATFORM - UNIFIED STARTUP

## Overview

This project provides a unified approach to run the complete Topology Knowledge Platform with just **2 simple commands**:

```bash
# Quick Start - Interactive Menu
./start.sh

# Or directly:
./start_server_mode.sh    # For development/direct mode
./start_docker_mode.sh    # For containerized mode
```

## Project Structure

```
TOPOLOGYKNOWLEDGE/
├── corebackend/          # Core Backend (formerly QwenRoute)
│   ├── qwenroute/
│   └── implementation/
├── openwebuibase/        # OpenWebUI with integrated features
│   ├── knowledge-fusion/ # IBM Knowledge Fusion Platform
│   │   ├── functions/    # OpenWebUI Functions
│   │   ├── enhanced_backend/
│   │   └── integration/
│   └── backend/
├── start.sh             # 🎯 MAIN LAUNCHER (Interactive)
├── start_server_mode.sh # 🖥️  SERVER MODE
└── start_docker_mode.sh # 🐳 DOCKER MODE
```

## 🎯 Quick Start Guide

### Option 1: Interactive Launcher (Recommended)
```bash
./start.sh
```
This provides a menu to choose:
- 🖥️  Server Mode
- 🐳 Docker Mode  
- 🔍 Status Check
- 🛑 Stop All

### Option 2: Direct Mode Selection

**Server Mode** (Development/Local):
```bash
./start_server_mode.sh
```

**Docker Mode** (Production/Containerized):
```bash
./start_docker_mode.sh
```

## 🖥️ Server Mode Details

**What it does:**
1. ✅ Verifies Python 3.11 virtual environment
2. ✅ Starts/verifies local Ollama
3. ✅ Starts Core Backend (Port 8001)
4. ✅ Starts Knowledge Fusion Backend (Port 8002)  
5. ✅ Starts OpenWebUI with integrated functions (Port 3000)
6. ✅ Runs health checks on all services
7. ✅ Provides monitoring and status updates

**Requirements:**
- Python 3.11+ virtual environment set up
- Ollama installed locally
- All dependencies installed

**Access Points:**
- 🌐 OpenWebUI: http://localhost:3000
- 🔧 Core Backend API: http://localhost:8001
- 🧠 Knowledge Fusion: http://localhost:8002
- 🤖 Ollama API: http://localhost:11434

## 🐳 Docker Mode Details

**What it does:**
1. ✅ Verifies Docker and docker-compose
2. ✅ Creates optimized Docker Compose configuration
3. ✅ Builds all containers with Knowledge Fusion integration
4. ✅ Starts/verifies local Ollama (runs outside Docker)
5. ✅ Starts all services in containers
6. ✅ Runs health checks and monitoring

**Requirements:**
- Docker installed and running
- docker-compose available
- Ollama installed locally

**Features:**
- Isolated container environment
- Automatic service dependencies
- Health checks and restart policies
- Easy scaling and management

## 🧠 Knowledge Fusion Integration

The IBM Knowledge Fusion is **automatically integrated** in both modes:

### Server Mode Integration:
- Function file: `openwebuibase/knowledge-fusion/functions/ibm_knowledge_fusion.py`
- Backend runs on port 8002
- Automatically available in OpenWebUI Functions

### Docker Mode Integration:
- Knowledge Fusion built into OpenWebUI container
- Function automatically mounted and available
- Backend runs in dedicated container

### To Enable in OpenWebUI:
1. Access http://localhost:3000
2. Go to **Settings** → **Functions**
3. Find **"IBM Knowledge Fusion"**
4. Enable the function
5. Start using enhanced AI capabilities!

## 🔍 Monitoring and Management

### Health Checks
Both scripts provide continuous monitoring:
- Service availability checks every 30 seconds
- Automatic failure detection
- Status reporting

### Logs and Debugging

**Server Mode:**
```bash
# View real-time logs
tail -f demo.log

# Check specific service
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:3000
```

**Docker Mode:**
```bash
# View all logs
docker-compose -f docker-compose.knowledge-fusion.yml logs -f

# View specific service logs
docker-compose -f docker-compose.knowledge-fusion.yml logs -f openwebui
docker-compose -f docker-compose.knowledge-fusion.yml logs -f core-backend
docker-compose -f docker-compose.knowledge-fusion.yml logs -f knowledge-fusion

# Check container status
docker-compose -f docker-compose.knowledge-fusion.yml ps
```

### Stopping Services

**Using the launcher:**
```bash
./start.sh  # Choose option 4 to stop all
```

**Manual stopping:**
```bash
# Server mode: Ctrl+C in the terminal
# Docker mode: 
./start_docker_mode.sh --stop
# or
docker-compose -f docker-compose.knowledge-fusion.yml down
```

## 🛠️ Troubleshooting

### Common Issues:

1. **Port conflicts:**
   - Check what's using ports: `lsof -i :3000,8001,8002,11434`
   - Stop conflicting services

2. **Ollama not running:**
   - Install: https://ollama.ai
   - Start: `ollama serve`
   - Verify: `curl http://localhost:11434`

3. **Docker issues:**
   - Ensure Docker is running: `docker info`
   - Check disk space: `docker system df`
   - Clean up: `docker system prune`

4. **Python environment issues:**
   - Verify virtual environment: `source openwebui_venv/bin/activate`
   - Check Python version: `python --version` (should be 3.11+)

### Status Checking:
```bash
# Quick status check
./start.sh  # Choose option 3

# Manual checks
curl -s http://localhost:3000 && echo "OpenWebUI: OK"
curl -s http://localhost:8001/health && echo "Core Backend: OK"  
curl -s http://localhost:8002/health && echo "Knowledge Fusion: OK"
curl -s http://localhost:11434 && echo "Ollama: OK"
```

## 📚 Documentation

- **API Documentation:** `docs/QWENROUTE_API_DOCUMENTATION.md`
- **Setup Guide:** `OPENWEBUI_SUCCESS.md`
- **Docker Guide:** `DOCKER_SUCCESS_GUIDE.md`
- **Knowledge Fusion:** `openwebuibase/knowledge-fusion/README.md`

## 🎯 Next Steps

1. **First Time Setup:**
   ```bash
   ./start.sh  # Choose your preferred mode
   ```

2. **Access OpenWebUI:**
   - Visit: http://localhost:3000
   - Create admin account (first time)
   - Enable IBM Knowledge Fusion function

3. **Start Using:**
   - Ask complex questions
   - Upload documents for analysis
   - Experience enhanced AI capabilities

## 🔄 Migration from Old Scripts

If you have old startup scripts, you can safely remove them:
- `run_openwebui.sh` → Use `./start_server_mode.sh`
- `start_openwebui.sh` → Use `./start_server_mode.sh`  
- Multiple docker scripts → Use `./start_docker_mode.sh`

The new unified scripts handle everything the old ones did, plus more!

---

**🎉 Enjoy your unified Topology Knowledge Platform!**
