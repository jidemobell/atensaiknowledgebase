#!/bin/bash

# =============================================================================
# TOPOLOGY KNOWLEDGE - GLOBAL LOG VIEWER (macOS Compatible)
# =============================================================================
# This script provides a unified view of all service logs with real-time
# monitoring, filtering, and search capabilities
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS_DIR="$PROJECT_ROOT/logs"

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

# Function to get log file for service
get_log_file() {
    case "$1" in
        "CoreBackend") echo "$LOGS_DIR/core_backend.log" ;;
        "OpenWebUI") echo "$LOGS_DIR/openwebui.log" ;;
        "KnowledgeFusion") echo "$LOGS_DIR/knowledge_fusion.log" ;;
        "Ollama") echo "$LOGS_DIR/ollama.log" ;;
        "System") echo "$LOGS_DIR/system.log" ;;
        *) echo "" ;;
    esac
}

# Function to get color for service
get_service_color() {
    case "$1" in
        "CoreBackend") echo "$BLUE" ;;
        "OpenWebUI") echo "$GREEN" ;;
        "KnowledgeFusion") echo "$PURPLE" ;;
        "Ollama") echo "$CYAN" ;;
        "System") echo "$YELLOW" ;;
        *) echo "$NC" ;;
    esac
}

# List of all services
ALL_SERVICES="CoreBackend OpenWebUI KnowledgeFusion Ollama System"

show_help() {
    echo -e "${BLUE}🔍 Topology Knowledge - Global Log Viewer${NC}"
    echo -e "${BLUE}===========================================${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -f, --follow         Follow logs in real-time (like tail -f)"
    echo "  -s, --service NAME   Show logs from specific service only"
    echo "                       (CoreBackend, OpenWebUI, KnowledgeFusion, Ollama, System)"
    echo "  -g, --grep PATTERN   Filter logs containing pattern"
    echo "  -e, --errors         Show only error messages"
    echo "  -w, --warnings       Show warnings and errors"
    echo "  -l, --lines N        Show last N lines from each log (default: 50)"
    echo "  -c, --clear          Clear all log files"
    echo "  -z, --size           Show log file sizes"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                   # Show recent logs from all services"
    echo "  $0 -f                # Follow all logs in real-time"
    echo "  $0 -s OpenWebUI -f   # Follow only OpenWebUI logs"
    echo "  $0 -e                # Show only errors"
    echo "  $0 -g \"Knowledge\"    # Show logs containing 'Knowledge'"
    echo "  $0 -l 100            # Show last 100 lines from each service"
}

check_log_sizes() {
    echo -e "${BLUE}📊 Log File Sizes${NC}"
    echo -e "${BLUE}=================${NC}"
    
    for service in $ALL_SERVICES; do
        log_file=$(get_log_file "$service")
        if [ -f "$log_file" ]; then
            size=$(du -h "$log_file" | cut -f1)
            lines=$(wc -l < "$log_file" 2>/dev/null || echo "0")
            color=$(get_service_color "$service")
            echo -e "${color}$service:${NC} $size ($lines lines)"
        else
            color=$(get_service_color "$service")
            echo -e "${color}$service:${NC} No log file"
        fi
    done
    echo ""
}

clear_logs() {
    echo -e "${YELLOW}🧹 Clearing all log files...${NC}"
    
    for service in $ALL_SERVICES; do
        log_file=$(get_log_file "$service")
        if [ -f "$log_file" ]; then
            > "$log_file"
            color=$(get_service_color "$service")
            echo -e "${color}✅ Cleared $service log${NC}"
        fi
    done
    echo -e "${GREEN}All logs cleared!${NC}"
}

format_log_line() {
    local service=$1
    local line=$2
    local color=$(get_service_color "$service")
    local timestamp=$(date "+%H:%M:%S")
    
    echo -e "${color}[$timestamp][$service]${NC} $line"
}

show_service_logs() {
    local service=$1
    local lines=${2:-50}
    local filter_pattern=$3
    local error_only=$4
    local warning_only=$5
    
    local log_file=$(get_log_file "$service")
    local color=$(get_service_color "$service")
    
    if [ ! -f "$log_file" ]; then
        echo -e "${color}📝 $service: No log file found${NC}"
        return
    fi
    
    echo -e "${color}📝 $service Logs (last $lines lines)${NC}"
    echo -e "${color}$(printf '=%.0s' {1..50})${NC}"
    
    local tail_cmd="tail -n $lines '$log_file'"
    
    # Apply filters
    if [ "$error_only" = true ]; then
        tail_cmd="$tail_cmd | grep -i -E '(error|exception|failed|fatal)'"
    elif [ "$warning_only" = true ]; then
        tail_cmd="$tail_cmd | grep -i -E '(warn|warning|error|exception|failed|fatal)'"
    fi
    
    if [ -n "$filter_pattern" ]; then
        tail_cmd="$tail_cmd | grep -i '$filter_pattern'"
    fi
    
    # Execute command and format output
    eval "$tail_cmd" 2>/dev/null | while IFS= read -r line; do
        format_log_line "$service" "$line"
    done || echo -e "${color}📭 No matching log entries${NC}"
    
    echo ""
}

