#!/bin/bash
# Local Repository Manager for ASM Knowledge Base
# Works with locally cloned repositories instead of GitHub API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_REPOS_DIR="$PROJECT_ROOT/data/asm_repositories"
CONFIG_FILE="$PROJECT_ROOT/asm_local_config.json"

echo -e "${BLUE}🏗️ ASM Local Repository Manager${NC}"
echo -e "${BLUE}================================${NC}"

# Create repositories directory
mkdir -p "$LOCAL_REPOS_DIR"

# Function to show help
show_help() {
    echo "ASM Local Repository Manager"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help"
    echo "  -i, --init           Initialize local repository structure"
    echo "  -u, --update         Update all local repositories"
    echo "  -s, --status         Show status of all repositories"
    echo "  -a, --analyze        Analyze repositories for knowledge extraction"
    echo "  --setup-cron         Setup weekly update cron job"
    echo ""
    echo "Examples:"
    echo "  $0 --init            # Setup local repo structure"
    echo "  $0 --update          # Pull latest changes"
    echo "  $0 --analyze         # Extract knowledge"
}

# Function to initialize repository structure
init_repos() {
    echo -e "${BLUE}🔧 Initializing ASM Repository Structure${NC}"
    echo ""
    
    # Create ASM-specific directory structure  
    mkdir -p "$LOCAL_REPOS_DIR/core_services"
    mkdir -p "$LOCAL_REPOS_DIR/observers" 
    mkdir -p "$LOCAL_REPOS_DIR/ui"
    mkdir -p "$LOCAL_REPOS_DIR/topology"
    mkdir -p "$LOCAL_REPOS_DIR/infrastructure"
    mkdir -p "$LOCAL_REPOS_DIR/documentation"
    
    echo -e "${GREEN}✅ Directory structure created${NC}"
    echo ""
    echo "📁 ASM Repository Structure:"
    echo "   • $LOCAL_REPOS_DIR/core_services/  - ASM Core/Backend Services"
    echo "   • $LOCAL_REPOS_DIR/observers/      - Observer Components & Patterns"
    echo "   • $LOCAL_REPOS_DIR/ui/             - ASM UI Components & Frontend"
    echo "   • $LOCAL_REPOS_DIR/topology/       - Topology Services & Management"
    echo "   • $LOCAL_REPOS_DIR/infrastructure/ - Deployment, Config & DevOps"
    echo "   • $LOCAL_REPOS_DIR/documentation/  - ASM Documentation & Guides"
    echo ""
    echo -e "${YELLOW}📝 Next Steps:${NC}"
    echo "1. Clone your ASM repositories into the appropriate directories"
    echo "2. Run: $0 --setup-cron (to setup automatic updates)"
    echo "3. Run: $0 --analyze (to extract knowledge)"
}

# Function to update all repositories
update_repos() {
    echo -e "${BLUE}🔄 Updating Local ASM Repositories${NC}"
    echo ""
    
    updated_count=0
    failed_count=0
    
    # Find all git repositories in the ASM directory
    find "$LOCAL_REPOS_DIR" -name ".git" -type d | while read -r git_dir; do
        repo_dir=$(dirname "$git_dir")
        repo_name=$(basename "$repo_dir")
        
        echo "📂 Updating: $repo_name"
        cd "$repo_dir"
        
        if git pull origin main 2>/dev/null || git pull origin master 2>/dev/null; then
            echo -e "   ${GREEN}✅ Updated successfully${NC}"
            ((updated_count++))
        else
            echo -e "   ${YELLOW}⚠️  Update had issues${NC}"
            ((failed_count++))
        fi
        echo ""
    done
    
    echo -e "${GREEN}🎯 Update complete: $updated_count updated, $failed_count failed${NC}"
}

