#!/bin/bash
# Quick fix to start the Core Backend with AI models properly configured

echo "🔧 Fixing Core Backend AI Model Integration..."

# Stop current services
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "main_lite" 2>/dev/null || true
sleep 2

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "❌ Ollama is not running! Please start Ollama first:"
    echo "   ollama serve"
    exit 1
fi

echo "✅ Ollama is running"

# Pull required models if not available
echo "🔍 Checking required models..."

# Check for embedding model
if ! ollama list | grep -q "nomic-embed-text"; then
    echo "📥 Pulling nomic-embed-text (required for semantic search)..."
    ollama pull nomic-embed-text
fi

# Check for a reasoning model
if ! ollama list | grep -q "llama3.1:8b" && ! ollama list | grep -q "granite3.2:8b"; then
    echo "📥 Pulling reasoning model..."
    if ollama list | grep -q "granite3.2"; then
        echo "✅ Using your existing Granite models"
    else
        echo "📥 Pulling llama3.1:8b for reasoning..."
        ollama pull llama3.1:8b
    fi
fi

echo "✅ Models ready"

# Set environment variables for AI integration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export OLLAMA_BASE_URL="http://localhost:11434"
export ENABLE_EMBEDDINGS="true"
export AI_MODEL_CONFIG="$PROJECT_ROOT/config/ai_models_config.json"

# Start Core Backend with full AI capabilities
echo "🚀 Starting Core Backend with AI models..."

# Get the current project root dynamically
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORE_BACKEND_PATH="$PROJECT_ROOT/corebackend/implementation/backend"

if [ -d "$CORE_BACKEND_PATH" ]; then
    cd "$CORE_BACKEND_PATH"
    echo "✅ Found Core Backend at: $CORE_BACKEND_PATH"
else
    echo "❌ Core Backend path not found: $CORE_BACKEND_PATH"
    echo "🔍 Looking for main.py in project..."
    
    # Search for main.py files
    if [ -f "$PROJECT_ROOT/corebackend/implementation/backend/main.py" ]; then
        cd "$PROJECT_ROOT/corebackend/implementation/backend"
        echo "✅ Using: main.py"
    elif [ -f "$PROJECT_ROOT/corebackend/implementation/backend/main_enhanced.py" ]; then
        cd "$PROJECT_ROOT/corebackend/implementation/backend"
        echo "✅ Using: main_enhanced.py (will rename to main.py)"
        cp main_enhanced.py main.py
    else
        echo "❌ Could not find main.py or main_enhanced.py. Please check your project structure."
        ls -la "$PROJECT_ROOT/corebackend/implementation/backend/main*.py"
        exit 1
    fi
fi

# Install requirements if needed
echo "📦 Installing AI dependencies..."
pip install sentence-transformers==2.2.2 numpy requests aiohttp fastapi uvicorn pydantic 2>/dev/null || true
echo "✅ Dependencies installed"

# Start with AI models enabled
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

echo "⏳ Waiting for Core Backend to initialize with AI models..."
sleep 5

# Test the connection
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    echo "✅ Core Backend is running with AI capabilities!"
    echo "🔗 Health: http://localhost:8001/health"
    echo "📚 Docs: http://localhost:8001/docs"
    
    # Check if ML components are enabled
    if curl -s http://localhost:8001/health | grep -q "ml_components.*disabled"; then
        echo "⚠️  ML components still disabled - checking requirements..."
        pip install sentence-transformers numpy requests
        echo "🔄 Restarting to pick up new packages..."
        kill $BACKEND_PID
        sleep 2
        python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
        sleep 3
    fi
    
    echo "🎯 Testing AI integration..."
    curl -X POST http://localhost:8001/query \
      -H "Content-Type: application/json" \
      -d '{"query": "test AI integration", "session_id": "test"}' \
      2>/dev/null | head -c 100
      
    echo ""
    echo "✅ Core Backend is ready for intelligent responses!"
else
    echo "❌ Core Backend failed to start properly"
    exit 1
fi

echo ""
echo "🎯 Next steps:"
echo "1. Restart the Knowledge Fusion Gateway: ./bin/start_server_mode.sh"
echo "2. Test with a query in OpenWebUI"
echo "3. You should now get AI-generated responses instead of templates!"