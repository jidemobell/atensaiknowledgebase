# 🚚 Migration Guide - With Local Ollama Setup

## 🎯 Overview

This guide helps you migrate your Novel Knowledge Fusion Platform to your work computer using a simple flash drive copying strategy, while leveraging your existing local Ollama installation instead of containerizing it.

## 📋 Simple Migration Strategy

### Your Approach (Recommended for Enterprise + Local Ollama):
1. **Clone OpenWebUI** on work computer
2. **Copy knowledge-fusion** via flash drive  
3. **Copy qwenroute** via flash drive
4. **Copy other root files** via flash drive
5. **Use existing local Ollama** (no container needed)
6. **Transfer to cloned OpenWebUI** and startup

This avoids complex containerization of Ollama while maintaining your preferred local setup.

## 📦 Preparation on Personal Computer

### Step 1: Prepare Flash Drive Folders
```bash
cd /Users/jidemobell/Documents/IBMALL/TOPOLOGYKNOWLEDGE

# Create organized folders on flash drive (adjust path to your flash drive)
FLASH_DRIVE="/Volumes/YourFlashDrive"  # Update this path
mkdir -p "${FLASH_DRIVE}/TOPOLOGYKNOWLEDGE_TRANSFER"
cd "${FLASH_DRIVE}/TOPOLOGYKNOWLEDGE_TRANSFER"

# Create organized structure
mkdir -p knowledge-fusion
mkdir -p qwenroute  
mkdir -p root-files
mkdir -p documentation
```

### Step 2: Copy Core Components
```bash
# Copy knowledge-fusion folder
echo "📁 Copying knowledge-fusion..."
cp -r /Users/jidemobell/Documents/IBMALL/TOPOLOGYKNOWLEDGE/openwebuibase/knowledge-fusion/* "${FLASH_DRIVE}/TOPOLOGYKNOWLEDGE_TRANSFER/knowledge-fusion/"

# Copy qwenroute folder  
echo "📁 Copying qwenroute..."
cp -r /Users/jidemobell/Documents/IBMALL/TOPOLOGYKNOWLEDGE/qwenroute/* "${FLASH_DRIVE}/TOPOLOGYKNOWLEDGE_TRANSFER/qwenroute/"

# Copy essential root files
echo "📁 Copying root files..."
cp /Users/jidemobell/Documents/IBMALL/TOPOLOGYKNOWLEDGE/requirements.txt "${FLASH_DRIVE}/TOPOLOGYKNOWLEDGE_TRANSFER/root-files/"
cp /Users/jidemobell/Documents/IBMALL/TOPOLOGYKNOWLEDGE/.env.docker.template "${FLASH_DRIVE}/TOPOLOGYKNOWLEDGE_TRANSFER/root-files/.env.template"
cp /Users/jidemobell/Documents/IBMALL/TOPOLOGYKNOWLEDGE/knowledge_base.json "${FLASH_DRIVE}/TOPOLOGYKNOWLEDGE_TRANSFER/root-files/"

# Copy documentation
echo "📚 Copying documentation..."
cp /Users/jidemobell/Documents/IBMALL/TOPOLOGYKNOWLEDGE/docs/*.md "${FLASH_DRIVE}/TOPOLOGYKNOWLEDGE_TRANSFER/documentation/"
```

### Step 3: Create Local Ollama Setup Instructions
```bash
# Create setup instructions for work computer with local Ollama
cat > "${FLASH_DRIVE}/TOPOLOGYKNOWLEDGE_TRANSFER/SETUP_INSTRUCTIONS_LOCAL_OLLAMA.md" << 'EOF'
# Setup Instructions for Work Computer (With Local Ollama)

## Prerequisites on Work Computer:
1. Git installed
2. Python 3.11+ installed (Python 3.11.x recommended, 3.12.x also works)
3. Node.js 16+ installed
4. **Ollama installed locally** (this guide assumes you have Ollama running locally)

## Setup Steps:

### 1. Verify Local Ollama Installation
```bash
# Check if Ollama is running locally
ollama --version
ollama list

# Start Ollama service if needed
ollama serve  # Usually runs on http://localhost:11434

# Pull recommended models for Knowledge Fusion
ollama pull llama3.1:8b
ollama pull mistral:7b
ollama pull granite3-moe:3b  # IBM's model
```

### 2. Clone OpenWebUI
```bash
git clone https://github.com/open-webui/open-webui.git
cd open-webui
```

### 3. Copy Knowledge Fusion
```bash
# Copy from flash drive to OpenWebUI (adjust flash drive path)
cp -r /path/to/flashdrive/TOPOLOGYKNOWLEDGE_TRANSFER/knowledge-fusion ./
```

### 4. Copy QwenRoute (Optional)
```bash
# Copy qwenroute to project root or desired location
cp -r /path/to/flashdrive/TOPOLOGYKNOWLEDGE_TRANSFER/qwenroute ./
```

### 5. Copy Root Files
```bash
# Copy essential configuration files
cp /path/to/flashdrive/TOPOLOGYKNOWLEDGE_TRANSFER/root-files/requirements.txt ./
cp /path/to/flashdrive/TOPOLOGYKNOWLEDGE_TRANSFER/root-files/.env.template ./
cp /path/to/flashdrive/TOPOLOGYKNOWLEDGE_TRANSFER/root-files/knowledge_base.json ./
```

### 6. Setup Python Environment
```bash
# Check available Python versions
python3 --version
python3.11 --version  # Preferred
python3.12 --version  # Also works

