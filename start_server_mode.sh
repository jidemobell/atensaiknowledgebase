#!/bin/bash

# =============================================================================
# TOPOLOGY KNOWLEDGE - UNIFIED SERVER MODE STARTUP
# =============================================================================
# This script starts everything in server mode:
# 1. Core Backend (formerly QwenRoute) 
# 2. OpenWebUI with Knowledge Fusion integration
# 3. Knowledge Fusion services and web server
# 4. Runs health checks and confirms all systems are operational
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_BACKEND_PATH="$PROJECT_ROOT/corebackend"
OPENWEBUI_PATH="$PROJECT_ROOT/open-webui-cloned"
KNOWLEDGE_FUSION_PATH="$OPENWEBUI_PATH/knowledge-fusion"
VENV_PATH="$PROJECT_ROOT/openwebui_venv"

# Ports configuration
CORE_BACKEND_PORT=8001
KNOWLEDGE_FUSION_PORT=8002
OPENWEBUI_PORT=3000
OLLAMA_PORT=11434

# PID file for tracking processes
PID_FILE="$PROJECT_ROOT/.topology_pids"

# Create necessary directories
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/data/chromadb"

echo -e "${BLUE}🚀 TOPOLOGY KNOWLEDGE - SERVER MODE STARTUP${NC}"
echo -e "${BLUE}=============================================${NC}"
echo "📁 Project Root: $PROJECT_ROOT"
echo "🔧 Core Backend: $CORE_BACKEND_PATH"
echo "🌐 OpenWebUI: $OPENWEBUI_PATH"
echo "🧠 Knowledge Fusion: $KNOWLEDGE_FUSION_PATH"
echo ""

# Cleanup function for graceful shutdown
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down all services...${NC}"
    if [ -f "$PID_FILE" ]; then
        while read -r service pid; do
            if kill -0 "$pid" 2>/dev/null; then
                echo "  Stopping $service (PID: $pid)"
                kill "$pid" 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=${3:-30}  # Default to 30 attempts if not specified
    local attempt=1
    
    echo "  Waiting for $service_name to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "  ${GREEN}✅ $service_name is ready${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "\n  ${RED}❌ $service_name failed to start within $((max_attempts * 2)) seconds${NC}"
    return 1
}

# Function to start a background service
start_service() {
    local name=$1
    local command=$2
    local working_dir=$3
    local port=$4
    
    echo "🔄 Starting $name..."
    
    # Check if port is already in use
    if check_port $port; then
        echo -e "  ${YELLOW}⚠️  Port $port is already in use. Assuming $name is already running.${NC}"
        return 0
    fi
    
    # Start the service with the virtual environment activated
    cd "$working_dir"
    
    # Make sure we use the correct Python from the virtual environment
    local python_cmd="$VENV_PATH/bin/python"
    local pip_cmd="$VENV_PATH/bin/pip"
    
    # Replace 'python' in the command with the full path to the venv python
    local venv_command="${command//python /$python_cmd }"
    
    # Export the virtual environment variables for the subprocess
    export VIRTUAL_ENV="$VENV_PATH"
    export PATH="$VENV_PATH/bin:$PATH"
    
    eval "$venv_command" &
    local pid=$!
    
    # Store PID for cleanup
    echo "$name $pid" >> "$PID_FILE"
    
    echo "  Started $name with PID: $pid"
    return 0
}

# =============================================================================
# 1. VERIFY ENVIRONMENT
# =============================================================================
echo -e "${BLUE}🔍 Step 1: Verifying Environment${NC}"

# Check if Python 3.11 virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ OpenWebUI virtual environment not found at: $VENV_PATH${NC}"
    echo "Please run the OpenWebUI installation first."
    exit 1
fi

# Activate Python environment
source "$VENV_PATH/bin/activate"
python_version=$(python --version)
echo -e "${GREEN}✅ Using $python_version${NC}"

# Check core directories
for dir in "$CORE_BACKEND_PATH" "$OPENWEBUI_PATH"; do
    if [ ! -d "$dir" ]; then
        echo -e "${RED}❌ Required directory not found: $dir${NC}"
        exit 1
    fi
done

