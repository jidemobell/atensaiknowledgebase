#!/bin/bash

# =============================================================================
# TOPOLOGY KNOWLEDGE - UNIFIED DOCKER MODE STARTUP
# =============================================================================
# This script handles everything needed for Docker mode:
# 1. Builds OpenWebUI with integrated Knowledge Fusion
# 2. Starts Core Backend in Docker
# 3. Verifies Ollama is running locally
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
DOCKER_PATH="$PROJECT_ROOT/docker"
CORE_BACKEND_PATH="$PROJECT_ROOT/corebackend"
OPENWEBUI_PATH="$PROJECT_ROOT/openwebuibase"
KNOWLEDGE_FUSION_PATH="$OPENWEBUI_PATH/knowledge-fusion"

# Ports configuration
CORE_BACKEND_PORT=8001
KNOWLEDGE_FUSION_PORT=8002
OPENWEBUI_PORT=3000
OLLAMA_PORT=11434

# Container runtime detection and configuration
CONTAINER_RUNTIME=""
COMPOSE_COMMAND=""
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.knowledge-fusion.yml"
DOCKER_NETWORK="topology-network"

# Detect container runtime (Docker or Podman)
detect_container_runtime() {
    if command -v podman >/dev/null 2>&1 && podman info >/dev/null 2>&1; then
        CONTAINER_RUNTIME="podman"
        # Check for podman-compose or docker-compose
        if command -v podman-compose >/dev/null 2>&1; then
            COMPOSE_COMMAND="podman-compose"
        elif command -v docker-compose >/dev/null 2>&1; then
            COMPOSE_COMMAND="docker-compose"
        else
            echo -e "${YELLOW}⚠️  No compose tool found for Podman. Installing podman-compose...${NC}"
            pip3 install podman-compose 2>/dev/null || {
                echo -e "${RED}❌ Failed to install podman-compose. Please install it manually.${NC}"
                return 1
            }
            COMPOSE_COMMAND="podman-compose"
        fi
        return 0
    elif command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        CONTAINER_RUNTIME="docker"
        COMPOSE_COMMAND="docker-compose"
        return 0
    else
        return 1
    fi
}

echo -e "${BLUE}🐳 TOPOLOGY KNOWLEDGE - CONTAINERIZED MODE STARTUP${NC}"
echo -e "${BLUE}===============================================${NC}"
echo "📁 Project Root: $PROJECT_ROOT"
echo "🐳 Compose File: $DOCKER_COMPOSE_FILE"
echo "🔧 Core Backend: $CORE_BACKEND_PATH"
echo "🌐 OpenWebUI: $OPENWEBUI_PATH"
echo "🧠 Knowledge Fusion: $KNOWLEDGE_FUSION_PATH"
echo ""

# Detect container runtime first
echo -e "${BLUE}🔍 Detecting Container Runtime...${NC}"
if detect_container_runtime; then
    echo -e "${GREEN}✅ Using $CONTAINER_RUNTIME with $COMPOSE_COMMAND${NC}"
else
    echo -e "${RED}❌ No container runtime found. Please install Docker or Podman.${NC}"
    echo ""
    echo -e "${YELLOW}For Docker: Visit https://docker.com${NC}"
    echo -e "${YELLOW}For Podman: Visit https://podman.io${NC}"
    exit 1
fi
echo ""

# Cleanup function for graceful shutdown
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down container services...${NC}"
    cd "$PROJECT_ROOT"
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        $COMPOSE_COMMAND -f "$DOCKER_COMPOSE_FILE" down --remove-orphans
    fi
    echo -e "${GREEN}✅ Container cleanup complete${NC}"
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
    local max_attempts=30
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
    
    echo -e "\n  ${RED}❌ $service_name failed to start within 60 seconds${NC}"
    return 1
}

# =============================================================================
# 1. VERIFY ENVIRONMENT
# =============================================================================
echo -e "${BLUE}🔍 Step 1: Verifying Environment${NC}"

# Container runtime already detected above
echo -e "${GREEN}✅ $CONTAINER_RUNTIME is available and running${NC}"
echo -e "${GREEN}✅ $COMPOSE_COMMAND is available${NC}"

# Check core directories
for dir in "$CORE_BACKEND_PATH" "$OPENWEBUI_PATH" "$KNOWLEDGE_FUSION_PATH"; do
    if [ ! -d "$dir" ]; then
        echo -e "${RED}❌ Required directory not found: $dir${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ All required directories found${NC}"

