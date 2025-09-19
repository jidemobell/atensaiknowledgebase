#!/bin/bash

# =============================================================================
# TOPOLOGY KNOWLEDGE - UNIFIED SERVER MODE STARTUP
# =============================================================================
# This script starts the Knowledge Fusion platform services:
# 1. Core Backend (port 8001) 
# 2. Knowledge Fusion Backend (port 8002)
# 3. Knowledge Fusion Gateway (port 9000)
# 4. Checks for OpenWebUI (external service)
# 5. Runs health checks and confirms all systems are operational
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORE_BACKEND_PATH="$PROJECT_ROOT/corebackend"
KNOWLEDGE_FUSION_TEMPLATE_PATH="$PROJECT_ROOT/knowledge-fusion-template"

# Ports configuration
CORE_BACKEND_PORT=8001
KNOWLEDGE_FUSION_PORT=8002
KNOWLEDGE_FUSION_GATEWAY_PORT=9000
OPENWEBUI_PORT=8080  # Default OpenWebUI port (user configurable)
OLLAMA_PORT=11434    # Default Ollama port

# PID file for tracking processes
PID_FILE="$PROJECT_ROOT/.topology_pids"

# Create necessary directories
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/data/chromadb"

echo -e "${BLUE}🚀 KNOWLEDGE FUSION PLATFORM - SERVER MODE STARTUP${NC}"
echo -e "${BLUE}=================================================${NC}"
echo "📁 Project Root: $PROJECT_ROOT"
echo "🔧 Core Backend: $CORE_BACKEND_PATH"
echo "🧠 Knowledge Fusion: $KNOWLEDGE_FUSION_TEMPLATE_PATH"
echo "🌐 OpenWebUI: External service (check port $OPENWEBUI_PORT)"
echo ""

# Pre-flight checks
echo "🔍 Running pre-flight checks..."

