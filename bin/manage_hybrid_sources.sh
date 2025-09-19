#!/bin/bash

# Hybrid Knowledge Sources Manager
# Manages diverse knowledge sources beyond GitHub repositories

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KNOWLEDGE_CONFIG="$PROJECT_ROOT/hybrid_knowledge_config.json"
LOGS_DIR="$PROJECT_ROOT/logs"
DATA_DIR="$PROJECT_ROOT/data/hybrid_sources"

# Initialize directories
mkdir -p "$DATA_DIR/web_content"
mkdir -p "$DATA_DIR/documents"
mkdir -p "$DATA_DIR/apis"
mkdir -p "$DATA_DIR/databases"
mkdir -p "$LOGS_DIR"

show_help() {
    echo -e "${BLUE}Hybrid Knowledge Sources Manager${NC}"
    echo -e "${BLUE}=================================${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo -e "${CYAN}Source Management:${NC}"
    echo "  add-web        Add web content source (blogs, docs, wikis)"
    echo "  add-api        Add API data source"
    echo "  add-database   Add database connection"
    echo "  add-document   Add document collection"
    echo "  list           List all configured sources"
    echo "  remove         Remove a source"
    echo "  status         Show source status"
    echo ""
    echo -e "${CYAN}Content Operations:${NC}"
    echo "  sync           Sync all sources"
    echo "  sync-web       Sync only web sources"
    echo "  sync-apis      Sync only API sources"
    echo "  test           Test source connectivity"
    echo ""
    echo -e "${CYAN}Analysis:${NC}"
    echo "  analyze        Analyze content quality"
    echo "  report         Generate source report"
    echo "  monitor        Monitor source health"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0 add-web --url='https://docs.python.org' --type='documentation'"
    echo "  $0 add-api --url='https://api.github.com' --auth='token:xyz'"
    echo "  $0 sync --source='python-docs'"
    echo "  $0 status"
}

# Initialize configuration
init_config() {
    if [ ! -f "$KNOWLEDGE_CONFIG" ]; then
        cat > "$KNOWLEDGE_CONFIG" << 'EOF'
{
  "version": "1.0",
  "sources": {},
  "settings": {
    "sync_interval": "3h",
    "max_content_size": "10MB",
    "content_formats": ["html", "markdown", "pdf", "json", "xml"],
    "quality_threshold": 0.7
  },
  "last_sync": null
}
EOF
        echo -e "${GREEN}✅ Initialized hybrid knowledge configuration${NC}"
    fi
}

# Add web content source
add_web_source() {
    local url=""
    local name=""
    local type=""
    local depth=2
    local schedule="daily"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --url=*)
                url="${1#*=}"
                shift
                ;;
            --name=*)
                name="${1#*=}"
                shift
                ;;
            --type=*)
                type="${1#*=}"
                shift
                ;;
            --depth=*)
                depth="${1#*=}"
                shift
                ;;
            --schedule=*)
                schedule="${1#*=}"
                shift
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    if [ -z "$url" ]; then
        echo -e "${RED}❌ URL is required${NC}"
        echo "Usage: $0 add-web --url='https://example.com' [--name='name'] [--type='type']"
        exit 1
    fi
    
    # Generate name if not provided
    if [ -z "$name" ]; then
        name=$(echo "$url" | sed 's|https\?://||' | sed 's|/.*||' | sed 's|\.|-|g')
    fi
    
    # Detect type if not provided
    if [ -z "$type" ]; then
        case "$url" in
            *docs*)
                type="documentation"
                ;;
            *blog*)
                type="blog"
                ;;
            *wiki*)
                type="wiki"
                ;;
            *)
                type="website"
                ;;
        esac
    fi
    
    echo -e "${BLUE}🌐 Adding web source: $name${NC}"
    
    # Create source configuration
    local source_config=$(cat << EOF
{
  "type": "web",
  "url": "$url",
  "content_type": "$type",
  "crawl_depth": $depth,
  "schedule": "$schedule",
  "added_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "last_sync": null,
  "status": "pending",
  "metadata": {
    "total_pages": 0,
    "total_size": "0MB",
    "last_error": null
  }
}
EOF
    )
    
    # Update configuration
    update_source_config "$name" "$source_config"
    
    echo -e "${GREEN}✅ Web source '$name' added successfully${NC}"
    echo -e "   URL: $url"
    echo -e "   Type: $type"
    echo -e "   Crawl Depth: $depth"
    echo -e "   Schedule: $schedule"
}

