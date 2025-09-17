#!/bin/bash

# =============================================================================
# TOPOLOGY KNOWLEDGE - SMART SETUP SCRIPT
# =============================================================================
# This script automatically handles repository setup for different environments:
# - Enterprise environments (IBM, etc.) with limited SSH access
# - Development environments with full SSH access
# - Mixed environments where some repos need HTTPS, others SSH
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 TOPOLOGY KNOWLEDGE - SMART SETUP${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""

# Function to test SSH access to GitHub
test_github_ssh() {
    ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"
    return $?
}

# Function to test HTTPS access to GitHub
test_github_https() {
    curl -s --connect-timeout 5 https://api.github.com/user >/dev/null 2>&1
    return $?
}

# Function to setup submodules with fallback
setup_submodules() {
    echo -e "${BLUE}🔍 Detecting best connection method...${NC}"
    
    # Test SSH access first (preferred for development)
    if test_github_ssh; then
        echo -e "${GREEN}✅ SSH access detected - using SSH URLs${NC}"
        git config --file .gitmodules submodule.open-webui-cloned.url "git@github.com:open-webui/open-webui.git"
    elif test_github_https; then
        echo -e "${YELLOW}⚠️  SSH not available - using HTTPS URLs${NC}"
        git config --file .gitmodules submodule.open-webui-cloned.url "https://github.com/open-webui/open-webui.git"
    else
        echo -e "${RED}❌ No GitHub access detected${NC}"
        echo "Please check your internet connection and GitHub access"
        exit 1
    fi
    
    # Sync and update submodules
    echo -e "${BLUE}🔄 Syncing submodule configuration...${NC}"
    git submodule sync
    
    echo -e "${BLUE}📥 Initializing and updating submodules...${NC}"
    git submodule update --init --recursive
    
    echo -e "${GREEN}✅ Submodules setup complete!${NC}"
}

# Function to verify setup
verify_setup() {
    echo -e "\n${BLUE}🔍 Verifying setup...${NC}"
    
    # Check if open-webui-cloned has content
    if [ "$(ls -A open-webui-cloned/ 2>/dev/null)" ]; then
        echo -e "${GREEN}✅ OpenWebUI submodule populated${NC}"
    else
        echo -e "${RED}❌ OpenWebUI submodule is empty${NC}"
        return 1
    fi
    
    # Check if Knowledge Fusion exists
    if [ -d "open-webui-cloned/knowledge-fusion" ]; then
        echo -e "${GREEN}✅ Knowledge Fusion integration found${NC}"
    else
        echo -e "${YELLOW}⚠️  Knowledge Fusion integration not found (will be installed during startup)${NC}"
    fi
    
    # Check startup scripts
    if [ -x "start.sh" ]; then
        echo -e "${GREEN}✅ Startup scripts ready${NC}"
    else
        echo -e "${RED}❌ Startup scripts not executable${NC}"
        chmod +x start*.sh
        echo -e "${GREEN}✅ Fixed startup script permissions${NC}"
    fi
}

# Main setup flow
main() {
    echo "Environment: $(uname -s) $(uname -m)"
    echo "Git version: $(git --version)"
    echo ""
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        echo -e "${RED}❌ Not in a git repository${NC}"
        echo "Please run this script from the project root directory"
        exit 1
    fi
    
    # Setup submodules
    setup_submodules
    
    # Verify everything works
    verify_setup
    
    echo ""
    echo -e "${GREEN}🎉 Setup complete!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Run: ${GREEN}./start.sh${NC}"
    echo "  2. Choose your deployment mode"
    echo "  3. Access OpenWebUI at http://localhost:3000"
    echo ""
    echo -e "${YELLOW}💡 For team members:${NC}"
    echo "  • Clone: git clone --recursive <repo-url>"
    echo "  • Or run: git submodule update --init --recursive"
    echo "  • Then: ./start.sh"
}

# Handle command line arguments
case "${1:-}" in
    --ssh)
        echo "Forcing SSH URLs..."
        git config --file .gitmodules submodule.open-webui-cloned.url "git@github.com:jidemobell/atensai-open-webui.git"
        git submodule sync
        git submodule update --init --recursive
        ;;
    --https)
        echo "Forcing HTTPS URLs..."
        git config --file .gitmodules submodule.open-webui-cloned.url "https://github.com/jidemobell/atensai-open-webui.git"
        git submodule sync
        git submodule update --init --recursive
        ;;
    --enterprise|--corporate)
        echo "Configuring for enterprise/corporate environment..."
        # Force HTTPS for all GitHub URLs globally
        git config --global url."https://github.com/".insteadOf git@github.com:
        git config --file .gitmodules submodule.open-webui-cloned.url "https://github.com/jidemobell/atensai-open-webui.git"
        git submodule sync
        git submodule update --init --recursive
        echo "✅ Configured for enterprise environment with HTTPS-only access"
        ;;
    --help|-h)
        echo "Usage: $0 [--ssh|--https|--enterprise|--help]"
        echo ""
        echo "Options:"
        echo "  --ssh          Force SSH URLs (for development environments)"
        echo "  --https        Force HTTPS URLs (for basic cross-machine compatibility)"
        echo "  --enterprise   Configure for enterprise/corporate environments"
        echo "  --corporate    (same as --enterprise)"
        echo "  --help         Show this help message"
        echo ""
        echo "Without options, automatically detects the best method"
        ;;
    *)
        main
        ;;
esac
