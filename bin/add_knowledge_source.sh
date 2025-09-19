#!/bin/bash

# GitHub Knowledge Source Manager
# Manages dynamic repository sources for Knowledge Fusion

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GITHUB_SOURCES_FILE="$PROJECT_ROOT/github_sources.yml"
REPOS_DIR="$PROJECT_ROOT/data/repositories"
SOURCES_REGISTRY="$PROJECT_ROOT/data/sources_registry.json"

# Ensure directories exist
mkdir -p "$REPOS_DIR"
mkdir -p "$(dirname "$SOURCES_REGISTRY")"

# Initialize sources registry if it doesn't exist
if [ ! -f "$SOURCES_REGISTRY" ]; then
    echo '{"repositories": {}, "last_updated": "", "update_schedule": "3days"}' > "$SOURCES_REGISTRY"
fi

show_help() {
    echo -e "${BLUE}GitHub Knowledge Source Manager${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  add-repo     Add a new GitHub repository"
    echo "  remove-repo  Remove a repository"
    echo "  list-repos   List all managed repositories"
    echo "  update-repo  Update specific repository"
    echo "  update-all   Update all repositories"
    echo "  status       Show repository status"
    echo "  schedule     Configure update schedule"
    echo ""
    echo "Options:"
    echo "  --url=URL              Repository URL"
    echo "  --name=NAME            Repository name/alias"
    echo "  --focus=FOCUS          Knowledge focus area"
    echo "  --description=DESC     Repository description"
    echo "  --private              Mark as private repository"
    echo "  --schedule=FREQUENCY   Update frequency (1day, 3days, 1week)"
    echo "  --force                Force operation"
    echo ""
    echo "Examples:"
    echo "  $0 add-repo --url=https://github.com/company/project --name=company-project --focus=backend"
    echo "  $0 update-all"
    echo "  $0 status"
    echo "  $0 schedule --schedule=1day"
}

# Parse command line arguments
parse_args() {
    COMMAND=""
    URL=""
    NAME=""
    FOCUS=""
    DESCRIPTION=""
    PRIVATE=false
    SCHEDULE=""
    FORCE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            add-repo|remove-repo|list-repos|update-repo|update-all|status|schedule|help)
                COMMAND="$1"
                shift
                ;;
            --url=*)
                URL="${1#*=}"
                shift
                ;;
            --name=*)
                NAME="${1#*=}"
                shift
                ;;
            --focus=*)
                FOCUS="${1#*=}"
                shift
                ;;
            --description=*)
                DESCRIPTION="${1#*=}"
                shift
                ;;
            --schedule=*)
                SCHEDULE="${1#*=}"
                shift
                ;;
            --private)
                PRIVATE=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
}

# Extract repository name from URL
extract_repo_name() {
    local url="$1"
    echo "$url" | sed -E 's|.*/([^/]+/[^/]+)\.git$|\1|' | sed -E 's|.*/([^/]+/[^/]+)$|\1|'
}

# Add new repository
add_repository() {
    if [ -z "$URL" ]; then
        echo -e "${RED}❌ Repository URL is required${NC}"
        exit 1
    fi
    
    if [ -z "$NAME" ]; then
        NAME=$(extract_repo_name "$URL" | tr '/' '-')
    fi
    
    if [ -z "$FOCUS" ]; then
        FOCUS="general"
    fi
    
    if [ -z "$DESCRIPTION" ]; then
        DESCRIPTION="GitHub repository: $URL"
    fi
    
    local repo_dir="$REPOS_DIR/$NAME"
    
    echo -e "${BLUE}📦 Adding repository: $NAME${NC}"
    echo -e "   URL: $URL"
    echo -e "   Focus: $FOCUS"
    echo -e "   Directory: $repo_dir"
    
    # Check if repository already exists
    if [ -d "$repo_dir" ] && [ "$FORCE" != true ]; then
        echo -e "${YELLOW}⚠️  Repository directory already exists. Use --force to override.${NC}"
        exit 1
    fi
    
    # Clone repository
    echo -e "${BLUE}🔄 Cloning repository...${NC}"
    if [ -d "$repo_dir" ]; then
        rm -rf "$repo_dir"
    fi
    
    if git clone --depth 1 "$URL" "$repo_dir"; then
        echo -e "${GREEN}✅ Repository cloned successfully${NC}"
    else
        echo -e "${RED}❌ Failed to clone repository${NC}"
        exit 1
    fi
    
    # Update registry
    echo -e "${BLUE}📝 Updating sources registry...${NC}"
    update_registry "$NAME" "$URL" "$FOCUS" "$DESCRIPTION" "$PRIVATE"
    
    # Update YAML configuration
    update_yaml_config "$NAME" "$URL" "$FOCUS" "$DESCRIPTION" "$PRIVATE"
    
    echo -e "${GREEN}✅ Repository added successfully${NC}"
}

