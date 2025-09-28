git #!/bin/bash

# Knowledge Fusion Platform Cleanup Script
# Removes outdated, redundant, and unwanted files

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}🧹 Knowledge Fusion Platform Cleanup${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""

# Files and directories to remove
declare -a SYSTEM_FILES=(
    ".DS_Store"
    ".webui_secret_key"
)

declare -a LEGACY_SCRIPTS=(
    "setup.sh"
    "start.sh"
)

declare -a OUTDATED_DOCS=(
    "docs/COMPLETE_SETUP_GUIDE.md"
    "docs/COMPLETE_USER_GUIDE.md"
    "docs/CORE_BACKEND_DEPENDENCIES_FIXED.md"
    "docs/CROSS_MACHINE_SETUP_GUIDE.md"
    "docs/DOCKER_DEPLOYMENT.md"
    "docs/ENTERPRISE_SETUP.md"
    "docs/GIT_SUBMODULE_GUIDE.md"
    "docs/IBM_DEPLOYMENT_GUIDE.md"
    "docs/IBM_TROUBLESHOOTING_GUIDE.md"
    "docs/INTEGRATION_PLAN.md"
    "docs/KNOWLEDGE_FUSION_COMPLETE.md"
    "docs/LOG_MONITORING_GUIDE.md"
    "docs/MIGRATION_GUIDE.md"
    "docs/MIGRATION_GUIDE_LOCAL_OLLAMA.md"
    "docs/MODEL_INTEGRATION.md"
    "docs/OPENWEBUI_FRESH_MIGRATION.md"
    "docs/OPENWEBUI_SETUP.md"
    "docs/OPENWEBUI_SUCCESS.md"
    "docs/PODMAN_SUPPORT.md"
    "docs/PROJECT_ORGANIZATION.md"
    "docs/PROJECT_VISION.md"
    "docs/QWENROUTE_API_DOCUMENTATION.md"
    "docs/SETUP_COMPLETION_SUMMARY.md"
    "docs/SSO_INTEGRATION_GUIDE.md"
    "docs/SUBMODULE_MIGRATION.md"
    "docs/UNIFIED_STARTUP_GUIDE.md"
)

declare -a KEEP_DOCS=(
    "docs/AI_AGENT_ARCHITECTURE.md"
    "docs/API_DOCUMENTATION_SUMMARY.md"
    "docs/INTEGRATION_FLOW.md"
    "docs/KNOWLEDGE_FUSION_ARCHITECTURE.md"
    "docs/STARTUP_GUIDE.md"
)

# Function to remove files safely
remove_file() {
    local file="$1"
    local category="$2"
    
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo -e "${YELLOW}Removing $category:${NC} $file"
        rm "$PROJECT_ROOT/$file"
        echo -e "${GREEN}✅ Removed${NC}"
    elif [ -d "$PROJECT_ROOT/$file" ]; then
        echo -e "${YELLOW}Removing $category directory:${NC} $file"
        rm -rf "$PROJECT_ROOT/$file"
        echo -e "${GREEN}✅ Removed${NC}"
    else
        echo -e "${CYAN}ℹ️  Already removed:${NC} $file"
    fi
}

# Function to clean log files
clean_logs() {
    echo -e "\n${CYAN}🗂️  Cleaning log files...${NC}"
    
    # Remove old log files (keep last 7 days)
    if [ -d "$PROJECT_ROOT/logs" ]; then
        find "$PROJECT_ROOT/logs" -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
        echo -e "${GREEN}✅ Cleaned old log files${NC}"
    fi
    
    # Clean scheduler logs
    if [ -d "$PROJECT_ROOT/logs/scheduler" ]; then
        find "$PROJECT_ROOT/logs/scheduler" -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
        echo -e "${GREEN}✅ Cleaned old scheduler logs${NC}"
    fi
}

# Function to clean data directories
clean_data() {
    echo -e "\n${CYAN}🗄️  Cleaning data directories...${NC}"
    
    # Clean temporary data
    if [ -d "$PROJECT_ROOT/data/temp" ]; then
        rm -rf "$PROJECT_ROOT/data/temp"
        echo -e "${GREEN}✅ Removed temporary data${NC}"
    fi
    
    # Clean old ChromaDB data if exists
    if [ -d "$PROJECT_ROOT/data/chromadb_old" ]; then
        rm -rf "$PROJECT_ROOT/data/chromadb_old"
        echo -e "${GREEN}✅ Removed old ChromaDB data${NC}"
    fi
}

# Main cleanup execution
main() {
    echo -e "${CYAN}Starting cleanup process...${NC}"
    echo ""
    
    # Remove system files
    echo -e "${BLUE}🖥️  Removing system files:${NC}"
    for file in "${SYSTEM_FILES[@]}"; do
        remove_file "$file" "system file"
    done
    
    echo ""
    
    # Remove legacy scripts
    echo -e "${BLUE}📜 Removing legacy scripts:${NC}"
    for file in "${LEGACY_SCRIPTS[@]}"; do
        remove_file "$file" "legacy script"
    done
    
    echo ""
    
    # Remove outdated documentation
    echo -e "${BLUE}📚 Removing outdated documentation:${NC}"
    for file in "${OUTDATED_DOCS[@]}"; do
        remove_file "$file" "outdated doc"
    done
    
    # Clean logs and data
    clean_logs
    clean_data
    
    echo ""
    echo -e "${GREEN}🎉 Cleanup completed!${NC}"
    echo ""
    
    # Show what's kept
    echo -e "${CYAN}📋 Essential files retained:${NC}"
    echo -e "${YELLOW}Core Scripts:${NC}"
    echo "  • start_server_mode.sh - Main service launcher"
    echo "  • add_knowledge_source.sh - GitHub repository management"
    echo "  • manage_hybrid_sources.sh - Hybrid knowledge sources"
    echo "  • view_logs.sh - Advanced monitoring"
    echo "  • automated_scheduler.sh - Update scheduling"
    echo "  • demo_platform.sh - Platform demonstration"
    echo ""
    
    echo -e "${YELLOW}Essential Documentation:${NC}"
    for doc in "${KEEP_DOCS[@]}"; do
        if [ -f "$PROJECT_ROOT/$doc" ]; then
            echo "  • $(basename "$doc")"
        fi
    done
    echo ""
    
    echo -e "${YELLOW}Core Directories:${NC}"
    echo "  • corebackend/ - Core backend services"
    echo "  • knowledge-fusion-template/ - Multi-agent system"
    echo "  • openwebui_venv/ - Python virtual environment"
    echo "  • chroma/ - Vector database"
    echo "  • data/ - Knowledge data storage"
    echo "  • logs/ - System logs (recent only)"
    echo ""
    
    # Final summary
    echo -e "${GREEN}✨ Platform is now clean and optimized!${NC}"
    echo -e "${CYAN}Ready for production deployment with minimal footprint.${NC}"
}

# Confirmation prompt
echo -e "${YELLOW}⚠️  This will remove outdated files and clean up the platform.${NC}"
echo -e "${CYAN}The following will be removed:${NC}"
echo "  • System files (.DS_Store, .webui_secret_key)"
echo "  • Legacy scripts (setup.sh, start.sh)"
echo "  • Outdated documentation (30+ legacy docs)"
echo "  • Old log files (older than 7 days)"
echo ""

read -p "Do you want to proceed? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    main
else
    echo -e "${CYAN}Cleanup cancelled.${NC}"
    exit 0
fi