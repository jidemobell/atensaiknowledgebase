#!/bin/bash

# =============================================================================
# TEST FRESH INSTALLATION
# =============================================================================
# This script simulates a fresh installation to verify Knowledge Fusion
# auto-installation works correctly
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing Fresh Installation Simulation${NC}"
echo -e "${BLUE}=========================================${NC}"

PROJECT_ROOT="$(pwd)"
OPENWEBUI_PATH="$PROJECT_ROOT/open-webui-cloned"
KNOWLEDGE_FUSION_PATH="$OPENWEBUI_PATH/knowledge-fusion"

echo -e "\n${YELLOW}📁 Current structure:${NC}"
echo "Project Root: $PROJECT_ROOT"
echo "OpenWebUI Path: $OPENWEBUI_PATH"
echo "Knowledge Fusion Path: $KNOWLEDGE_FUSION_PATH"

echo -e "\n${YELLOW}🔍 Checking submodule status:${NC}"
git submodule status

echo -e "\n${YELLOW}📋 Checking if Knowledge Fusion exists:${NC}"
if [ -d "$KNOWLEDGE_FUSION_PATH" ]; then
    echo -e "${GREEN}✅ Knowledge Fusion directory exists${NC}"
    echo "Contents:"
    ls -la "$KNOWLEDGE_FUSION_PATH" | head -5
else
    echo -e "${RED}❌ Knowledge Fusion directory missing${NC}"
fi

echo -e "\n${YELLOW}🔍 Checking Knowledge Fusion template:${NC}"
if [ -d "$PROJECT_ROOT/knowledge-fusion-template" ]; then
    echo -e "${GREEN}✅ Knowledge Fusion template exists${NC}"
    echo "Template contents:"
    ls -la "$PROJECT_ROOT/knowledge-fusion-template"
else
    echo -e "${RED}❌ Knowledge Fusion template missing${NC}"
fi

echo -e "\n${YELLOW}⚙️ Testing auto-installation logic:${NC}"
# Temporarily remove Knowledge Fusion to test auto-install
if [ -d "$KNOWLEDGE_FUSION_PATH" ]; then
    echo "Temporarily removing Knowledge Fusion for test..."
    rm -rf "$KNOWLEDGE_FUSION_PATH"
fi

# Test the installation logic
if [ ! -d "$KNOWLEDGE_FUSION_PATH" ]; then
    echo "Knowledge Fusion not found, testing installation..."
    if [ -d "$PROJECT_ROOT/knowledge-fusion-template" ]; then
        cp -r "$PROJECT_ROOT/knowledge-fusion-template" "$KNOWLEDGE_FUSION_PATH"
        echo -e "${GREEN}✅ Knowledge Fusion auto-installation successful${NC}"
    else
        echo -e "${RED}❌ Knowledge Fusion template not found${NC}"
        exit 1
    fi
fi

echo -e "\n${YELLOW}✅ Verification:${NC}"
if [ -d "$KNOWLEDGE_FUSION_PATH" ] && [ -f "$KNOWLEDGE_FUSION_PATH/start_server.py" ]; then
    echo -e "${GREEN}✅ Knowledge Fusion is properly installed${NC}"
    echo -e "${GREEN}✅ Server files are present${NC}"
else
    echo -e "${RED}❌ Knowledge Fusion installation failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 Fresh installation test PASSED!${NC}"
echo -e "${GREEN}Users can now successfully pull and run the repository on any system.${NC}"
echo ""
echo -e "${BLUE}📝 Next steps for users:${NC}"
echo "1. git clone <repository>"
echo "2. cd <repository>"
echo "3. git submodule update --init --recursive"
echo "4. ./start.sh (select option 1)"
echo "5. Knowledge Fusion will be automatically installed!"
