#!/bin/bash

# =============================================================================
# TOPOLOGY KNOWLEDGE - CLEANUP SCRIPT
# =============================================================================
# This script removes old, duplicate, and unnecessary files to keep only
# the essential unified startup system
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 TOPOLOGY KNOWLEDGE - CLEANUP${NC}"
echo -e "${BLUE}================================${NC}"

# Get confirmation before proceeding
echo -e "${YELLOW}This will remove old startup scripts and redundant files.${NC}"
echo -e "${YELLOW}The unified startup system (start.sh, start_server_mode.sh, start_docker_mode.sh) will be kept.${NC}"
echo ""
echo -n -e "${YELLOW}Do you want to proceed? (y/N): ${NC}"
read -r confirmation

if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Cleanup cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}🗑️ Removing old startup scripts...${NC}"

# Old startup scripts to remove
OLD_STARTUP_SCRIPTS=(
    "run_openwebui.sh"
    "start_openwebui.sh"
    "setup_knowledge_fusion.sh"
    "knowledge_fusion_init.py"
    "deploy-full-backend.sh"
    "deploy-hybrid-kf.sh"
    "deploy-ibm.sh"
    "cleanup.sh"
    "prepare_flash_drive.sh"
    "quick-fix-registry.sh"
    "validate-docker-setup.sh"
    "simple_ollama_interface.py"
    "demo_interface.py"
    "test_integration.py"
)

for script in "${OLD_STARTUP_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        echo "  🗑️ Removing: $script"
        rm -f "$script"
    fi
done

echo ""
echo -e "${BLUE}🗑️ Removing redundant Docker Compose files...${NC}"

# Keep only the main docker-compose files, remove the rest
DOCKER_COMPOSE_TO_REMOVE=(
    "docker-compose.dockerhub.yml"
    "docker-compose.full-backend.yml"
    "docker-compose.hybrid-kf.yml"
    "docker-compose.ibm-enhanced.yml"
    "docker-compose.ibm.yml"
    "docker-compose.official-base.yml"
    "docker-compose.simple.yml"
)

for compose_file in "${DOCKER_COMPOSE_TO_REMOVE[@]}"; do
    if [ -f "$compose_file" ]; then
        echo "  🗑️ Removing: $compose_file"
        rm -f "$compose_file"
    fi
done

echo ""
echo -e "${BLUE}🗑️ Removing redundant documentation files...${NC}"

# Remove duplicate/redundant documentation
REDUNDANT_DOCS=(
    "CLEANUP_SUMMARY.md"
    "DOCKER_MEMORY_SOLUTION.md"
    "DOCKER_SOLUTION_SUMMARY.md"
    "DOCKER_SUCCESS_GUIDE.md"
    "DOCUMENTATION_STATUS.md"
    "OPENWEBUI_TROUBLESHOOTING.md"
    "REGISTRY_ACCESS_SOLUTION.md"
    "QUICK_REFERENCE.md"  # We have UNIFIED_STARTUP_GUIDE.md now
)

for doc in "${REDUNDANT_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo "  🗑️ Removing: $doc"
        rm -f "$doc"
    fi
done

echo ""
echo -e "${BLUE}🗑️ Removing temporary/log files...${NC}"

# Remove temporary and log files
TEMP_FILES=(
    "demo.log"
    ".topology_pids"
    "env.docker.template"
    ".env.ibm.template"
)

for temp_file in "${TEMP_FILES[@]}"; do
    if [ -f "$temp_file" ]; then
        echo "  🗑️ Removing: $temp_file"
        rm -f "$temp_file"
    fi
done

echo ""
echo -e "${BLUE}🗑️ Cleaning up Docker directory...${NC}"

# Clean up docker directory if it exists
if [ -d "docker" ]; then
    echo "  🗑️ Removing docker/ directory (replaced by unified scripts)"
    rm -rf "docker"
fi

echo ""
echo -e "${BLUE}🗑️ Removing duplicate GitHub configs...${NC}"

# Keep only one GitHub sources config
if [ -f "github_sources_config.yaml" ] && [ -f "github_sources.yml" ]; then
    echo "  🗑️ Removing duplicate: github_sources_config.yaml (keeping github_sources.yml)"
    rm -f "github_sources_config.yaml"
fi

echo ""
echo -e "${BLUE}📁 Checking what remains...${NC}"

echo ""
echo -e "${GREEN}✅ Essential files kept:${NC}"
echo "  📄 Core Scripts:"
echo "    • start.sh (main launcher)"
echo "    • start_server_mode.sh" 
echo "    • start_docker_mode.sh"
echo "    • verify_knowledge_fusion.py"
echo ""
echo "  📄 Core Configuration:"
echo "    • README.md"
echo "    • UNIFIED_STARTUP_GUIDE.md"
echo "    • IBM_DEPLOYMENT_GUIDE.md"
echo "    • OPENWEBUI_SUCCESS.md"
echo "    • .env (if exists)"
echo "    • .webui_secret_key"
echo "    • requirements.txt"
echo "    • github_sources.yml"
echo "    • knowledge_base.json"
echo ""
echo "  📁 Core Directories:"
echo "    • corebackend/"
echo "    • openwebuibase/"
echo "    • openwebui_venv/"
echo "    • docs/"
echo "    • txts/"

# Keep only essential docker-compose file
if [ -f "docker-compose.knowledge-fusion.yml" ]; then
    echo "    • docker-compose.knowledge-fusion.yml (for Docker mode)"
fi

echo ""
echo -e "${GREEN}🎯 Current project structure:${NC}"
tree -L 2 -a 2>/dev/null || ls -la

echo ""
echo -e "${GREEN}✅ Cleanup complete!${NC}"
echo ""
echo -e "${BLUE}🚀 Your streamlined Topology Knowledge Platform is ready:${NC}"
echo "  • Run: ${GREEN}./start.sh${NC} for interactive launcher"
echo "  • Run: ${GREEN}./start_server_mode.sh${NC} for server mode"
echo "  • Run: ${GREEN}./start_docker_mode.sh${NC} for Docker mode"
echo ""
echo -e "${YELLOW}📖 See UNIFIED_STARTUP_GUIDE.md for complete documentation${NC}"
