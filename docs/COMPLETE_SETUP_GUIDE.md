# 🚀 IBM Knowledge Fusion Platform - Complete Setup Guide

## 📋 Table of Contents

1. [Prerequisites & Installation](#prerequisites--installation)
2. [Environment Setup](#environment-setup)
3. [OpenWebUI Configuration](#openwebui-configuration)
4. [Knowledge Fusion Activation](#knowledge-fusion-activation)
5. [GitHub Repository Integration](#github-repository-integration)
6. [Authentication & Security](#authentication--security)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## 🛠️ Prerequisites & Installation

### System Requirements
- **Python**: 3.11+ (required)
- **Docker**: Latest version (for containerized deployment)
- **Ollama**: Latest version (for local AI models)
- **Git**: For repository cloning
- **Memory**: 8GB+ RAM recommended
- **Storage**: 10GB+ free space

### Step 1: Clone the Repository
```bash
# Clone the IBM Knowledge Fusion Platform
git clone [YOUR_REPOSITORY_URL]
cd TOPOLOGYKNOWLEDGE

# Verify project structure
ls -la
```

### Step 2: Install Ollama & Models
```bash
# Install Ollama (macOS)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# In a new terminal, install required models
ollama pull llama3.2:latest
ollama pull nomic-embed-text:latest

# Verify models are installed
ollama list
```

### Step 3: Install Docker (for production deployment)
```bash
# macOS
brew install docker

# Or download from: https://www.docker.com/products/docker-desktop
```

---

## 🔧 Environment Setup

### Option A: Local Development Setup (Recommended for Development)

```bash
# Create and activate Python virtual environment
python3.11 -m venv openwebui_venv
source openwebui_venv/bin/activate

# Install OpenWebUI
pip install open-webui

# Verify installation
open-webui --version
```

### Option B: Docker Setup (Recommended for Production)

```bash
# Verify Docker is running
docker info

# Choose your deployment method:
# 1. Hybrid approach (official image + knowledge fusion)
./deploy-hybrid-kf.sh

# 2. Full backend build (includes QwenRoute backend)
./deploy-full-backend.sh
```

---

## ⚙️ OpenWebUI Configuration

### Step 1: First Launch
```bash
# For local development
source openwebui_venv/bin/activate
open-webui serve --host 0.0.0.0 --port 8080

# Access at: http://localhost:8080
```

### Step 2: Initial Setup in Web Interface

1. **Create Admin Account**
   - Navigate to http://localhost:8080
   - Sign up with your admin credentials
   - **Important**: First user becomes admin

2. **Configure Models**
   - Go to **Settings** → **Models**
   - Verify Ollama connection: `http://localhost:11434`
   - Confirm models are detected:
     - `llama3.2:latest`
     - `nomic-embed-text:latest`

3. **Essential Settings**
   ```
   Settings → General:
   ✅ Enable RAG (Retrieval Augmented Generation)
   ✅ Enable Web Search
   ✅ Enable File Upload
   
   Settings → Audio:
   ✅ Enable Speech-to-Text
   ✅ Enable Text-to-Speech
   
   Settings → Advanced:
   ✅ Enable Function Calling
   ✅ Enable Tools
   ✅ Enable Code Execution (Sandbox)
   ```

### Step 3: Knowledge Fusion Settings

1. **Enable Custom Functions**
   - Go to **Settings** → **Functions**
   - Click **"+ Add Function"**
   - **Import** or **Create** IBM Knowledge Fusion functions

2. **Configure Knowledge Base**
   - Go to **Settings** → **Documents**
   - Upload your knowledge base files
   - Configure document processing settings

3. **Advanced Knowledge Fusion**
   ```
   Settings → Experimental:
   ✅ Enable Advanced RAG
   ✅ Enable Hybrid Search
   ✅ Enable Context Memory
   ✅ Enable Multi-Source Intelligence
   ```

---

## 🧠 Knowledge Fusion Activation

### Step 1: Run Knowledge Fusion Setup
```bash
# Activate knowledge fusion components
./setup_knowledge_fusion.sh

# This will:
# ✅ Configure backend integration
# ✅ Setup enhanced routing
# ✅ Enable multi-source intelligence
# ✅ Initialize GitHub integration
```

### Step 2: Verify Knowledge Fusion Status
```bash
# Check if all components are running
curl http://localhost:8000/health  # QwenRoute backend
curl http://localhost:8001/health  # Enhanced backend
curl http://localhost:8080/health  # OpenWebUI frontend
```

### Step 3: Test Knowledge Fusion Features

1. **Upload Test Documents**
   - Upload a few test PDF/text files
   - Verify they are processed and indexed

2. **Test Multi-Source Intelligence**
   - Ask a question that requires knowledge synthesis
   - Example: "Analyze the architectural patterns in our recent projects"

3. **Test GitHub Integration**
   - Ask about code patterns from configured repositories
   - Example: "What are the common design patterns in our codebase?"

---

## 🔗 GitHub Repository Integration

### Step 1: Configure Repository Access

**⚠️ Authentication Requirements:**
- **Public Repositories**: No authentication needed
- **Private Repositories**: Requires GitHub Personal Access Token (PAT)

### Step 2: Generate GitHub Personal Access Token (for private repos)

1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens**
2. Click **"Generate new token (classic)"**
3. Select scopes:
   ```
   ✅ repo (Full control of private repositories)
   ✅ read:org (Read org membership)
   ✅ read:user (Read user profile data)
   ```
4. Generate and **copy the token securely**

### Step 3: Configure Repository Links

Edit `github_sources.yml`:
```yaml
github_sources:
  ibm_research:
    repositories:
      - url: "https://github.com/IBM/your-ai-project"
        focus: "aiops_patterns"
        extraction_method: "code_analysis"
        auth_required: true  # Set to false for public repos
      
  enterprise_projects:
    repositories:
      - url: "https://github.com/company/topology-service"
        focus: "domain_expertise"
        extraction_method: "architecture_analysis"
        auth_required: true
        
  research_papers:
    repositories:
      - url: "https://github.com/research/novel-ai-approaches"
        focus: "cutting_edge_techniques"
        extraction_method: "research_implementation"
        auth_required: false  # Public research repo

# Authentication configuration
auth_config:
  github_token: "${GITHUB_TOKEN}"  # Set in environment
  rate_limit_respect: true
  cache_enabled: true
  cache_duration: "24h"
```

### Step 4: Set Environment Variables
```bash
# Add to your shell profile (.zshrc/.bashrc)
export GITHUB_TOKEN="your_github_personal_access_token_here"

# Or create .env file in project root
echo "GITHUB_TOKEN=your_token_here" >> .env
```

### Step 5: Test GitHub Integration
```bash
# Test repository access
python -c "from knowledge_fusion_init import test_github_access; test_github_access()"

# Manually test access
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

---

## 🔐 Authentication & Security

### Local Development Security
```bash
# Generate secure keys
export WEBUI_SECRET_KEY=$(openssl rand -hex 32)
export GITHUB_TOKEN="your_personal_access_token"

# Save to .env file
cat > .env << EOF
WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}
GITHUB_TOKEN=${GITHUB_TOKEN}
ENABLE_SIGNUP=false
WEBUI_AUTH=true
EOF
```

### Production Security Checklist
- [ ] Change default secret keys
- [ ] Disable public signup (`ENABLE_SIGNUP=false`)
- [ ] Enable authentication (`WEBUI_AUTH=true`)
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up proper CORS origins
- [ ] Use environment variables for all secrets
- [ ] Regular GitHub token rotation
- [ ] Monitor access logs

---

## 🏭 Production Deployment

### IBM Environment Deployment

1. **Prepare Environment**
   ```bash
   # Copy project to IBM environment
   # Exclude virtual environments and cache
   rsync -av --exclude='*venv' --exclude='__pycache__' . ibm-server:/path/to/deployment/
   ```

2. **Deploy with Docker**
   ```bash
   # On IBM server
   cd /path/to/deployment
   
   # Create production environment file
   cp .env.production.template .env
   # Edit .env with production values
   
   # Deploy with full backend
   ./deploy-full-backend.sh
   ```

3. **IBM-Specific Configuration**
   ```yaml
   # docker-compose.override.yml for IBM
   version: '3.8'
   services:
     openwebui-frontend:
       environment:
         - WEBUI_URL=https://your-ibm-domain.com
         - CORS_ALLOW_ORIGIN=https://your-ibm-domain.com
         - ENABLE_SIGNUP=false
         - WEBUI_AUTH=true
   ```

### Environment Migration
When moving to new environment, virtual environments will be auto-created:
- `setup_knowledge_fusion.sh` - Detects and creates venv if needed
- `prepare_flash_drive.sh` - Full environment setup script
- `qwenroute/implementation/start.sh` - Auto-venv creation

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Ollama Connection Issues
```bash
# Check Ollama status
ollama list
ps aux | grep ollama

# Restart Ollama
pkill ollama
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

#### 2. OpenWebUI Won't Start
```bash
# Check Python environment
source openwebui_venv/bin/activate
which python
python --version

# Reinstall OpenWebUI
pip uninstall open-webui
pip install open-webui

# Check for port conflicts
lsof -i :8080
```

#### 3. GitHub Authentication Fails
```bash
# Test token
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit

# Check token permissions
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Regenerate token if needed
```

#### 4. Knowledge Fusion Not Working
```bash
# Check backend status
curl http://localhost:8000/health
curl http://localhost:8001/health

# Restart knowledge fusion
./setup_knowledge_fusion.sh

# Check logs
docker-compose logs knowledge-fusion-backend
```

### Getting Help

1. **Documentation**: Check `docs/` folder for detailed guides
2. **Logs**: Always check logs first (`docker-compose logs` or OpenWebUI admin panel)
3. **GitHub Issues**: Report issues with full error logs
4. **IBM Support**: For enterprise deployment issues

---

## 📚 Related Documentation

- **[IBM Deployment Guide](./IBM_DEPLOYMENT_GUIDE.md)** - Enterprise deployment
- **[Knowledge Fusion Architecture](./docs/KNOWLEDGE_FUSION_ARCHITECTURE.md)** - Technical architecture
- **[Quick Reference](./QUICK_REFERENCE.md)** - Command cheat sheet
- **[Model Integration](./docs/MODEL_INTEGRATION.md)** - AI model setup
- **[Migration Guide](./docs/MIGRATION_GUIDE.md)** - Environment migration

---

## ✅ Setup Verification Checklist

After completing setup, verify these work:

### Basic Functionality
- [ ] OpenWebUI loads at http://localhost:8080
- [ ] Can create account and login
- [ ] Ollama models are detected and working
- [ ] Can send messages and get responses

### Knowledge Fusion Features
- [ ] Can upload and process documents
- [ ] Multi-source knowledge synthesis working
- [ ] GitHub repository integration functional
- [ ] Enhanced backends responding (ports 8000, 8001)

### Production Readiness
- [ ] Docker deployment works
- [ ] Environment variables configured
- [ ] Authentication enabled
- [ ] Security settings applied
- [ ] Backup and monitoring configured

**🎉 Congratulations! Your IBM Knowledge Fusion Platform is ready!**