# Check and install Knowledge Fusion if missing
if [ ! -d "$KNOWLEDGE_FUSION_PATH" ]; then
    echo -e "${YELLOW}⚠️  Knowledge Fusion not found, installing...${NC}"
    if [ -d "$PROJECT_ROOT/knowledge-fusion-template" ]; then
        cp -r "$PROJECT_ROOT/knowledge-fusion-template" "$KNOWLEDGE_FUSION_PATH"
        echo -e "${GREEN}✅ Knowledge Fusion installed from template${NC}"
    else
        echo -e "${RED}❌ Knowledge Fusion template not found at $PROJECT_ROOT/knowledge-fusion-template${NC}"
        echo -e "${YELLOW}Creating basic Knowledge Fusion structure...${NC}"
        mkdir -p "$KNOWLEDGE_FUSION_PATH"
        # Create minimal required files - this will be expanded in future iterations
        echo "# Knowledge Fusion will be fully installed in next update" > "$KNOWLEDGE_FUSION_PATH/README.md"
    fi
fi

echo -e "${GREEN}✅ All required directories found${NC}"

# Smart Core Backend dependency installation
echo -e "\n${BLUE}🔄 Checking Core Backend dependencies...${NC}"
CORE_BACKEND_REQUIREMENTS="$CORE_BACKEND_PATH/implementation/backend/requirements.txt"

if [ -f "$CORE_BACKEND_REQUIREMENTS" ]; then
    # Create a filtered requirements file that avoids conflicts
    TEMP_REQUIREMENTS=$(mktemp)
    
    echo "# Smart Core Backend Dependencies - avoiding conflicts with OpenWebUI" > "$TEMP_REQUIREMENTS"
    echo "# Generated automatically by start_server_mode.sh" >> "$TEMP_REQUIREMENTS"
    echo "" >> "$TEMP_REQUIREMENTS"
    
    # Essential packages that don't conflict (use current versions)
    cat >> "$TEMP_REQUIREMENTS" << 'EOF'
# Data processing (compatible versions)
python-dateutil>=2.8.2
python-multipart>=0.0.6

# Web framework essentials (required for Core Backend and Knowledge Fusion)
fastapi>=0.104.1
uvicorn[standard]>=0.24.0

# AI/ML dependencies (use compatible versions to avoid build issues)
# Note: tiktoken installed separately to handle version compatibility
sentence-transformers>=2.2.2
transformers>=4.35.2

# Compatible huggingface_hub version for sentence-transformers
huggingface_hub<0.20

# Development and testing
requests>=2.31.0
httpx>=0.25.2
aiohttp>=3.9.1

# Utilities
python-dotenv>=1.0.0
python-jose>=3.3.0
passlib>=1.7.4
EOF

    echo "Installing compatible Core Backend dependencies..."
    if pip install -r "$TEMP_REQUIREMENTS" --quiet; then
        echo -e "${GREEN}✅ Core Backend dependencies installed (conflict-safe)${NC}"
    else
        echo -e "${YELLOW}⚠️  Some Core Backend dependencies may need manual installation${NC}"
        echo "You can manually install missing packages if needed"
    fi
    
    # Cleanup
    rm "$TEMP_REQUIREMENTS"
    
    # Check for essential missing packages with compatibility fixes
    echo "Checking for essential missing packages..."
    missing_packages=()
    
    # Check for tiktoken (critical for AI functionality) - use compatible version
    if ! python -c "import tiktoken" 2>/dev/null; then
        echo -e "${YELLOW}Installing tiktoken (latest compatible version)...${NC}"
        # Use latest version that has pre-built wheels to avoid Rust compilation issues
        pip install tiktoken --no-cache-dir --quiet || {
            echo -e "${YELLOW}⚠️  tiktoken installation failed - may need manual installation${NC}"
        }
    fi
    
    # Check for sentence-transformers (critical for AI functionality)
    if ! python -c "import sentence_transformers" 2>/dev/null; then
        echo -e "${YELLOW}Installing sentence-transformers with compatible dependencies...${NC}"
        # Install compatible huggingface_hub first to avoid import errors
        pip install "huggingface_hub<0.20" --quiet 2>/dev/null
        missing_packages+=("sentence-transformers==2.2.2")
    else
        # Check if sentence-transformers can import (compatibility issue check)
        if ! python -c "import sentence_transformers; print('OK')" 2>/dev/null | grep -q "OK"; then
            echo -e "${YELLOW}Fixing sentence-transformers compatibility issues...${NC}"
            pip install "huggingface_hub<0.20" --force-reinstall --quiet 2>/dev/null
        fi
    fi
    
    # Check for python-multipart (needed for file uploads)
    if ! python -c "import python_multipart" 2>/dev/null; then
        missing_packages+=("python-multipart")
    fi
    
    # Check for uvicorn (needed for FastAPI)
    if ! python -c "import uvicorn" 2>/dev/null; then
        missing_packages+=("uvicorn[standard]")
    fi
    
    # Check for FastAPI (needed for Core Backend)
    if ! python -c "import fastapi" 2>/dev/null; then
        missing_packages+=("fastapi")
    fi
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo -e "${YELLOW}Installing critical missing packages: ${missing_packages[*]}${NC}"
        pip install "${missing_packages[@]}" --quiet || {
            echo -e "${YELLOW}⚠️  Some critical packages couldn't be installed automatically${NC}"
        }
    fi
    
    # Final compatibility check
    echo "Performing final compatibility checks..."
    
    # Test Core Backend imports
    if python -c "