# Update sources registry JSON
update_registry() {
    local name="$1"
    local url="$2"
    local focus="$3"
    local description="$4"
    local private="$5"
    
    local current_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Create new entry
    local entry=$(cat <<EOF
{
    "url": "$url",
    "focus": "$focus",
    "description": "$description",
    "private": $private,
    "added_date": "$current_time",
    "last_updated": "$current_time",
    "status": "active",
    "local_path": "data/repositories/$name"
}
EOF
)
    
    # Update JSON using Python
    python3 -c "
import json
import sys

try:
    with open('$SOURCES_REGISTRY', 'r') as f:
        data = json.load(f)
    
    data['repositories']['$name'] = $entry
    data['last_updated'] = '$current_time'
    
    with open('$SOURCES_REGISTRY', 'w') as f:
        json.dump(data, f, indent=2)
        
    print('Registry updated successfully')
except Exception as e:
    print(f'Error updating registry: {e}')
    sys.exit(1)
" || echo -e "${YELLOW}⚠️  Could not update JSON registry${NC}"
}

# Update YAML configuration
update_yaml_config() {
    local name="$1"
    local url="$2"
    local focus="$3"
    local description="$4"
    local private="$5"
    
    # Add entry to YAML (simple append for now)
    cat >> "$GITHUB_SOURCES_FILE" << EOF

  # Added by add_knowledge_source.sh on $(date)
  $name:
    repositories:
      - url: "$url"
        focus: "$focus"
        extraction_method: "code_analysis"
        auth_required: $private
        description: "$description"
EOF
    
    echo -e "${GREEN}✅ YAML configuration updated${NC}"
}

# List all repositories
list_repositories() {
    echo -e "${BLUE}📋 Managed Repositories${NC}"
    echo -e "${BLUE}=====================${NC}"
    
    if [ ! -f "$SOURCES_REGISTRY" ]; then
        echo -e "${YELLOW}No repositories configured${NC}"
        return
    fi
    
    python3 -c "
import json
import os

try:
    with open('$SOURCES_REGISTRY', 'r') as f:
        data = json.load(f)
    
    repos = data.get('repositories', {})
    if not repos:
        print('${YELLOW}No repositories configured${NC}')
        exit(0)
    
    for name, info in repos.items():
        entry = json.loads(info) if isinstance(info, str) else info
        status = '✅' if os.path.exists(entry.get('local_path', '')) else '❌'
        print(f'{status} {name}')
        print(f'   URL: {entry.get(\"url\", \"N/A\")}')
        print(f'   Focus: {entry.get(\"focus\", \"N/A\")}')
        print(f'   Last Updated: {entry.get(\"last_updated\", \"N/A\")}')
        print('')
        
except Exception as e:
    print(f'Error reading registry: {e}')
" 2>/dev/null || echo -e "${YELLOW}Could not read repositories${NC}"
}