# =============================================================================
# 2. VERIFY OLLAMA (LOCAL)
# =============================================================================
echo -e "\n${BLUE}🔍 Step 2: Verifying Local Ollama${NC}"

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
# 3. CREATE/UPDATE DOCKER COMPOSE FILE
# =============================================================================
echo -e "\n${BLUE}🔍 Step 3: Creating Docker Compose Configuration${NC}"

cat > "$DOCKER_COMPOSE_FILE" << 'EOF'
version: '3.8'

networks:
  topology-network:
    external: false

services:
  # Core Backend (formerly QwenRoute)
  core-backend:
    build:
      context: ./corebackend
      dockerfile: Dockerfile
    container_name: topology-core-backend
    ports:
      - "8001:8001"
    environment:
      - HOST=0.0.0.0
      - PORT=8001
      - OLLAMA_API_BASE_URL=http://host.docker.internal:11434
    volumes:
      - ./corebackend:/app
      - ./txts:/app/txts
      - ./knowledge_base.json:/app/knowledge_base.json
    networks:
      - topology-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    extra_hosts:
      - "host.docker.internal:host-gateway"

  # Knowledge Fusion Backend
  knowledge-fusion:
    build:
      context: ./openwebuibase/knowledge-fusion
      dockerfile: Dockerfile
    container_name: topology-knowledge-fusion
    ports:
      - "8002:8002"
    environment:
      - HOST=0.0.0.0
      - PORT=8002
      - OLLAMA_API_BASE_URL=http://host.docker.internal:11434
      - CORE_BACKEND_URL=http://core-backend:8001
    volumes:
      - ./openwebuibase/knowledge-fusion:/app
      - ./github_sources.yml:/app/config/github_sources.yml
    networks:
      - topology-network
    depends_on:
      - core-backend
    restart: unless-stopped
    extra_hosts:
      - "host.docker.internal:host-gateway"

  # OpenWebUI with Knowledge Fusion Integration
  openwebui:
    build:
      context: ./openwebuibase
      dockerfile: Dockerfile
      args:
        - KNOWLEDGE_FUSION_ENABLED=true
    container_name: topology-openwebui
    ports:
      - "3000:8080"
    environment:
      - WEBUI_SECRET_KEY=your-secret-key-here
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - ENABLE_OLLAMA_API=true
      - ENABLE_OPENAI_API=false
      - CORS_ALLOW_ORIGIN=*
      - ANONYMIZED_TELEMETRY=false
      - KNOWLEDGE_FUSION_URL=http://knowledge-fusion:8002
      - CORE_BACKEND_URL=http://core-backend:8001
    volumes:
      - ./openwebuibase:/app/backend/data
      - ./openwebuibase/knowledge-fusion/functions:/app/backend/data/functions
    networks:
      - topology-network
    depends_on:
      - core-backend
      - knowledge-fusion
    restart: unless-stopped
    extra_hosts:
      - "host.docker.internal:host-gateway"
EOF

echo -e "${GREEN}✅ Docker Compose file created${NC}"

# =============================================================================
# 4. CREATE DOCKERFILES IF NEEDED
# =============================================================================
echo -e "\n${BLUE}🔍 Step 4: Setting up Dockerfiles${NC}"

# Core Backend Dockerfile
if [ ! -f "$CORE_BACKEND_PATH/Dockerfile" ]; then
    cat > "$CORE_BACKEND_PATH/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Start the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
EOF
    echo -e "${GREEN}✅ Created Core Backend Dockerfile${NC}"
fi

# Knowledge Fusion Dockerfile
if [ ! -f "$KNOWLEDGE_FUSION_PATH/Dockerfile" ]; then
    cat > "$KNOWLEDGE_FUSION_PATH/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8002

# Start the application
CMD ["python", "run_knowledge_fusion.py"]
EOF
    echo -e "${GREEN}✅ Created Knowledge Fusion Dockerfile${NC}"
fi

# =============================================================================
# 5. BUILD AND START DOCKER SERVICES
# =============================================================================
echo -e "\n${BLUE}🔍 Step 5: Building and Starting Docker Services${NC}"

cd "$PROJECT_ROOT"

# Stop any existing services
echo "🛑 Stopping existing services..."
$COMPOSE_COMMAND -f "$DOCKER_COMPOSE_FILE" down --remove-orphans 2>/dev/null || true

# Build images
echo "🔨 Building container images..."
$COMPOSE_COMMAND -f "$DOCKER_COMPOSE_FILE" build --no-cache