import tiktoken, fastapi, uvicorn
try:
    import sentence_transformers
    print('✅ All Core Backend dependencies verified')
except ImportError as e:
    print(f'⚠️  Dependency issue: {e}')
    exit(1)
" 2>/dev/null; then
        echo -e "${GREEN}✅ All Core Backend dependencies are working properly${NC}"
    else
        echo -e "${YELLOW}⚠️  Some Core Backend dependencies may have issues${NC}"
        echo "The platform will still try to start, but some features may not work"
    fi
    
else
    echo -e "${YELLOW}⚠️  Core Backend requirements.txt not found${NC}"
fi

echo -e "${GREEN}✅ Core Backend dependency check completed${NC}"

# =============================================================================
# 2. VERIFY OLLAMA
# =============================================================================
echo -e "\n${BLUE}🔍 Step 2: Verifying Ollama${NC}"

if ! command -v ollama >/dev/null 2>&1; then
    echo -e "${RED}❌ Ollama not found. Please install Ollama first.${NC}"
    echo "Visit: https://ollama.ai"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:$OLLAMA_PORT >/dev/null 2>&1; then
    echo "🔄 Starting Ollama..."
    ollama serve &
    sleep 5
    
    if ! wait_for_service "http://localhost:$OLLAMA_PORT" "Ollama"; then
        echo -e "${RED}❌ Failed to start Ollama${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Ollama is already running${NC}"
fi

# List available models
echo "📋 Available Ollama models:"
ollama list

# =============================================================================
# 3. START CORE BACKEND
# =============================================================================
echo -e "\n${BLUE}🔍 Step 3: Starting Core Backend${NC}"

# Check if core backend has the right structure
if [ -f "$CORE_BACKEND_PATH/implementation/backend/main.py" ]; then
    CORE_BACKEND_MAIN="$CORE_BACKEND_PATH/implementation/backend/main.py"
elif [ -f "$CORE_BACKEND_PATH/qwenroute/implementation/main.py" ]; then
    CORE_BACKEND_MAIN="$CORE_BACKEND_PATH/qwenroute/implementation/main.py"
elif [ -f "$CORE_BACKEND_PATH/main.py" ]; then
    CORE_BACKEND_MAIN="$CORE_BACKEND_PATH/main.py"
else
    echo -e "${RED}❌ Core backend main.py not found${NC}"
    echo -e "${RED}   Looking in:${NC}"
    echo -e "${RED}   - $CORE_BACKEND_PATH/implementation/backend/main.py${NC}"
    echo -e "${RED}   - $CORE_BACKEND_PATH/qwenroute/implementation/main.py${NC}"
    echo -e "${RED}   - $CORE_BACKEND_PATH/main.py${NC}"
    exit 1
fi

start_service "Core Backend" \
    "python -m uvicorn main:app --host 0.0.0.0 --port $CORE_BACKEND_PORT" \
    "$(dirname "$CORE_BACKEND_MAIN")" \
    $CORE_BACKEND_PORT

