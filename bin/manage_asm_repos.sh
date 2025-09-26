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

# Function to add path mapping for existing repositories
add_path_mapping() {
    echo -e "${BLUE}📂 Add ASM Repository Path Mapping${NC}"
    echo ""
    
    # Create config file if it doesn't exist
    if [ ! -f "$CONFIG_FILE" ]; then
        echo '{"repository_paths": {}}' > "$CONFIG_FILE"
    fi
    
    echo "Available categories:"
    echo "1. core_services   - ASM Core/Backend Services (topology, merge, status, inventory)"
    echo "2. observers       - Observer Components & Patterns"
    echo "3. ui             - ASM UI Components & Frontend"
    echo "4. documentation  - ASM Documentation & Guides"
    echo ""
    
    read -p "Select category (1-4): " category_choice
    
    case $category_choice in
        1) category="core_services" ;;
        2) category="observers" ;;
        3) category="ui" ;;
        4) category="documentation" ;;
        *) echo "Invalid choice"; return 1 ;;
    esac
    
    echo ""
    read -p "Repository name (e.g., asm-topology-service): " repo_name
    read -p "Full path to repository: " repo_path
    
    # Validate path exists
    if [ ! -d "$repo_path" ]; then
        echo -e "${RED}❌ Path does not exist: $repo_path${NC}"
        return 1
    fi
    
    # Validate it's a git repository
    if [ ! -d "$repo_path/.git" ]; then
        echo -e "${RED}❌ Not a git repository: $repo_path${NC}"
        return 1
    fi
    
    # Update config file using python
    python3 -c "
import json
import sys

try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
except:
    config = {'repository_paths': {}}

if 'repository_paths' not in config:
    config['repository_paths'] = {}

if '$category' not in config['repository_paths']:
    config['repository_paths']['$category'] = {}

config['repository_paths']['$category']['$repo_name'] = '$repo_path'

with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)

print('Config updated successfully')
"
    
    echo -e "${GREEN}✅ Path mapping added${NC}"
    echo "   Category: $category"
    echo "   Repository: $repo_name"
    echo "   Path: $repo_path"
    echo ""
}

# Function to list all path mappings
list_mappings() {
    echo -e "${BLUE}📋 Current ASM Repository Path Mappings${NC}"
    echo ""
    
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${YELLOW}⚠️  No mappings configured yet${NC}"
        echo "   Run: $0 --add-mapping to add repository paths"
        return
    fi
    
    # Use python to parse and display the JSON config
    python3 -c "
import json
import os

try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
    
    repo_paths = config.get('repository_paths', {})
    
    if not repo_paths:
        print('⚠️  No mappings configured yet')
        exit(0)
    
    total_repos = 0
    for category, repos in repo_paths.items():
        print(f'📁 {category}/')
        for repo_name, repo_path in repos.items():
            exists = '✅' if os.path.exists(repo_path) else '❌'
            is_git = '📂' if os.path.exists(os.path.join(repo_path, '.git')) else '❓'
            print(f'   {exists} {is_git} {repo_name}')
            print(f'      → {repo_path}')
            total_repos += 1
        print()
    
    print(f'📈 Total mapped repositories: {total_repos}')
    
except Exception as e:
    print(f'Error reading config: {e}')
"
}

# Function to remove path mapping
remove_mapping() {
    echo -e "${BLUE}🗑️ Remove ASM Repository Path Mapping${NC}"
    echo ""
    
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${YELLOW}⚠️  No mappings configured yet${NC}"
        return
    fi
    
    list_mappings
    echo ""
    
    read -p "Category to remove from: " category
    read -p "Repository name to remove: " repo_name
    
    # Remove using python
    python3 -c "
import json

try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
    
    repo_paths = config.get('repository_paths', {})
    
    if '$category' in repo_paths and '$repo_name' in repo_paths['$category']:
        del repo_paths['$category']['$repo_name']
        
        # Remove empty categories
        if not repo_paths['$category']:
            del repo_paths['$category']
        
        with open('$CONFIG_FILE', 'w') as f:
            json.dump(config, f, indent=2)
        
        print('✅ Mapping removed successfully')
    else:
        print('❌ Mapping not found')
        
except Exception as e:
    print(f'Error: {e}')
"
}