# Function to show repository status
show_status() {
    echo -e "${BLUE}📊 ASM Repository Status${NC}"
    echo ""
    
    total_repos=0
    
    for category in core observers ui services infrastructure documentation; do
        category_dir="$LOCAL_REPOS_DIR/$category"
        if [ -d "$category_dir" ]; then
            echo -e "${PURPLE}📁 $category/${NC}"
            
            repo_count=0
            find "$category_dir" -maxdepth 2 -name ".git" -type d | while read -r git_dir; do
                repo_dir=$(dirname "$git_dir")
                repo_name=$(basename "$repo_dir")
                
                cd "$repo_dir"
                
                # Get last commit info
                last_commit=$(git log -1 --format="%h %s" 2>/dev/null || echo "No commits")
                last_update=$(git log -1 --format="%cr" 2>/dev/null || echo "Unknown")
                
                echo "   • $repo_name"
                echo "     Last commit: $last_commit"
                echo "     Last update: $last_update"
                echo ""
                
                ((repo_count++))
                ((total_repos++))
            done
            
            if [ $repo_count -eq 0 ]; then
                echo -e "     ${YELLOW}No repositories found${NC}"
                echo ""
            fi
        fi
    done
    
    echo -e "${GREEN}📈 Total repositories: $total_repos${NC}"
}

# Function to analyze repositories for knowledge extraction
analyze_repos() {
    echo -e "${BLUE}🧠 Analyzing ASM Repositories for Knowledge Extraction${NC}"
    echo ""
    
    analysis_output="$PROJECT_ROOT/data/asm_analysis_$(date +%Y%m%d_%H%M%S).json"
    
    echo "{"
    echo "  \"analysis_timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
    echo "  \"categories\": {"
    
    for category in core observers ui services infrastructure documentation; do
        category_dir="$LOCAL_REPOS_DIR/$category"
        if [ -d "$category_dir" ]; then
            echo "Analyzing $category repositories..."
            
            # Find key files and patterns in each repository
            find "$category_dir" -maxdepth 2 -name ".git" -type d | while read -r git_dir; do
                repo_dir=$(dirname "$git_dir")
                repo_name=$(basename "$repo_dir")
                
                echo "   📂 $repo_name"
                
                # Count different file types
                java_files=$(find "$repo_dir" -name "*.java" 2>/dev/null | wc -l)
                yaml_files=$(find "$repo_dir" -name "*.yaml" -o -name "*.yml" 2>/dev/null | wc -l)
                js_files=$(find "$repo_dir" -name "*.js" 2>/dev/null | wc -l)
                dockerfile_count=$(find "$repo_dir" -name "Dockerfile*" 2>/dev/null | wc -l)
                
                echo "     • Java files: $java_files"
                echo "     • YAML files: $yaml_files"
                echo "     • JavaScript files: $js_files"
                echo "     • Dockerfiles: $dockerfile_count"
                
                # Look for key ASM patterns
                if grep -r "kafka" "$repo_dir" >/dev/null 2>&1; then
                    echo "     • Contains Kafka integration"
                fi
                
                if grep -r "cassandra\|topology" "$repo_dir" >/dev/null 2>&1; then
                    echo "     • Contains Topology/Cassandra components"
                fi
                
                if grep -r "observer" "$repo_dir" >/dev/null 2>&1; then
                    echo "     • Contains Observer patterns"
                fi
                
                echo ""
            done
        fi
    done
    
    echo -e "${GREEN}✅ Analysis complete${NC}"
    echo "   Results logged for knowledge extraction processing"
}

# Function to setup cron job
setup_cron() {
    echo -e "${BLUE}⏰ Setting up Weekly Update Cron Job${NC}"
    echo ""
    
    cron_command="0 2 * * 1 cd $(pwd) && ./bin/manage_asm_repos.sh --update >> $PROJECT_ROOT/logs/asm_update.log 2>&1"
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "manage_asm_repos.sh"; then
        echo -e "${YELLOW}⚠️  Cron job already exists${NC}"
    else
        (crontab -l 2>/dev/null; echo "$cron_command") | crontab -
        echo -e "${GREEN}✅ Cron job added${NC}"
        echo "   Updates will run every Monday at 2:00 AM"
    fi
    
    echo ""
    echo "📝 Current cron jobs:"
    crontab -l | grep -E "(manage_asm_repos|ASM)" || echo "   No ASM-related cron jobs found"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        ;;
    -i|--init)
        init_repos
        ;;
    -u|--update)
        update_repos
        ;;
    -s|--status)
        show_status
        ;;
    -a|--analyze)
        analyze_repos
        ;;
    --setup-cron)
        setup_cron
        ;;
    *)
        echo -e "${YELLOW}ℹ️  ASM Local Repository Manager${NC}"
        echo ""
        show_status
        echo ""
        echo "Run '$0 --help' for available options"
        ;;
esac