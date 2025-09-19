#!/bin/bash
# Core Backend Runner with Isolated Virtual Environment
# Runs Core Backend in its own clean virtual environment without ML dependencies

set -e  # Exit on any error

# Configuration
CORE_BACKEND_PORT=8001
VENV_PATH="corebackend_venv"
BACKEND_PATH="corebackend/implementation/backend"
LOG_FILE="logs/core_backend_isolated.log"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔧 Starting Core Backend in Isolated Environment..."

# Check if script is run from project root
if [ ! -f "knowledge_base.json" ]; then
    echo -e "${RED}❌ Error: Please run this script from the TOPOLOGYKNOWLEDGE project root${NC}"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if isolated virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Error: Isolated virtual environment not found at $VENV_PATH${NC}"
    echo "Please create it first with: python3 -m venv $VENV_PATH"
    exit 1
fi

# Check if backend directory exists
if [ ! -d "$BACKEND_PATH" ]; then
    echo -e "${RED}❌ Error: Core Backend directory not found at $BACKEND_PATH${NC}"
    exit 1
fi

# Kill any existing process on the Core Backend port
echo "🔍 Checking for existing processes on port $CORE_BACKEND_PORT..."
if lsof -ti:$CORE_BACKEND_PORT >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port $CORE_BACKEND_PORT is in use. Stopping existing process...${NC}"
    pkill -f "uvicorn.*:$CORE_BACKEND_PORT" 2>/dev/null || true
    sleep 2
fi

# Activate the isolated virtual environment
echo "🐍 Activating isolated virtual environment..."
source "$VENV_PATH/bin/activate"

# Verify FastAPI is installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${RED}❌ Error: FastAPI not installed in isolated environment${NC}"
    echo "Please install it with: source $VENV_PATH/bin/activate && pip install fastapi uvicorn"
    exit 1
fi

# Navigate to backend directory
cd "$BACKEND_PATH"

# Check if lightweight main exists
if [ ! -f "main_lite.py" ]; then
    echo -e "${RED}❌ Error: main_lite.py not found in $BACKEND_PATH${NC}"
    echo "Creating lightweight backend..."
    exit 1
fi

# Start Core Backend in lightweight mode
echo "🚀 Starting Core Backend (Lightweight Mode) on port $CORE_BACKEND_PORT..."
echo "📁 Working directory: $(pwd)"
echo "🐍 Python executable: $(which python)"
echo "📝 Logs will be written to: $LOG_FILE"
echo "🔧 Mode: Lightweight (No ML Dependencies)"

# Run with proper logging
python -m uvicorn main_lite:app \
    --host 0.0.0.0 \
    --port $CORE_BACKEND_PORT \
    --reload \
    --log-level info 2>&1 | tee "../../../$LOG_FILE" &

BACKEND_PID=$!

# Wait a moment for startup
sleep 3

# Check if the process is still running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Core Backend failed to start. Check logs: $LOG_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Core Backend started successfully!${NC}"
echo ""
echo "📊 Service Information:"
echo "   • PID: $BACKEND_PID"
echo "   • Port: $CORE_BACKEND_PORT"
echo "   • API Docs: http://localhost:$CORE_BACKEND_PORT/docs"
echo "   • Health Check: http://localhost:$CORE_BACKEND_PORT/health"
echo "   • Virtual Environment: $VENV_PATH"
echo ""
echo "🔍 Testing endpoint availability..."
sleep 2

# Test if the endpoint is responding
if curl -s "http://localhost:$CORE_BACKEND_PORT/health" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Core Backend health endpoint responding${NC}"
else
    echo -e "${YELLOW}⚠️  Health endpoint not yet available (may still be starting)${NC}"
fi

echo ""
echo "🎯 Core Backend is running in isolated environment!"
echo "   To stop: pkill -f 'uvicorn.*:$CORE_BACKEND_PORT'"
echo "   To view logs: tail -f $LOG_FILE"