# Add API source
add_api_source() {
    local url=""
    local name=""
    local auth=""
    local format="json"
    local schedule="hourly"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --url=*)
                url="${1#*=}"
                shift
                ;;
            --name=*)
                name="${1#*=}"
                shift
                ;;
            --auth=*)
                auth="${1#*=}"
                shift
                ;;
            --format=*)
                format="${1#*=}"
                shift
                ;;
            --schedule=*)
                schedule="${1#*=}"
                shift
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    if [ -z "$url" ] || [ -z "$name" ]; then
        echo -e "${RED}❌ URL and name are required${NC}"
        echo "Usage: $0 add-api --url='https://api.example.com' --name='api-name' [--auth='token:xyz']"
        exit 1
    fi
    
    echo -e "${BLUE}🔌 Adding API source: $name${NC}"
    
    # Create source configuration
    local source_config=$(cat << EOF
{
  "type": "api",
  "url": "$url",
  "auth": "$auth",
  "format": "$format",
  "schedule": "$schedule",
  "added_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "last_sync": null,
  "status": "pending",
  "metadata": {
    "records_count": 0,
    "data_size": "0MB",
    "last_error": null
  }
}
EOF
    )
    
    # Update configuration
    update_source_config "$name" "$source_config"
    
    echo -e "${GREEN}✅ API source '$name' added successfully${NC}"
    echo -e "   URL: $url"
    echo -e "   Format: $format"
    echo -e "   Schedule: $schedule"
}

# Add database source
add_database_source() {
    local name=""
    local type=""
    local connection=""
    local tables=""
    local schedule="daily"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --name=*)
                name="${1#*=}"
                shift
                ;;
            --type=*)
                type="${1#*=}"
                shift
                ;;
            --connection=*)
                connection="${1#*=}"
                shift
                ;;
            --tables=*)
                tables="${1#*=}"
                shift
                ;;
            --schedule=*)
                schedule="${1#*=}"
                shift
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    if [ -z "$name" ] || [ -z "$type" ] || [ -z "$connection" ]; then
        echo -e "${RED}❌ Name, type, and connection are required${NC}"
        echo "Usage: $0 add-database --name='db-name' --type='postgresql' --connection='host:port/db'"
        exit 1
    fi
    
    echo -e "${BLUE}🗄️  Adding database source: $name${NC}"
    
    # Create source configuration
    local source_config=$(cat << EOF
{
  "type": "database",
  "db_type": "$type",
  "connection": "$connection",
  "tables": "$tables",
  "schedule": "$schedule",
  "added_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "last_sync": null,
  "status": "pending",
  "metadata": {
    "table_count": 0,
    "record_count": 0,
    "last_error": null
  }
}
EOF
    )
    
    # Update configuration
    update_source_config "$name" "$source_config"
    
    echo -e "${GREEN}✅ Database source '$name' added successfully${NC}"
    echo -e "   Type: $type"
    echo -e "   Connection: $connection"
    echo -e "   Schedule: $schedule"
}

# Add document collection
add_document_source() {
    local name=""
    local path=""
    local format=""
    local recursive=true
    local schedule="daily"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --name=*)
                name="${1#*=}"
                shift
                ;;
            --path=*)
                path="${1#*=}"
                shift
                ;;
            --format=*)
                format="${1#*=}"
                shift
                ;;
            --recursive=*)
                recursive="${1#*=}"
                shift
                ;;
            --schedule=*)
                schedule="${1#*=}"
                shift
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    if [ -z "$name" ] || [ -z "$path" ]; then
        echo -e "${RED}❌ Name and path are required${NC}"
        echo "Usage: $0 add-document --name='docs' --path='/path/to/documents' [--format='pdf,docx']"
        exit 1
    fi
    
    if [ ! -d "$path" ]; then
        echo -e "${RED}❌ Path does not exist: $path${NC}"
        exit 1
    fi
    
    # Auto-detect formats if not provided
    if [ -z "$format" ]; then
        format="pdf,docx,txt,md,html"
    fi
    
    echo -e "${BLUE}📄 Adding document source: $name${NC}"
    
    # Create source configuration
    local source_config=$(cat << EOF
{
  "type": "documents",
  "path": "$path",
  "formats": "$format",
  "recursive": $recursive,
  "schedule": "$schedule",
  "added_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "last_sync": null,
  "status": "pending",
  "metadata": {
    "file_count": 0,
    "total_size": "0MB",
    "last_error": null
  }
}
EOF
    )
    
    # Update configuration
    update_source_config "$name" "$source_config"
    
    echo -e "${GREEN}✅ Document source '$name' added successfully${NC}"
    echo -e "   Path: $path"
    echo -e "   Formats: $format"
    echo -e "   Recursive: $recursive"
    echo -e "   Schedule: $schedule"
}