if ! wait_for_service "http://localhost:$CORE_BACKEND_PORT/health" "Core Backend"; then
    echo -e "${RED}❌ Core Backend failed to start${NC}"
    cleanup
    exit 1
fi

# =============================================================================
# 4. RUN KNOWLEDGE FUSION INTEGRATION
# =============================================================================
echo -e "\n${BLUE}🔍 Step 4: Starting Knowledge Fusion Services${NC}"

# Run the batch knowledge fusion integration first
echo "🔄 Running Knowledge Fusion integration..."
cd "$KNOWLEDGE_FUSION_PATH"

# Run Knowledge Fusion as a batch job (it processes and exits)
if "$VENV_PATH/bin/python" run_knowledge_fusion.py; then
    echo -e "${GREEN}✅ Knowledge Fusion integration completed successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Knowledge Fusion integration encountered issues, but continuing...${NC}"
fi

# Start the Knowledge Fusion web server
echo "🔄 Starting Knowledge Fusion web server..."

# Verify uvicorn and FastAPI are available (required for Knowledge Fusion server)
uvicorn_available=true
if ! "$VENV_PATH/bin/python" -c "import uvicorn, fastapi" 2>/dev/null; then
    echo -e "  ${YELLOW}⚠️  uvicorn or FastAPI not available, installing for Knowledge Fusion...${NC}"
    if "$VENV_PATH/bin/pip" install uvicorn fastapi --quiet; then
        echo -e "  ${GREEN}✅ uvicorn and FastAPI installed successfully${NC}"
    else
        echo -e "  ${RED}❌ Failed to install uvicorn/FastAPI for Knowledge Fusion${NC}"
        echo -e "  ${YELLOW}⚠️  Skipping Knowledge Fusion web server${NC}"
        uvicorn_available=false
    fi
fi

if [ "$uvicorn_available" = true ]; then
    nohup "$VENV_PATH/bin/python" start_server.py > "$PROJECT_ROOT/logs/knowledge_fusion.log" 2>&1 &
    KNOWLEDGE_PID=$!
    echo "KnowledgeFusion $KNOWLEDGE_PID" >> "$PID_FILE"
    echo -e "  Started Knowledge Fusion web server with PID: $KNOWLEDGE_PID"

    # Wait for Knowledge Fusion to be ready
    echo "  Waiting for Knowledge Fusion to be ready..."
    wait_for_service "http://localhost:8002/docs" "Knowledge Fusion" 90

    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✅ Knowledge Fusion web server is ready${NC}"
    else
        echo -e "  ${RED}❌ Knowledge Fusion web server failed to start within 180 seconds${NC}"
        echo -e "  ${YELLOW}⚠️  Continuing without Knowledge Fusion web server${NC}"
    fi
fi
KNOWLEDGE_PID=$!
echo "KnowledgeFusion $KNOWLEDGE_PID" >> "$PID_FILE"
echo -e "  Started Knowledge Fusion web server with PID: $KNOWLEDGE_PID"

# Wait for Knowledge Fusion to be ready
echo "  Waiting for Knowledge Fusion to be ready..."
wait_for_service "http://localhost:8002/docs" "Knowledge Fusion" 90

if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✅ Knowledge Fusion web server is ready${NC}"
else
    echo -e "  ${RED}❌ Knowledge Fusion web server failed to start within 120 seconds${NC}"
    echo -e "  ${YELLOW}⚠️  Continuing without Knowledge Fusion web server${NC}"
fi

cd "$PROJECT_ROOT"

# =============================================================================
# 5. SETUP AND START OPENWEBUI
# =============================================================================
echo -e "\n${BLUE}🔍 Step 5: Setup and Start OpenWebUI${NC}"

# Ensure OpenWebUI clone is properly installed
echo "🔄 Ensuring OpenWebUI is properly installed..."
cd "$OPENWEBUI_PATH"
source "$VENV_PATH/bin/activate"

# Check if open-webui command is available, if not install it
if ! command -v open-webui >/dev/null 2>&1; then
    echo "🔄 Installing OpenWebUI in development mode..."
    pip install -e . --quiet || {
        echo -e "${RED}❌ Failed to install OpenWebUI${NC}"
        exit 1
    }
    echo -e "${GREEN}✅ OpenWebUI installed successfully${NC}"