# Create Python virtual environment (use Python 3.11 if available)
python3.11 -m venv venv
# OR python3.12 -m venv venv
# OR python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 7. Configure Environment for Local Ollama
```bash
# Create .env file from template
cp .env.template .env

# Edit .env with your API keys and local Ollama configuration
cat > .env << 'ENVEOF'
# API Keys - Add your actual keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GROQ_API_KEY=your_groq_key_here

# Local Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
ENABLE_OLLAMA=true

# System Configuration
DEBUG=true
LOG_LEVEL=INFO

# Disable containerized services (using local Ollama)
USE_DOCKER_OLLAMA=false
ENVEOF
```

### 8. Start Services (Local Ollama Mode)

#### Traditional Setup (Recommended with Local Ollama):
```bash
# Ensure Ollama is running locally
ollama serve &  # If not already running

# Start Knowledge Fusion Engine (Novel Architecture)
python knowledge-fusion/enhanced_backend/main_novel_architecture.py &

# Start Multi-Agent System
python knowledge-fusion/enhanced_backend/main_enhanced.py &

# Start OpenWebUI frontend (in separate terminal)
npm install
npm run dev
```

#### Optional: Lightweight Docker for Backend Only
If you want to containerize just the backend while keeping Ollama local:
```bash
# Create lightweight docker-compose for backend only
cat > docker-compose.local-ollama.yml << 'DOCKEREOF'
version: '3.8'

services:
  # Novel Knowledge Fusion Backend (without Ollama)
  knowledge-fusion:
    build: 
      context: .
      dockerfile: docker/Dockerfile.backend
    container_name: knowledge-fusion-backend
    ports:
      - "8000:8000"  # Basic service
      - "8001:8001"  # Multi-agent system
      - "8003:8003"  # Novel fusion engine
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - DEBUG=false
      - LOG_LEVEL=INFO
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  # Redis for caching
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
DOCKEREOF

# Start with local Ollama integration
docker-compose -f docker-compose.local-ollama.yml up -d
```

## Quick Test:
```bash
# Test local Ollama
curl http://localhost:11434/api/tags

# Test services
curl http://localhost:8003/health    # Novel Fusion Engine
curl http://localhost:8001/health    # Multi-Agent System
curl http://localhost:8080          # OpenWebUI Interface

# Test model integration
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test local ollama integration", "enable_temporal": true}'
```
EOF
```

## 🖥️ Setup on Work Computer

### Step 1: Install Local Ollama (if not already installed)
```bash
# Install Ollama on work computer
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull recommended models
ollama pull llama3.1:8b
ollama pull mistral:7b
ollama pull granite3-moe:3b  # Great for enterprise/IBM environments
```

### Step 2: Clone OpenWebUI
```bash
# On your work computer
git clone https://github.com/open-webui/open-webui.git
cd open-webui
```

### Step 3: Copy Files from Flash Drive
```bash
# Adjust flash drive path for your work computer
FLASH_DRIVE="/media/flashdrive"  # Linux
# FLASH_DRIVE="/Volumes/YourFlashDrive"  # macOS  
# FLASH_DRIVE="D:"  # Windows

# Copy knowledge-fusion
cp -r "${FLASH_DRIVE}/TOPOLOGYKNOWLEDGE_TRANSFER/knowledge-fusion" ./

# Copy qwenroute (optional - for additional functionality)
cp -r "${FLASH_DRIVE}/TOPOLOGYKNOWLEDGE_TRANSFER/qwenroute" ./

# Copy root files
cp "${FLASH_DRIVE}/TOPOLOGYKNOWLEDGE_TRANSFER/root-files/requirements.txt" ./
cp "${FLASH_DRIVE}/TOPOLOGYKNOWLEDGE_TRANSFER/root-files/.env.template" ./
cp "${FLASH_DRIVE}/TOPOLOGYKNOWLEDGE_TRANSFER/root-files/knowledge_base.json" ./
```

### Step 4: Python Environment Setup
```bash
# Check available Python versions
python3 --version
python3.11 --version  # Preferred for production compatibility
python3.12 --version  # Also excellent (your current dev version)

# Create Python virtual environment with preferred version
python3.11 -m venv venv  # Recommended
# OR python3.12 -m venv venv  # Also works great
# OR python3 -m venv venv     # Fallback