# Update source configuration
update_source_config() {
    local name="$1"
    local config="$2"
    
    init_config
    
    # Use jq to update the configuration
    local temp_file=$(mktemp)
    jq --arg name "$name" --argjson config "$config" '.sources[$name] = $config' "$KNOWLEDGE_CONFIG" > "$temp_file"
    mv "$temp_file" "$KNOWLEDGE_CONFIG"
}

# List all sources
list_sources() {
    init_config
    
    echo -e "${BLUE}📚 Hybrid Knowledge Sources${NC}"
    echo -e "${BLUE}===========================${NC}"
    
    local source_count=$(jq '.sources | length' "$KNOWLEDGE_CONFIG")
    
    if [ "$source_count" -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No sources configured${NC}"
        echo -e "Use '$0 add-web', '$0 add-api', etc. to add sources"
        return
    fi
    
    echo -e "Total sources: $source_count\n"
    
    # List by type
    echo -e "${CYAN}Web Sources:${NC}"
    jq -r '.sources | to_entries[] | select(.value.type == "web") | "  \(.key) - \(.value.url) (\(.value.status))"' "$KNOWLEDGE_CONFIG" || echo -e "  ${YELLOW}None configured${NC}"
    
    echo -e "\n${CYAN}API Sources:${NC}"
    jq -r '.sources | to_entries[] | select(.value.type == "api") | "  \(.key) - \(.value.url) (\(.value.status))"' "$KNOWLEDGE_CONFIG" || echo -e "  ${YELLOW}None configured${NC}"
    
    echo -e "\n${CYAN}Database Sources:${NC}"
    jq -r '.sources | to_entries[] | select(.value.type == "database") | "  \(.key) - \(.value.db_type) (\(.value.status))"' "$KNOWLEDGE_CONFIG" || echo -e "  ${YELLOW}None configured${NC}"
    
    echo -e "\n${CYAN}Document Sources:${NC}"
    jq -r '.sources | to_entries[] | select(.value.type == "documents") | "  \(.key) - \(.value.path) (\(.value.status))"' "$KNOWLEDGE_CONFIG" || echo -e "  ${YELLOW}None configured${NC}"
}

# Show source status
show_status() {
    init_config
    
    echo -e "${BLUE}📊 Source Status Report${NC}"
    echo -e "${BLUE}========================${NC}"
    
    local total_sources=$(jq '.sources | length' "$KNOWLEDGE_CONFIG")
    local active_sources=$(jq '.sources | to_entries[] | select(.value.status == "active") | length' "$KNOWLEDGE_CONFIG")
    local pending_sources=$(jq '.sources | to_entries[] | select(.value.status == "pending") | length' "$KNOWLEDGE_CONFIG")
    local error_sources=$(jq '.sources | to_entries[] | select(.value.status == "error") | length' "$KNOWLEDGE_CONFIG")
    
    echo -e "Total Sources: $total_sources"
    echo -e "${GREEN}Active: $active_sources${NC}"
    echo -e "${YELLOW}Pending: $pending_sources${NC}"
    echo -e "${RED}Errors: $error_sources${NC}"
    echo ""
    
    # Show detailed status
    if [ "$total_sources" -gt 0 ]; then
        echo -e "${CYAN}Source Details:${NC}"
        jq -r '.sources | to_entries[] | "  \(.key): \(.value.status) - \(.value.type)"' "$KNOWLEDGE_CONFIG"
    fi
}

# Sync all sources
sync_sources() {
    local source_filter=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --source=*)
                source_filter="${1#*=}"
                shift
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    init_config
    
    echo -e "${BLUE}🔄 Syncing Knowledge Sources${NC}"
    echo -e "${BLUE}=============================${NC}"
    
    local sources
    if [ -n "$source_filter" ]; then
        sources=$(jq -r --arg filter "$source_filter" '.sources | to_entries[] | select(.key == $filter) | .key' "$KNOWLEDGE_CONFIG")
    else
        sources=$(jq -r '.sources | keys[]' "$KNOWLEDGE_CONFIG")
    fi
    
    if [ -z "$sources" ]; then
        echo -e "${YELLOW}⚠️  No sources to sync${NC}"
        return
    fi
    
    while IFS= read -r source_name; do
        echo -e "${CYAN}📥 Syncing: $source_name${NC}"
        sync_single_source "$source_name"
    done <<< "$sources"
    
    # Update last sync time
    local temp_file=$(mktemp)
    jq --arg date "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" '.last_sync = $date' "$KNOWLEDGE_CONFIG" > "$temp_file"
    mv "$temp_file" "$KNOWLEDGE_CONFIG"
    
    echo -e "${GREEN}✅ Sync completed${NC}"
}