else
    echo -e "${GREEN}✅ OpenWebUI is already installed${NC}"
fi

# Configure ChromaDB environment (minimal for 0.6.3 compatibility)
echo "🔄 Configuring ChromaDB environment..."
export VECTOR_DB="chroma"
mkdir -p "$PROJECT_ROOT/data/chromadb"
echo "✅ ChromaDB environment configured for compatibility"

# Start OpenWebUI using the proper command from project root
echo "🔄 Starting OpenWebUI..."
cd "$PROJECT_ROOT"

# Ensure we're using the correct Python path
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Start OpenWebUI with the installed executable - use proper working directory
nohup "$VENV_PATH/bin/open-webui" serve --host 0.0.0.0 --port $OPENWEBUI_PORT > "$PROJECT_ROOT/logs/openwebui.log" 2>&1 &
OPENWEBUI_PID=$!
echo "OpenWebUI $OPENWEBUI_PID" >> "$PID_FILE"
echo "  Started OpenWebUI with PID: $OPENWEBUI_PID"

if ! wait_for_service "http://localhost:$OPENWEBUI_PORT" "OpenWebUI" 90; then
    echo -e "${RED}❌ OpenWebUI failed to start${NC}"
    cleanup
    exit 1
fi

# =============================================================================
# 6. RUN HEALTH CHECKS
# =============================================================================
echo -e "\n${BLUE}🔍 Step 6: Running Health Checks${NC}"

services=(
    "Ollama:http://localhost:$OLLAMA_PORT"
    "Core Backend:http://localhost:$CORE_BACKEND_PORT/health"
    "OpenWebUI:http://localhost:$OPENWEBUI_PORT"
    "Knowledge Fusion:http://localhost:8002/docs"
)

all_healthy=true
for service_info in "${services[@]}"; do
    IFS=':' read -r name url <<< "$service_info"
    if curl -s "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $name: HEALTHY${NC}"
    else
        echo -e "${RED}❌ $name: UNHEALTHY${NC}"
        all_healthy=false
    fi
done

# =============================================================================
# 7. DISPLAY STATUS AND ACCESS INFORMATION
# =============================================================================
echo -e "\n${BLUE}🎉 TOPOLOGY KNOWLEDGE - SERVER MODE READY${NC}"
echo -e "${BLUE}===========================================${NC}"

if [ "$all_healthy" = true ]; then
    echo -e "${GREEN}✅ All services are running and healthy!${NC}"
else
    echo -e "${YELLOW}⚠️  Some services may not be fully operational${NC}"
fi

echo ""
echo -e "${GREEN}📱 Access Points:${NC}"
echo "  🌐 OpenWebUI:           http://localhost:$OPENWEBUI_PORT"
echo "  🔧 Core Backend API:    http://localhost:$CORE_BACKEND_PORT"
echo "  🧠 Knowledge Fusion:    http://localhost:$KNOWLEDGE_FUSION_PORT"
echo "  🤖 Ollama API:          http://localhost:$OLLAMA_PORT"
echo ""
echo -e "${GREEN}📚 Documentation:${NC}"
echo "  📖 API Reference:       docs/QWENROUTE_API_DOCUMENTATION.md"
echo "  🔧 Setup Guide:         OPENWEBUI_SUCCESS.md"
echo ""
echo -e "${GREEN}🎯 Next Steps:${NC}"
echo "  1. Open http://localhost:$OPENWEBUI_PORT in your browser"
echo "  2. Create your admin account (first time only)"
echo "  3. Go to Settings → Functions → Enable 'IBM Knowledge Fusion'"
echo "  4. Start chatting with enhanced AI capabilities!"
echo ""
echo -e "${YELLOW}💡 To stop all services: Press Ctrl+C${NC}"

# Keep the script running and monitor services
echo -e "\n${BLUE}🔍 Monitoring services... (Press Ctrl+C to stop)${NC}"
while true; do
    sleep 30
    
    # Quick health check
    failed_services=()
    for service_info in "${services[@]}"; do
        IFS=':' read -r name url <<< "$service_info"
        if ! curl -s "$url" >/dev/null 2>&1; then
            failed_services+=("$name")
        fi
    done
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        echo -e "${RED}⚠️  Health check failed for: ${failed_services[*]}${NC}"
    fi
done
