#!/bin/bash

# =============================================================================
# STANDALONE CORE BACKEND RUNNER
# =============================================================================
# Run Core Backend directly for testing and debugging
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/corebackend/implementation/backend"
VENV_PATH="$PROJECT_ROOT/openwebui_venv"

echo -e "${BLUE}🚀 Starting Core Backend Standalone${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found: $VENV_PATH${NC}"
    echo -e "${YELLOW}Please run the main setup first to create the virtual environment${NC}"
    exit 1
fi

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
    exit 1
fi

# Check if main.py exists
if [ ! -f "$BACKEND_DIR/main.py" ]; then
    echo -e "${RED}❌ main.py not found in: $BACKEND_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found Core Backend at: $BACKEND_DIR${NC}"
echo -e "${GREEN}✅ Found virtual environment at: $VENV_PATH${NC}"

# Kill any existing processes on port 8001
echo -e "${YELLOW}🔄 Cleaning up existing processes on port 8001...${NC}"
pkill -f "uvicorn.*main:app.*8001" 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
sleep 2

# Check if port is free
if lsof -i :8001 >/dev/null 2>&1; then
    echo -e "${RED}❌ Port 8001 is still in use. Please stop the conflicting process.${NC}"
    lsof -i :8001
    exit 1
fi

echo -e "${GREEN}✅ Port 8001 is available${NC}"

# Change to backend directory
cd "$BACKEND_DIR"
echo -e "${BLUE}📂 Working directory: $(pwd)${NC}"

# Activate virtual environment
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"

# Check Python environment
echo -e "${BLUE}🐍 Python environment:${NC}"
which python
python --version
echo ""

# Check if required packages are installed
echo -e "${BLUE}📦 Checking dependencies...${NC}"
python -c "import fastapi, uvicorn; print('✅ FastAPI and Uvicorn available')" || {
    echo -e "${RED}❌ Missing FastAPI or Uvicorn. Installing...${NC}"
    pip install fastapi uvicorn
}

# Check if enhanced_agent.py exists
if [ ! -f "enhanced_agent.py" ]; then
    echo -e "${YELLOW}⚠️  enhanced_agent.py not found. Core Backend may have import issues.${NC}"
fi

# Run the backend
echo -e "${GREEN}🚀 Starting Core Backend on port 8001...${NC}"
echo -e "${BLUE}   Access at: http://localhost:8001${NC}"
echo -e "${BLUE}   API docs: http://localhost:8001/docs${NC}"
echo -e "${BLUE}   OpenAPI:  http://localhost:8001/openapi.json${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Start uvicorn with detailed logging
exec python -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8001 \
    --reload \
    --log-level info \
    --access-log