# Function to show help
show_help() {
    echo "ASM Local Repository Manager"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help"
    echo "  -i, --init           Initialize repository system (directory or path mapping)"
    echo "  -u, --update         Update all repositories"
    echo "  -s, --status         Show status of all repositories"
    echo "  -a, --analyze        Analyze repositories for knowledge extraction"
    echo "  --setup-cron         Setup weekly update cron job"
    echo ""
    echo "Path Mapping Options:"
    echo "  --add-mapping        Map path to existing ASM repository"
    echo "  --list-mappings      List all configured repository paths"
    echo "  --remove-mapping     Remove repository path mapping"
    echo ""
    echo "Examples:"
    echo "  $0 --init                    # Setup system (choose approach)"
    echo "  $0 --add-mapping            # Map existing ASM repo"
    echo "  $0 --list-mappings          # View all mappings"
    echo "  $0 --update                 # Update all repos (any approach)"
    echo "  $0 --analyze                # Extract knowledge"
}

# Function to initialize repository structure
init_repos() {
    echo -e "${BLUE}🔧 Initializing ASM Repository Structure${NC}"
    echo ""
    
    echo "Choose your approach:"
    echo ""
    echo "📂 Option 1: Directory Structure (copies repos into project)"
    echo "   • Creates directories under: $LOCAL_REPOS_DIR"
    echo "   • Requires cloning/copying repositories into project"
    echo "   • Good for: Testing, isolated environments"
    echo ""
    echo "🔗 Option 2: Path Mapping (links to existing repos)"
    echo "   • Maps existing repository locations"
    echo "   • Preserves your original repository locations"
    echo "   • Good for: Production, existing setups"
    echo ""
    
    read -p "Select approach (1 or 2): " approach
    
    case $approach in
        1)
            # Create ASM-specific directory structure  
            mkdir -p "$LOCAL_REPOS_DIR/core_services"
            mkdir -p "$LOCAL_REPOS_DIR/observers" 
            mkdir -p "$LOCAL_REPOS_DIR/ui"
            mkdir -p "$LOCAL_REPOS_DIR/documentation"
            
            echo -e "${GREEN}✅ Directory structure created${NC}"
            echo ""
            echo "📁 ASM Repository Structure:"
            echo "   • $LOCAL_REPOS_DIR/core_services/  - ASM Core/Backend Services"
            echo "   • $LOCAL_REPOS_DIR/observers/      - Observer Components"
            echo "   • $LOCAL_REPOS_DIR/ui/             - ASM UI Components"
            echo "   • $LOCAL_REPOS_DIR/documentation/  - ASM Documentation"
            echo ""
            echo -e "${YELLOW}📝 Next Steps:${NC}"
            echo "1. Clone your ASM repositories into the appropriate directories"
            echo "2. Run: $0 --setup-cron (to setup automatic updates)"
            echo "3. Run: $0 --analyze (to extract knowledge)"
            ;;
        2)
            # Initialize empty config for path mapping
            echo '{"repository_paths": {}}' > "$CONFIG_FILE"
            
            echo -e "${GREEN}✅ Path mapping system initialized${NC}"
            echo ""
            echo -e "${YELLOW}📝 Next Steps:${NC}"
            echo "1. Run: $0 --add-mapping (to map your existing repositories)"
            echo "2. Run: $0 --list-mappings (to view configured paths)"
            echo "3. Run: $0 --analyze (to extract knowledge from mapped repos)"
            ;;
        *)
            echo -e "${RED}❌ Invalid choice${NC}"
            return 1
            ;;
    esac
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
    --add-mapping)
        add_path_mapping
        ;;
    --list-mappings)
        list_mappings
        ;;
    --remove-mapping)
        remove_mapping
        ;;
    *)
        echo -e "${YELLOW}ℹ️  ASM Local Repository Manager${NC}"
        echo ""
        show_status
        echo ""
        echo "Run '$0 --help' for available options"
        ;;
esac