# Update all repositories
update_all_repositories() {
    echo -e "${BLUE}🔄 Updating all repositories...${NC}"
    
    if [ ! -d "$REPOS_DIR" ]; then
        echo -e "${YELLOW}No repositories directory found${NC}"
        return
    fi
    
    local count=0
    for repo_dir in "$REPOS_DIR"/*; do
        if [ -d "$repo_dir" ]; then
            local repo_name=$(basename "$repo_dir")
            echo -e "${BLUE}📦 Updating: $repo_name${NC}"
            
            cd "$repo_dir"
            if git pull --rebase; then
                echo -e "   ${GREEN}✅ Updated successfully${NC}"
                ((count++))
            else
                echo -e "   ${RED}❌ Update failed${NC}"
            fi
            cd - > /dev/null
        fi
    done
    
    echo -e "${GREEN}✅ Updated $count repositories${NC}"
    
    # Update last updated timestamp
    local current_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    python3 -c "
import json
try:
    with open('$SOURCES_REGISTRY', 'r') as f:
        data = json.load(f)
    data['last_updated'] = '$current_time'
    with open('$SOURCES_REGISTRY', 'w') as f:
        json.dump(data, f, indent=2)
except:
    pass
" 2>/dev/null
}

# Show status
show_status() {
    echo -e "${BLUE}📊 Knowledge Sources Status${NC}"
    echo -e "${BLUE}============================${NC}"
    
    local total_repos=$(find "$REPOS_DIR" -maxdepth 1 -type d 2>/dev/null | wc -l)
    ((total_repos--)) # Subtract the parent directory
    
    echo -e "📁 Total Repositories: $total_repos"
    echo -e "📂 Storage Location: $REPOS_DIR"
    echo -e "📋 Registry: $SOURCES_REGISTRY"
    echo -e "⚙️  Configuration: $GITHUB_SOURCES_FILE"
    
    if [ -f "$SOURCES_REGISTRY" ]; then
        python3 -c "
import json
try:
    with open('$SOURCES_REGISTRY', 'r') as f:
        data = json.load(f)
    
    last_updated = data.get('last_updated', 'Never')
    schedule = data.get('update_schedule', 'Not set')
    
    print(f'🕒 Last Updated: {last_updated}')
    print(f'⏰ Update Schedule: {schedule}')
    
except:
    print('📄 Registry Status: Error reading')
" 2>/dev/null
    fi
    
    echo ""
    list_repositories
}

# Configure update schedule
configure_schedule() {
    if [ -z "$SCHEDULE" ]; then
        echo -e "${RED}❌ Schedule frequency is required${NC}"
        echo -e "Valid options: 1day, 3days, 1week"
        exit 1
    fi
    
    case "$SCHEDULE" in
        1day|3days|1week)
            echo -e "${BLUE}⏰ Configuring update schedule: $SCHEDULE${NC}"
            
            python3 -c "
import json
try:
    with open('$SOURCES_REGISTRY', 'r') as f:
        data = json.load(f)
    
    data['update_schedule'] = '$SCHEDULE'
    
    with open('$SOURCES_REGISTRY', 'w') as f:
        json.dump(data, f, indent=2)
    
    print('${GREEN}✅ Schedule updated successfully${NC}')
    
except Exception as e:
    print(f'${RED}❌ Error updating schedule: {e}${NC}')
" 2>/dev/null || echo -e "${RED}❌ Failed to update schedule${NC}"
            
            # TODO: Add cron job configuration here
            echo -e "${YELLOW}💡 To enable automatic updates, add this to your crontab:${NC}"
            case "$SCHEDULE" in
                1day)
                    echo -e "   ${BLUE}0 2 * * * cd $PROJECT_ROOT && ./add_knowledge_source.sh update-all${NC}"
                    ;;
                3days)
                    echo -e "   ${BLUE}0 2 */3 * * cd $PROJECT_ROOT && ./add_knowledge_source.sh update-all${NC}"
                    ;;
                1week)
                    echo -e "   ${BLUE}0 2 * * 0 cd $PROJECT_ROOT && ./add_knowledge_source.sh update-all${NC}"
                    ;;
            esac
            ;;
        *)
            echo -e "${RED}❌ Invalid schedule: $SCHEDULE${NC}"
            echo -e "Valid options: 1day, 3days, 1week"
            exit 1
            ;;
    esac
}

# Main execution
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    parse_args "$@"
    
    case "$COMMAND" in
        add-repo)
            add_repository
            ;;
        remove-repo)
            echo -e "${YELLOW}🚧 Remove functionality coming soon${NC}"
            ;;
        list-repos)
            list_repositories
            ;;
        update-repo)
            echo -e "${YELLOW}🚧 Single repo update coming soon${NC}"
            ;;
        update-all)
            update_all_repositories
            ;;
        status)
            show_status
            ;;
        schedule)
            configure_schedule
            ;;
        help|"")
            show_help
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $COMMAND${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"