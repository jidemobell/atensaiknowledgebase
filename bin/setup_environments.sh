#!/bin/bash
# Virtual Environment Setup for Knowledge Fusion Platform
# Creates and configures both virtual environments if they don't exist

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}🔧 KNOWLEDGE FUSION PLATFORM - ENVIRONMENT SETUP${NC}"
echo -e "${BLUE}================================================${NC}"
echo "📁 Project Root: $PROJECT_ROOT"
echo ""

cd "$PROJECT_ROOT"

# Setup Core Backend isolated environment
echo -e "${BLUE}🐍 Setting up Core Backend Virtual Environment...${NC}"
if [ ! -d "corebackend_venv" ]; then
    echo "  Creating corebackend_venv..."
    python3 -m venv corebackend_venv
    
    echo "  Installing Core Backend dependencies..."
    source corebackend_venv/bin/activate
    pip install --upgrade pip
    pip install fastapi uvicorn python-multipart tiktoken requests
    deactivate
    
    echo -e "  ${GREEN}✅ Core Backend environment created${NC}"
else
    echo -e "  ${GREEN}✅ Core Backend environment already exists${NC}"
fi

# Check Knowledge Fusion environment
echo -e "\n${BLUE}🧠 Checking Knowledge Fusion Virtual Environment...${NC}"
if [ ! -d "openwebui_venv" ]; then
    echo -e "  ${YELLOW}⚠️  Knowledge Fusion environment (openwebui_venv) not found${NC}"
    echo "  This environment is required for Knowledge Fusion and OpenWebUI"
    echo "  Please create it manually or run the appropriate setup script"
    echo ""
    echo "  Example creation:"
    echo "    python3 -m venv openwebui_venv"
    echo "    source openwebui_venv/bin/activate"
    echo "    pip install fastapi uvicorn chromadb sentence-transformers"
    echo ""
else
    echo -e "  ${GREEN}✅ Knowledge Fusion environment exists${NC}"
fi

echo ""
echo -e "${GREEN}🎯 Environment Setup Complete!${NC}"
echo ""
echo "📋 Summary:"
echo "  • Core Backend: corebackend_venv (isolated, lightweight)"
echo "  • Knowledge Fusion: openwebui_venv (includes ML dependencies)"
echo ""
echo "🚀 Usage:"
echo "  • Start isolated Core Backend: ./bin/run_corebackend_isolated.sh"
echo "  • Start full platform: ./bin/start_server_mode.sh"
echo "  • Test Core Backend: curl http://localhost:8001/health"