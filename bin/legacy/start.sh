#!/bin/bash

# Enhanced AI-Powered Support System Startup Script
echo "🚀 Starting Enhanced AI-Powered Support System"

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: Please run this script from the implementation directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if Qdrant is running (optional)
echo "🔍 Checking optional services..."
if curl -s http://localhost:6333/collections > /dev/null 2>&1; then
    echo "✅ Qdrant vector database detected at localhost:6333"
else
    echo "⚠️  Qdrant not detected - semantic search will use mock mode"
    echo "   To enable full semantic search, run: docker run -p 6333:6333 qdrant/qdrant"
fi

# Start the FastAPI server
echo "🌟 Starting FastAPI server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📖 Interactive docs at: http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop"

cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