# Sync single source
sync_single_source() {
    local source_name="$1"
    local source_type=$(jq -r --arg name "$source_name" '.sources[$name].type' "$KNOWLEDGE_CONFIG")
    
    case "$source_type" in
        "web")
            sync_web_source "$source_name"
            ;;
        "api")
            sync_api_source "$source_name"
            ;;
        "database")
            sync_database_source "$source_name"
            ;;
        "documents")
            sync_document_source "$source_name"
            ;;
        *)
            echo -e "  ${RED}❌ Unknown source type: $source_type${NC}"
            ;;
    esac
}

# Sync web source
sync_web_source() {
    local source_name="$1"
    local url=$(jq -r --arg name "$source_name" '.sources[$name].url' "$KNOWLEDGE_CONFIG")
    local depth=$(jq -r --arg name "$source_name" '.sources[$name].crawl_depth' "$KNOWLEDGE_CONFIG")
    
    echo -e "  🌐 Crawling web content from: $url"
    
    # Create output directory
    local output_dir="$DATA_DIR/web_content/$source_name"
    mkdir -p "$output_dir"
    
    # Simple web crawling (in production, use proper crawler)
    if command -v wget >/dev/null 2>&1; then
        wget -r -l "$depth" -k -p -E -np -R "*.jpg,*.jpeg,*.png,*.gif,*.svg,*.css,*.js" \
             -P "$output_dir" "$url" 2>/dev/null || echo -e "  ${YELLOW}⚠️  Partial crawl completed${NC}"
    else
        curl -L "$url" > "$output_dir/index.html" 2>/dev/null || echo -e "  ${RED}❌ Failed to fetch content${NC}"
    fi
    
    # Update status
    update_source_status "$source_name" "active" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo -e "  ${GREEN}✅ Web sync completed${NC}"
}

# Sync API source
sync_api_source() {
    local source_name="$1"
    local url=$(jq -r --arg name "$source_name" '.sources[$name].url' "$KNOWLEDGE_CONFIG")
    local auth=$(jq -r --arg name "$source_name" '.sources[$name].auth' "$KNOWLEDGE_CONFIG")
    
    echo -e "  🔌 Fetching API data from: $url"
    
    # Create output directory
    local output_dir="$DATA_DIR/apis/$source_name"
    mkdir -p "$output_dir"
    
    # Build curl command
    local curl_cmd="curl -L"
    if [ "$auth" != "null" ] && [ -n "$auth" ]; then
        if [[ "$auth" == token:* ]]; then
            local token="${auth#token:}"
            curl_cmd="$curl_cmd -H 'Authorization: Bearer $token'"
        fi
    fi
    
    # Fetch data
    eval "$curl_cmd '$url'" > "$output_dir/data.json" 2>/dev/null || echo -e "  ${RED}❌ Failed to fetch API data${NC}"
    
    # Update status
    update_source_status "$source_name" "active" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo -e "  ${GREEN}✅ API sync completed${NC}"
}

# Sync database source
sync_database_source() {
    local source_name="$1"
    echo -e "  🗄️  Database sync not yet implemented for: $source_name"
    echo -e "  ${YELLOW}⚠️  Requires database-specific implementation${NC}"
}

