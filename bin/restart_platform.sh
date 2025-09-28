#!/bin/bash
# Complete Platform Restart Script
# Properly stops all services and restarts with AI integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Knowledge Fusion Platform - Complete Restart${NC}"
echo "=================================================="

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$PROJECT_ROOT/.topology_pids"

echo "📁 Project Root: $PROJECT_ROOT"

# Function to kill processes by port
kill_port() {
    local port=$1
    local service_name=$2
    
    echo "🔍 Checking port $port for $service_name..."
    
    # Find process using the port
    local pid=$(lsof -ti:$port 2>/dev/null || true)
    
    if [ -n "$pid" ]; then
        echo "  🛑 Stopping $service_name (PID: $pid) on port $port"
        kill -TERM $pid 2>/dev/null || true
        sleep 2
        
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            echo "  💀 Force stopping $service_name"
            kill -KILL $pid 2>/dev/null || true
        fi
        echo "  ✅ $service_name stopped"
    else
        echo "  ✅ Port $port is free"
    fi
}

# Stop all services
echo -e "\n${YELLOW}🛑 Step 1: Stopping All Services${NC}"

# Stop by port (more reliable than PID files)
kill_port 8001 "Core Backend"
kill_port 8002 "Knowledge Fusion Backend" 
kill_port 9000 "Knowledge Fusion Gateway"

# Clean up any remaining uvicorn processes
echo "🧹 Cleaning up remaining processes..."
pkill -f "main:app" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "knowledge_fusion" 2>/dev/null || true

# Remove PID file
rm -f "$PID_FILE"

sleep 3

# Check Ollama
echo -e "\n${BLUE}🔍 Step 2: Verifying Ollama${NC}"
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "✅ Ollama is running"
    
    # Check for required models
    echo "🔍 Checking required models..."
    if ! ollama list | grep -q "nomic-embed-text"; then
        echo "📥 Pulling nomic-embed-text (required for embeddings)..."
        ollama pull nomic-embed-text
    fi
    
    # Check for reasoning model
    if ollama list | grep -q "granite3.2:8b"; then
        echo "✅ Found Granite models"
    elif ollama list | grep -q "llama3.1:8b"; then
        echo "✅ Found Llama models"
    else
        echo "📥 Pulling llama3.1:8b for reasoning..."
        ollama pull llama3.1:8b
    fi
    
    echo "✅ All required models available"
else
    echo "❌ Ollama not running! Please start: ollama serve"
    exit 1
fi

# Install Python dependencies
echo -e "\n${BLUE}📦 Step 3: Installing Dependencies${NC}"
pip install sentence-transformers==2.2.2 numpy aiohttp fastapi uvicorn pydantic requests 2>/dev/null || echo "Dependencies already installed"

# Start Core Backend with AI
echo -e "\n${BLUE}🚀 Step 4: Starting Core Backend with AI${NC}"
cd "$PROJECT_ROOT/corebackend/implementation/backend"

# Ensure we have main.py (copy from main_enhanced.py if needed)
if [ ! -f "main.py" ] && [ -f "main_enhanced.py" ]; then
    echo "📝 Creating main.py from main_enhanced.py"
    cp main_enhanced.py main.py
fi

# Set environment variables for AI
export OLLAMA_BASE_URL="http://localhost:11434"
export ENABLE_EMBEDDINGS="true"
export AI_MODEL_CONFIG="$PROJECT_ROOT/config/ai_models_config.json"

# Start Core Backend
echo "🔄 Starting Core Backend with AI models..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
CORE_PID=$!
echo "core_backend $CORE_PID" >> "$PID_FILE"

# Wait for Core Backend
echo "⏳ Waiting for Core Backend..."
for i in {1..15}; do
    if curl -s http://localhost:8001/health >/dev/null 2>&1; then
        echo "✅ Core Backend is ready"
        break
    fi
    sleep 2
    echo -n "."
done

# Check if ML components are enabled
echo "🔍 Checking AI integration..."
HEALTH_RESPONSE=$(curl -s http://localhost:8001/health)
if echo "$HEALTH_RESPONSE" | grep -q '"ml_components":"disabled"'; then
    echo "⚠️  ML components still disabled - fixing..."
    # This means sentence-transformers isn't loading properly, restart once more
    kill $CORE_PID 2>/dev/null || true
    sleep 3
    python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
    CORE_PID=$!
    sleep 5
fi

# Start Knowledge Fusion Gateway
echo -e "\n${BLUE}🚀 Step 5: Starting Knowledge Fusion Gateway${NC}"
cd "$PROJECT_ROOT"
python3 knowledge_fusion_gateway.py &
GATEWAY_PID=$!
echo "gateway $GATEWAY_PID" >> "$PID_FILE"

# Wait for Gateway
echo "⏳ Waiting for Gateway..."
for i in {1..10}; do
    if curl -s http://localhost:9000/health >/dev/null 2>&1; then
        echo "✅ Gateway is ready"
        break
    fi
    sleep 2
    echo -n "."
done

# Check OpenWebUI
echo -e "\n${BLUE}🔍 Step 6: Checking OpenWebUI${NC}"
if curl -s http://localhost:8080/health >/dev/null 2>&1; then
    echo "✅ OpenWebUI is running"
else
    echo "⚠️  OpenWebUI not detected. Start it with:"
    echo "   open-webui serve --port 8080"
fi

# Final health check
echo -e "\n${GREEN}🎯 Final System Status:${NC}"
echo -n "Core Backend (8001): "
curl -s http://localhost:8001/health >/dev/null 2>&1 && echo "✅ Running" || echo "❌ Failed"

echo -n "Gateway (9000): "
curl -s http://localhost:9000/health >/dev/null 2>&1 && echo "✅ Running" || echo "❌ Failed"

echo -n "OpenWebUI (8080): "
curl -s http://localhost:8080/health >/dev/null 2>&1 && echo "✅ Running" || echo "⚠️  Not detected"

echo -n "Ollama (11434): "
curl -s http://localhost:11434/api/tags >/dev/null 2>&1 && echo "✅ Running" || echo "❌ Failed"

# Test AI integration
echo -e "\n${BLUE}🧪 Testing AI Integration:${NC}"
TEST_RESPONSE=$(curl -s -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "session_id": "test"}' 2>/dev/null || echo "error")

if echo "$TEST_RESPONSE" | grep -q "confidence"; then
    echo "✅ AI integration working"
else
    echo "⚠️  AI integration needs attention"
    echo "Response: $TEST_RESPONSE"
fi

echo -e "\n${GREEN}🎉 Platform Restart Complete!${NC}"
echo ""
echo "📋 Next Steps:"
echo "1. Test with a simple query: 'hello'"
echo "2. You should get an AI response instead of a template"
echo "3. If still getting templates, check the logs above"
echo ""
echo "🔧 Useful Commands:"
echo "  ./bin/restart_platform.sh  - Run this script again"
echo "  ./bin/cleanup_platform.sh  - Stop all services"
echo "  curl http://localhost:8001/health  - Check Core Backend"
echo "  curl http://localhost:9000/health  - Check Gateway"

# Keep script running to show logs
echo -e "\n${YELLOW}📊 Monitoring logs... (Press Ctrl+C to exit)${NC}"
sleep 2
tail -f "$PROJECT_ROOT/logs/"*.log 2>/dev/null || echo "No log files found yet"