source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure for Local Ollama
```bash
# Setup environment variables for local Ollama
cp .env.template .env

# Configure for local Ollama setup
cat > .env << 'EOF'
# API Keys - Add your actual keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GROQ_API_KEY=your_groq_key_here

# Local Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
ENABLE_OLLAMA=true

# System Configuration
DEBUG=true
LOG_LEVEL=INFO

# Local setup (not using Docker for Ollama)
USE_DOCKER_OLLAMA=false
EOF
```

## 🚀 Startup Options

### Option A: Full Local Setup (Recommended)
```bash
# 1. Start Ollama (if not running)
ollama serve &

# 2. Start Knowledge Fusion Engine (Novel Architecture)
source venv/bin/activate
python knowledge-fusion/enhanced_backend/main_novel_architecture.py &

# 3. Start Multi-Agent System
python knowledge-fusion/enhanced_backend/main_enhanced.py &

# 4. Start OpenWebUI (in separate terminal)
npm install
npm run dev
```

### Option B: Hybrid Setup (Backend Container + Local Ollama)
```bash
# Create lightweight docker-compose without Ollama
cat > docker-compose.local-ollama.yml << 'EOF'
version: '3.8'

services:
  knowledge-fusion:
    build: 
      context: .
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8000:8000"
      - "8001:8001"
      - "8003:8003"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  redis_data:
EOF

# Start Ollama locally
ollama serve &

# Start containerized backend with local Ollama integration
docker-compose -f docker-compose.local-ollama.yml up -d
```

## ✅ Verification

### Test Local Ollama Integration
```bash
# 1. Verify Ollama is running
ollama list
curl http://localhost:11434/api/tags

# 2. Test model inference
ollama run llama3.1:8b "Hello, test local Ollama integration"

# 3. Test Knowledge Fusion Platform
curl http://localhost:8003/health
curl http://localhost:8001/health

# 4. Test end-to-end functionality
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "explain temporal knowledge synthesis using local models",
    "enable_temporal": true,
    "use_local_models": true
  }'

# 5. Access web interface
# http://localhost:8080
```

### Verify Model Availability
```bash
# Check available models
ollama list

# Should show models like:
# llama3.1:8b
# mistral:7b  
# granite3-moe:3b
```

## 🔄 Future Updates

### Simple Update Process with Local Ollama:
1. **Make changes** on personal computer
2. **Test with local Ollama** 
3. **Copy changed files** to flash drive
4. **Transfer to work computer**
5. **Replace files** and restart services (Ollama keeps running)

### Model Updates:
```bash
# Update/add models on work computer
ollama pull llama3.1:8b      # Update existing
ollama pull codellama:13b    # Add new model
ollama pull granite3-moe:3b  # IBM enterprise model
```

### Quick File Updates:
```bash
# Copy specific updated files
cp /path/to/updated/file.py /path/to/work/project/file.py

# Restart Python services (Ollama keeps running)
pkill -f main_novel_architecture.py
pkill -f main_enhanced.py
python knowledge-fusion/enhanced_backend/main_novel_architecture.py &
python knowledge-fusion/enhanced_backend/main_enhanced.py &
```

## 📁 Project Structure After Setup

```
open-webui/
├── knowledge-fusion/          # Your Novel Knowledge Fusion Platform
│   ├── enhanced_backend/
│   ├── functions/
│   └── requirements.txt
├── qwenroute/                # Optional: Additional functionality
├── requirements.txt          # Python dependencies
├── .env                     # Environment variables (API keys)
├── knowledge_base.json       # Knowledge base data
└── [OpenWebUI files]        # Standard OpenWebUI structure

# Local Ollama (separate installation)
~/.ollama/                    # Ollama models and configuration
```

## 🎯 Key Benefits of Local Ollama Approach

✅ **Performance** - Direct local model access, no container overhead  
✅ **Reliability** - Your familiar Ollama setup  
✅ **Flexibility** - Easy model management with `ollama pull/rm`  
✅ **Resource Efficiency** - No duplicate model storage in containers  
✅ **Enterprise Friendly** - Many enterprises prefer local model management  
✅ **Development Speed** - Faster iteration and testing  

## 🔧 Troubleshooting

### Ollama Connection Issues:
```bash
# Check Ollama service
ps aux | grep ollama
curl http://localhost:11434/api/tags

# Restart Ollama if needed
pkill ollama
ollama serve &
```

### Python Service Issues:
```bash
# Check services
ps aux | grep python
lsof -i :8001,8003,8080

# Restart specific service
pkill -f main_novel_architecture.py
python knowledge-fusion/enhanced_backend/main_novel_architecture.py &
```

### Model Loading Issues:
```bash
# Verify model availability
ollama list
ollama pull llama3.1:8b  # Re-download if needed

# Test model directly
ollama run llama3.1:8b "test prompt"
```

## 📞 Support

If you encounter issues:
1. Check local Ollama status: `ollama list`
2. Verify Python services: `curl http://localhost:8003/health`
3. Check logs in terminal outputs
4. Ensure API keys are configured in `.env`

---

*This local Ollama migration approach ensures your Novel Knowledge Fusion Platform leverages your preferred local model setup while maintaining all innovative capabilities.*