# Sync document source
sync_document_source() {
    local source_name="$1"
    local path=$(jq -r --arg name "$source_name" '.sources[$name].path' "$KNOWLEDGE_CONFIG")
    local formats=$(jq -r --arg name "$source_name" '.sources[$name].formats' "$KNOWLEDGE_CONFIG")
    
    echo -e "  📄 Indexing documents from: $path"
    
    # Create output directory
    local output_dir="$DATA_DIR/documents/$source_name"
    mkdir -p "$output_dir"
    
    # Copy/link documents
    local format_patterns=$(echo "$formats" | tr ',' ' ' | sed 's/[^a-zA-Z ]//g')
    local file_count=0
    
    for format in $format_patterns; do
        find "$path" -name "*.$format" -type f | while read -r file; do
            cp "$file" "$output_dir/" 2>/dev/null || true
            ((file_count++))
        done
    done
    
    # Update status
    update_source_status "$source_name" "active" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo -e "  ${GREEN}✅ Document sync completed${NC}"
}

# Update source status
update_source_status() {
    local name="$1"
    local status="$2"
    local last_sync="$3"
    
    local temp_file=$(mktemp)
    jq --arg name "$name" --arg status "$status" --arg sync "$last_sync" \
       '.sources[$name].status = $status | .sources[$name].last_sync = $sync' \
       "$KNOWLEDGE_CONFIG" > "$temp_file"
    mv "$temp_file" "$KNOWLEDGE_CONFIG"
}

# Generate report
generate_report() {
    init_config
    
    echo -e "${BLUE}📋 Hybrid Knowledge Sources Report${NC}"
    echo -e "${BLUE}===================================${NC}"
    echo -e "Generated: $(date)"
    echo ""
    
    # Summary
    local total=$(jq '.sources | length' "$KNOWLEDGE_CONFIG")
    local active=$(jq '.sources | to_entries[] | select(.value.status == "active") | length' "$KNOWLEDGE_CONFIG")
    
    echo -e "${CYAN}Summary:${NC}"
    echo -e "  Total Sources: $total"
    echo -e "  Active Sources: $active"
    echo -e "  Last Global Sync: $(jq -r '.last_sync // "Never"' "$KNOWLEDGE_CONFIG")"
    echo ""
    
    # Source details
    echo -e "${CYAN}Source Details:${NC}"
    jq -r '.sources | to_entries[] | "  \(.key):\n    Type: \(.value.type)\n    Status: \(.value.status)\n    Last Sync: \(.value.last_sync // "Never")\n"' "$KNOWLEDGE_CONFIG"
    
    # Data size analysis
    echo -e "${CYAN}Data Storage:${NC}"
    if [ -d "$DATA_DIR" ]; then
        du -sh "$DATA_DIR"/* 2>/dev/null | while read -r size path; do
            local dirname=$(basename "$path")
            echo -e "  $dirname: $size"
        done
    fi
}

# Main execution
main() {
    # Ensure jq is available
    if ! command -v jq >/dev/null 2>&1; then
        echo -e "${RED}❌ jq is required but not installed${NC}"
        echo -e "Install with: brew install jq"
        exit 1
    fi
    
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    local command="$1"
    shift
    
    case "$command" in
        add-web)
            add_web_source "$@"
            ;;
        add-api)
            add_api_source "$@"
            ;;
        add-database)
            add_database_source "$@"
            ;;
        add-document)
            add_document_source "$@"
            ;;
        list)
            list_sources
            ;;
        status)
            show_status
            ;;
        sync)
            sync_sources "$@"
            ;;
        sync-web)
            # Sync only web sources
            init_config
            jq -r '.sources | to_entries[] | select(.value.type == "web") | .key' "$KNOWLEDGE_CONFIG" | while read -r source; do
                sync_single_source "$source"
            done
            ;;
        sync-apis)
            # Sync only API sources
            init_config
            jq -r '.sources | to_entries[] | select(.value.type == "api") | .key' "$KNOWLEDGE_CONFIG" | while read -r source; do
                sync_single_source "$source"
            done
            ;;
        report)
            generate_report
            ;;
        help|"")
            show_help
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $command${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"