# Check if Knowledge Fusion template exists
if [ ! -d "$KNOWLEDGE_FUSION_TEMPLATE_PATH" ]; then
    echo -e "${RED}❌ Knowledge Fusion template not found: $KNOWLEDGE_FUSION_TEMPLATE_PATH${NC}"
    echo "💡 Please run: ./setup.sh"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check for OpenWebUI (but don't require it to be running yet)
echo "🔍 Checking for OpenWebUI availability..."
if check_port $OPENWEBUI_PORT; then
    echo -e "${GREEN}✅ OpenWebUI detected on port $OPENWEBUI_PORT${NC}"
    OPENWEBUI_RUNNING=true
else
    echo -e "${YELLOW}⚠️  OpenWebUI not detected on port $OPENWEBUI_PORT${NC}"
    echo "💡 Please ensure OpenWebUI is running before integrating"
    OPENWEBUI_RUNNING=false
fi

echo -e "${GREEN}✅ Pre-flight checks completed${NC}"

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

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=${3:-30}  # Default to 30 attempts if not specified
    local attempt=1
    
    echo "  Waiting for $service_name to be ready (timeout: $((max_attempts * 2)) seconds)..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "\n  ${GREEN}✅ $service_name is ready (took $((attempt * 2)) seconds)${NC}"
            return 0
        fi
        
        # Show progress every 30 seconds for long waits
        if [ $((attempt % 15)) -eq 0 ] && [ $attempt -gt 15 ]; then
            echo -e "\n  ⏳ Still waiting for $service_name... (${attempt}/${max_attempts} attempts, $((attempt * 2))s elapsed)"
            echo -n "    "
        else
            echo -n "."
        fi
        
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
    
    # Start the service with system Python
    cd "$working_dir"
    
    # Use system Python
    local python_cmd="python3"
    
    # Replace 'python' in the command with python3
    local updated_command="${command//python /$python_cmd }"
    
    eval "$updated_command" &
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

# Check if Python is available
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "Please install Python 3 first."
    exit 1
fi

# Check Python version
python_version=$(python3 --version)
echo -e "${GREEN}✅ Using $python_version${NC}"

# Check core directories
if [ ! -d "$CORE_BACKEND_PATH" ]; then
    echo -e "${RED}❌ Required directory not found: $CORE_BACKEND_PATH${NC}"
    exit 1
fi

# Knowledge Fusion template should already exist (verified in pre-flight checks)
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

# Check if Ollama is running first (more important than command availability)
if curl -s http://localhost:$OLLAMA_PORT >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama is running and accessible on port $OLLAMA_PORT${NC}"
elif command -v ollama >/dev/null 2>&1; then
    echo "🔄 Starting Ollama..."
    ollama serve &
    sleep 5
    
    if ! wait_for_service "http://localhost:$OLLAMA_PORT" "Ollama"; then
        echo -e "${RED}❌ Failed to start Ollama${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Ollama command not found, but checking for running instance...${NC}"
    if curl -s http://localhost:$OLLAMA_PORT >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama is running (external service detected)${NC}"
    else
        echo -e "${RED}❌ Ollama not found and not running. Please install Ollama first.${NC}"
        echo "Visit: https://ollama.ai"
        exit 1
    fi
fi

# =============================================================================
# MAIN SERVICE STARTUP SEQUENCE
# =============================================================================

echo -e "\n${BLUE}🔍 Step 1: Starting Core Backend${NC}"

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

echo -e "\n${BLUE}🔍 Step 2: Starting Knowledge Fusion Backend${NC}"

start_service "Knowledge Fusion Backend" \
    "python start_server.py" \
    "$KNOWLEDGE_FUSION_TEMPLATE_PATH" \
    $KNOWLEDGE_FUSION_PORT

if ! wait_for_service "http://localhost:$KNOWLEDGE_FUSION_PORT/health" "Knowledge Fusion Backend"; then
    echo -e "${RED}❌ Knowledge Fusion Backend failed to start${NC}"
    cleanup
    exit 1
fi

echo -e "\n${BLUE}🔍 Step 3: Starting Knowledge Fusion Gateway${NC}"

# Start the Knowledge Fusion Gateway
start_service "Knowledge Fusion Gateway" \
    "python knowledge_fusion_gateway.py" \
    "$PROJECT_ROOT" \
    $KNOWLEDGE_FUSION_GATEWAY_PORT

if ! wait_for_service "http://localhost:$KNOWLEDGE_FUSION_GATEWAY_PORT/health" "Knowledge Fusion Gateway"; then
    echo -e "${RED}❌ Knowledge Fusion Gateway failed to start${NC}"
    cleanup
    exit 1
fi

echo -e "\n${BLUE}🔍 Step 4: Checking OpenWebUI Status${NC}"

if [ "$OPENWEBUI_RUNNING" = true ]; then
    echo -e "${GREEN}✅ OpenWebUI is already running on port $OPENWEBUI_PORT${NC}"
    echo -e "${BLUE}💡 Next Step: Upload the pipe function to OpenWebUI${NC}"
    echo -e "   1. Copy the function code: ${YELLOW}cat knowledge_fusion_function.py${NC}"
    echo -e "   2. Go to OpenWebUI → Admin Panel → Functions"
    echo -e "   3. Click '+' to add new function"
    echo -e "   4. Paste the code and save"
    echo -e "   5. Enable the function"
else
    echo -e "${YELLOW}⚠️  OpenWebUI not detected on port $OPENWEBUI_PORT${NC}"
    echo -e "${BLUE}💡 Please start OpenWebUI before proceeding with integration:${NC}"
    echo -e "   ${YELLOW}open-webui serve --port $OPENWEBUI_PORT${NC}"
    echo -e "   Or check if it's running on a different port"
fi

# =============================================================================
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
# 5. CHECK EXTERNAL OPENWEBUI
# =============================================================================
echo -e "\n${BLUE}🔍 Step 5: Check External OpenWebUI${NC}"

# Check if OpenWebUI is running externally (we no longer install it)
echo "🔍 Checking for external OpenWebUI installation..."
if curl -s "http://localhost:$OPENWEBUI_PORT" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ External OpenWebUI detected at http://localhost:$OPENWEBUI_PORT${NC}"
    EXTERNAL_OPENWEBUI=true
else
    echo -e "${YELLOW}⚠️  No external OpenWebUI detected${NC}"
    echo "🔧 Please install and start OpenWebUI separately:"
    echo "   pip install open-webui"
    echo "   open-webui serve --port $OPENWEBUI_PORT"
    echo ""
    echo "💡 The Knowledge Fusion backend services will start anyway"
    echo "   You can integrate with OpenWebUI later by uploading the function"
    EXTERNAL_OPENWEBUI=false
fi

# Configure ChromaDB environment (minimal for 0.6.3 compatibility)
echo "🔄 Configuring ChromaDB environment..."
export VECTOR_DB="chroma"
mkdir -p "$PROJECT_ROOT/data/chromadb"
echo "✅ ChromaDB environment configured for compatibility"

# Only start Knowledge Fusion services (OpenWebUI should be external)
echo "🔄 Knowledge Fusion services are ready for integration..."

# Skip OpenWebUI startup - it should be running externally
if [ "$EXTERNAL_OPENWEBUI" = true ]; then
    echo -e "${GREEN}✅ Using external OpenWebUI at http://localhost:$OPENWEBUI_PORT${NC}"
else
    echo -e "${YELLOW}⚠️  OpenWebUI not detected - services ready for when you start it${NC}"
fi

# =============================================================================
# 6. RUN HEALTH CHECKS
# =============================================================================
echo -e "\n${BLUE}🔍 Step 6: Running Health Checks${NC}"

# Build services list based on what should be running
services=(
    "Ollama:http://localhost:$OLLAMA_PORT"
    "Core Backend:http://localhost:$CORE_BACKEND_PORT/health"
    "Knowledge Fusion:http://localhost:8002/docs"
)

# Only check OpenWebUI if it was detected as external
if [ "$EXTERNAL_OPENWEBUI" = true ]; then
    services+=("OpenWebUI:http://localhost:$OPENWEBUI_PORT")
fi

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
echo -e "\n${BLUE}🎉 IBM KNOWLEDGE FUSION PLATFORM - READY${NC}"
echo -e "${BLUE}=========================================${NC}"

if [ "$all_healthy" = true ]; then
    echo -e "${GREEN}✅ All Knowledge Fusion services are running and healthy!${NC}"
else
    echo -e "${YELLOW}⚠️  Some services may not be fully operational${NC}"
fi

echo ""
echo -e "${GREEN}📱 Knowledge Fusion Services:${NC}"
echo "  🔧 Core Backend API:    http://localhost:$CORE_BACKEND_PORT"
echo "  🧠 Knowledge Fusion:    http://localhost:$KNOWLEDGE_FUSION_PORT"
echo "  🤖 Ollama API:          http://localhost:$OLLAMA_PORT"

if [ "$EXTERNAL_OPENWEBUI" = true ]; then
    echo "  🌐 External OpenWebUI:  http://localhost:$OPENWEBUI_PORT"
else
    echo "  ⚠️  OpenWebUI: Not detected (install separately)"
fi

echo ""
echo -e "${GREEN}📚 Documentation:${NC}"
echo "  📖 Integration Guide:   docs/INTEGRATION_FLOW.md"
echo "  � Quick Start:         docs/STARTUP_GUIDE.md"
echo "  🏗️  Architecture:        docs/KNOWLEDGE_FUSION_ARCHITECTURE.md"
echo ""
echo -e "${GREEN}🎯 Next Steps:${NC}"
if [ "$EXTERNAL_OPENWEBUI" = true ]; then
    echo "  1. Open http://localhost:$OPENWEBUI_PORT in your browser"
    echo "  2. Go to Admin Panel → Functions"
    echo "  3. Upload knowledge_fusion_function.py"
    echo "  4. Enable the 'IBM Knowledge Fusion' function"
    echo "  5. Start chatting with enhanced AI capabilities!"
else
    echo "  1. Install OpenWebUI: pip install open-webui"
    echo "  2. Start OpenWebUI: open-webui serve --port $OPENWEBUI_PORT"
    echo "  3. Upload knowledge_fusion_function.py to Functions"
    echo "  4. Enable integration and start chatting!"
fi
echo ""
echo -e "${YELLOW}💡 To stop services: Press Ctrl+C${NC}"

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