follow_logs() {
    local specific_service=$1
    local filter_pattern=$2
    local error_only=$3
    local warning_only=$4
    
    echo -e "${BLUE}🔄 Following logs in real-time... (Press Ctrl+C to stop)${NC}"
    echo -e "${BLUE}======================================================${NC}"
    echo ""
    
    # Build tail command for following logs
    local tail_files=()
    
    if [ -n "$specific_service" ]; then
        local log_file=$(get_log_file "$specific_service")
        if [ -f "$log_file" ]; then
            tail_files+=("$log_file")
        fi
    else
        for service in $ALL_SERVICES; do
            local log_file=$(get_log_file "$service")
            if [ -f "$log_file" ]; then
                tail_files+=("$log_file")
            fi
        done
    fi
    
    if [ ${#tail_files[@]} -eq 0 ]; then
        echo -e "${RED}❌ No log files found to follow${NC}"
        return 1
    fi
    
    # Use multitail if available, otherwise fall back to tail
    if command -v multitail >/dev/null 2>&1; then
        echo -e "${GREEN}Using multitail for enhanced viewing${NC}"
        multitail "${tail_files[@]}"
    else
        # Use tail -f with multiple files
        tail -f "${tail_files[@]}" | while IFS= read -r line; do
            # Try to identify which service the log line comes from
            local identified_service=""
            for service in $ALL_SERVICES; do
                local service_log_file=$(get_log_file "$service")
                if [[ "$line" == *"$service_log_file"* ]]; then
                    identified_service="$service"
                    break
                fi
            done
            
            # Apply filters
            if [ "$error_only" = true ] && ! echo "$line" | grep -qi -E '(error|exception|failed|fatal)'; then
                continue
            fi
            
            if [ "$warning_only" = true ] && ! echo "$line" | grep -qi -E '(warn|warning|error|exception|failed|fatal)'; then
                continue
            fi
            
            if [ -n "$filter_pattern" ] && ! echo "$line" | grep -qi "$filter_pattern"; then
                continue
            fi
            
            # Format and display
            if [ -n "$identified_service" ]; then
                format_log_line "$identified_service" "$line"
            else
                echo -e "${NC}$line${NC}"
            fi
        done
    fi
}

show_all_logs() {
    local lines=${1:-50}
    local filter_pattern=$2
    local error_only=$3
    local warning_only=$4
    
    echo -e "${BLUE}📋 Global Log View - All Services${NC}"
    echo -e "${BLUE}==================================${NC}"
    echo ""
    
    # Show log sizes first
    check_log_sizes
    
    # Show logs from each service
    for service in $ALL_SERVICES; do
        local log_file=$(get_log_file "$service")
        if [ -f "$log_file" ]; then
            show_service_logs "$service" "$lines" "$filter_pattern" "$error_only" "$warning_only"
        fi
    done
}

# Parse command line arguments
FOLLOW=false
SPECIFIC_SERVICE=""
FILTER_PATTERN=""
ERROR_ONLY=false
WARNING_ONLY=false
LINES=50
CLEAR_LOGS=false
SHOW_SIZES=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -s|--service)
            SPECIFIC_SERVICE="$2"
            shift 2
            ;;
        -g|--grep)
            FILTER_PATTERN="$2"
            shift 2
            ;;
        -e|--errors)
            ERROR_ONLY=true
            shift
            ;;
        -w|--warnings)
            WARNING_ONLY=true
            shift
            ;;
        -l|--lines)
            LINES="$2"
            shift 2
            ;;
        -c|--clear)
            CLEAR_LOGS=true
            shift
            ;;
        -z|--size)
            SHOW_SIZES=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Execute based on options
if [ "$CLEAR_LOGS" = true ]; then
    clear_logs
    exit 0
fi

if [ "$SHOW_SIZES" = true ]; then
    check_log_sizes
    exit 0
fi

# Validate specific service if provided
if [ -n "$SPECIFIC_SERVICE" ]; then
    valid_service=false
    for service in $ALL_SERVICES; do
        if [ "$service" = "$SPECIFIC_SERVICE" ]; then
            valid_service=true
            break
        fi
    done
    
    if [ "$valid_service" = false ]; then
        echo -e "${RED}❌ Invalid service name: $SPECIFIC_SERVICE${NC}"
        echo -e "${YELLOW}Available services: $ALL_SERVICES${NC}"
        exit 1
    fi
fi

# Main execution
if [ "$FOLLOW" = true ]; then
    follow_logs "$SPECIFIC_SERVICE" "$FILTER_PATTERN" "$ERROR_ONLY" "$WARNING_ONLY"
elif [ -n "$SPECIFIC_SERVICE" ]; then
    show_service_logs "$SPECIFIC_SERVICE" "$LINES" "$FILTER_PATTERN" "$ERROR_ONLY" "$WARNING_ONLY"
else
    show_all_logs "$LINES" "$FILTER_PATTERN" "$ERROR_ONLY" "$WARNING_ONLY"
fi