# Start services
echo "🚀 Starting container services..."
$COMPOSE_COMMAND -f "$DOCKER_COMPOSE_FILE" up -d

# =============================================================================
# 6. WAIT FOR SERVICES TO BE READY
# =============================================================================
echo -e "\n${BLUE}🔍 Step 6: Waiting for Services to be Ready${NC}"

services=(
    "Core Backend:http://localhost:$CORE_BACKEND_PORT/health"
    "Knowledge Fusion:http://localhost:$KNOWLEDGE_FUSION_PORT/health"
    "OpenWebUI:http://localhost:$OPENWEBUI_PORT"
)

all_ready=true
for service_info in "${services[@]}"; do
    IFS=':' read -r name url <<< "$service_info"
    if ! wait_for_service "$url" "$name"; then
        all_ready=false
    fi
done

# =============================================================================
# 7. RUN HEALTH CHECKS
# =============================================================================
echo -e "\n${BLUE}🔍 Step 7: Running Health Checks${NC}"

# Check container status
echo "📋 Container Status:"
$COMPOSE_COMMAND -f "$DOCKER_COMPOSE_FILE" ps

# Check service endpoints
health_services=(
    "Ollama (Local):http://localhost:$OLLAMA_PORT"
    "Core Backend:http://localhost:$CORE_BACKEND_PORT/health"
    "Knowledge Fusion:http://localhost:$KNOWLEDGE_FUSION_PORT/health"
    "OpenWebUI:http://localhost:$OPENWEBUI_PORT"
)

all_healthy=true
for service_info in "${health_services[@]}"; do
    IFS=':' read -r name url <<< "$service_info"
    if curl -s "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $name: HEALTHY${NC}"
    else
        echo -e "${RED}❌ $name: UNHEALTHY${NC}"
        all_healthy=false
    fi
done

# =============================================================================
# 8. DISPLAY STATUS AND ACCESS INFORMATION
# =============================================================================
echo -e "\n${BLUE}🎉 TOPOLOGY KNOWLEDGE - DOCKER MODE READY${NC}"
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
echo "  🤖 Ollama API:          http://localhost:$OLLAMA_PORT (Local)"
echo ""
echo -e "${GREEN}🐳 Container Management:${NC}"
echo "  📋 View logs:           $COMPOSE_COMMAND -f $DOCKER_COMPOSE_FILE logs -f"
echo "  🛑 Stop services:       $COMPOSE_COMMAND -f $DOCKER_COMPOSE_FILE down"
echo "  🔄 Restart service:     $COMPOSE_COMMAND -f $DOCKER_COMPOSE_FILE restart <service>"
echo ""
echo -e "${GREEN}📚 Documentation:${NC}"
echo "  📖 API Reference:       docs/QWENROUTE_API_DOCUMENTATION.md"
echo "  🔧 Setup Guide:         OPENWEBUI_SUCCESS.md"
echo ""
echo -e "${GREEN}🎯 Next Steps:${NC}"
echo "  1. Open http://localhost:$OPENWEBUI_PORT in your browser"
echo "  2. Create your admin account (first time only)"
echo "  3. Knowledge Fusion should be automatically integrated"
echo "  4. Start chatting with enhanced AI capabilities!"
echo ""
echo -e "${YELLOW}💡 To stop all services: Run this script with --stop flag${NC}"
echo -e "${YELLOW}💡 To view logs: $COMPOSE_COMMAND -f $DOCKER_COMPOSE_FILE logs -f${NC}"

# Handle stop flag
if [ "$1" = "--stop" ]; then
    cleanup
    exit 0
fi

# Keep monitoring if not stopping
echo -e "\n${BLUE}🔍 Monitoring Docker services... (Press Ctrl+C to stop)${NC}"
while true; do
    sleep 30
    
    # Quick health check
    failed_services=()
    for service_info in "${health_services[@]}"; do
        IFS=':' read -r name url <<< "$service_info"
        if ! curl -s "$url" >/dev/null 2>&1; then
            failed_services+=("$name")
        fi
    done
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        echo -e "${RED}⚠️  Health check failed for: ${failed_services[*]}${NC}"
    fi
    
    # Check containers
    if ! $COMPOSE_COMMAND -f "$DOCKER_COMPOSE_FILE" ps --services --filter "status=running" | wc -l | grep -q "3"; then
        echo -e "${RED}⚠️  Some containers may have stopped${NC}"
        $COMPOSE_COMMAND -f "$DOCKER_COMPOSE_FILE" ps
    fi
done
