#!/bin/bash#!/bin/bash



# Knowledge Fusion Monitoring & Logging System# =============================================================================

# Advanced log viewing and monitoring for Knowledge Fusion services# TOPOLOGY KNOWLEDGE - GLOBAL LOG VIEWER (macOS Compatible)

# =============================================================================

set -euo pipefail# This script provides a unified view of all service logs with real-time

# monitoring, filtering, and search capabilities

# Colors for output# =============================================================================

RED='\033[0;31m'

GREEN='\033[0;32m'set -e

YELLOW='\033[1;33m'

BLUE='\033[0;34m'# Colors for output

PURPLE='\033[0;35m'RED='\033[0;31m'

CYAN='\033[0;36m'GREEN='\033[0;32m'

NC='\033[0m' # No ColorYELLOW='\033[1;33m'

BLUE='\033[0;34m'

# ConfigurationPURPLE='\033[0;35m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CYAN='\033[0;36m'

LOGS_DIR="$PROJECT_ROOT/logs"NC='\033[0m' # No Color

PID_FILE="$PROJECT_ROOT/.topology_pids"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Service definitionsLOGS_DIR="$PROJECT_ROOT/logs"

declare -A SERVICES=(

    ["core-backend"]="$LOGS_DIR/core_backend.log"# Ensure logs directory exists

    ["knowledge-fusion"]="$LOGS_DIR/knowledge_fusion.log"mkdir -p "$LOGS_DIR"

    ["gateway"]="$LOGS_DIR/gateway.log"

    ["monitor"]="$LOGS_DIR/monitor.log"# Function to get log file for service

    ["all"]="$LOGS_DIR/*.log"get_log_file() {

)    case "$1" in

        "CoreBackend") echo "$LOGS_DIR/core_backend.log" ;;

declare -A SERVICE_PORTS=(        "OpenWebUI") echo "$LOGS_DIR/openwebui.log" ;;

    ["core-backend"]="8001"        "KnowledgeFusion") echo "$LOGS_DIR/knowledge_fusion.log" ;;

    ["knowledge-fusion"]="8002"        "Ollama") echo "$LOGS_DIR/ollama.log" ;;

    ["gateway"]="9000"        "System") echo "$LOGS_DIR/system.log" ;;

    ["ollama"]="11434"        *) echo "" ;;

)    esac

}

show_help() {

    echo -e "${BLUE}Knowledge Fusion Monitoring System${NC}"# Function to get color for service

    echo -e "${BLUE}==================================${NC}"get_service_color() {

    echo ""    case "$1" in

    echo "Usage: $0 [COMMAND] [OPTIONS]"        "CoreBackend") echo "$BLUE" ;;

    echo ""        "OpenWebUI") echo "$GREEN" ;;

    echo -e "${CYAN}Log Viewing Commands:${NC}"        "KnowledgeFusion") echo "$PURPLE" ;;

    echo "  logs         View service logs"        "Ollama") echo "$CYAN" ;;

    echo "  tail         Follow live logs"        "System") echo "$YELLOW" ;;

    echo "  errors       Show errors and warnings"        *) echo "$NC" ;;

    echo "  search       Search in logs"    esac

    echo ""}

    echo -e "${CYAN}Monitoring Commands:${NC}"

    echo "  status       Show service status"# List of all services

    echo "  health       Health check all services"ALL_SERVICES="CoreBackend OpenWebUI KnowledgeFusion Ollama System"

    echo "  metrics      Show performance metrics"

    echo "  processes    Show running processes"show_help() {

    echo ""    echo -e "${BLUE}🔍 Topology Knowledge - Global Log Viewer${NC}"

    echo -e "${CYAN}Analysis Commands:${NC}"    echo -e "${BLUE}===========================================${NC}"

    echo "  analyze      Analyze log patterns"    echo ""

    echo "  summary      Generate log summary"    echo "Usage: $0 [OPTIONS]"

    echo "  performance  Performance analysis"    echo ""

    echo ""    echo "Options:"

    echo -e "${CYAN}Options:${NC}"    echo "  -f, --follow         Follow logs in real-time (like tail -f)"

    echo "  --service=NAME     Service name (core-backend, knowledge-fusion, gateway, all)"    echo "  -s, --service NAME   Show logs from specific service only"

    echo "  --level=LEVEL      Log level (info, warn, error, debug)"    echo "                       (CoreBackend, OpenWebUI, KnowledgeFusion, Ollama, System)"

    echo "  --lines=N          Number of lines to show (default: 50)"    echo "  -g, --grep PATTERN   Filter logs containing pattern"

    echo "  --follow           Follow logs in real-time"    echo "  -e, --errors         Show only error messages"

    echo "  --since=TIME       Show logs since time (1h, 30m, 1d)"    echo "  -w, --warnings       Show warnings and errors"

    echo "  --grep=PATTERN     Search pattern"    echo "  -l, --lines N        Show last N lines from each log (default: 50)"

    echo "  --json             Output in JSON format"    echo "  -c, --clear          Clear all log files"

    echo ""    echo "  -z, --size           Show log file sizes"

    echo -e "${CYAN}Examples:${NC}"    echo "  -h, --help           Show this help message"

    echo "  $0 logs --service=all --lines=100"    echo ""

    echo "  $0 tail --service=gateway --follow"    echo "Examples:"

    echo "  $0 errors --since=1h"    echo "  $0                   # Show recent logs from all services"

    echo "  $0 search --grep='ERROR' --service=knowledge-fusion"    echo "  $0 -f                # Follow all logs in real-time"

    echo "  $0 health"    echo "  $0 -s OpenWebUI -f   # Follow only OpenWebUI logs"

    echo "  $0 metrics --service=gateway"    echo "  $0 -e                # Show only errors"

}    echo "  $0 -g \"Knowledge\"    # Show logs containing 'Knowledge'"

    echo "  $0 -l 100            # Show last 100 lines from each service"

# Parse command line arguments}

parse_args() {

    COMMAND=""check_log_sizes() {

    SERVICE="all"    echo -e "${BLUE}📊 Log File Sizes${NC}"

    LEVEL=""    echo -e "${BLUE}=================${NC}"

    LINES=50    

    FOLLOW=false    for service in $ALL_SERVICES; do

    SINCE=""        log_file=$(get_log_file "$service")

    GREP_PATTERN=""        if [ -f "$log_file" ]; then

    JSON_OUTPUT=false            size=$(du -h "$log_file" | cut -f1)

                lines=$(wc -l < "$log_file" 2>/dev/null || echo "0")

    while [[ $# -gt 0 ]]; do            color=$(get_service_color "$service")

        case $1 in            echo -e "${color}$service:${NC} $size ($lines lines)"

            logs|tail|errors|search|status|health|metrics|processes|analyze|summary|performance|help)        else

                COMMAND="$1"            color=$(get_service_color "$service")

                shift            echo -e "${color}$service:${NC} No log file"

                ;;        fi

            --service=*)    done

                SERVICE="${1#*=}"    echo ""

                shift}

                ;;

            --level=*)clear_logs() {

                LEVEL="${1#*=}"    echo -e "${YELLOW}🧹 Clearing all log files...${NC}"

                shift    

                ;;    for service in $ALL_SERVICES; do

            --lines=*)        log_file=$(get_log_file "$service")

                LINES="${1#*=}"        if [ -f "$log_file" ]; then

                shift            > "$log_file"

                ;;            color=$(get_service_color "$service")

            --since=*)            echo -e "${color}✅ Cleared $service log${NC}"

                SINCE="${1#*=}"        fi

                shift    done

                ;;    echo -e "${GREEN}All logs cleared!${NC}"

            --grep=*)}

                GREP_PATTERN="${1#*=}"

                shiftformat_log_line() {

                ;;    local service=$1

            --follow)    local line=$2

                FOLLOW=true    local color=$(get_service_color "$service")

                shift    local timestamp=$(date "+%H:%M:%S")

                ;;    

            --json)    echo -e "${color}[$timestamp][$service]${NC} $line"

                JSON_OUTPUT=true}

                shift

                ;;show_service_logs() {

            *)    local service=$1

                echo -e "${RED}Unknown option: $1${NC}"    local lines=${2:-50}

                show_help    local filter_pattern=$3

                exit 1    local error_only=$4

                ;;    local warning_only=$5

        esac    

    done    local log_file=$(get_log_file "$service")

}    local color=$(get_service_color "$service")

    

# Get log files for service    if [ ! -f "$log_file" ]; then

get_log_files() {        echo -e "${color}📝 $service: No log file found${NC}"

    local service="$1"        return

    if [[ -n "${SERVICES[$service]:-}" ]]; then    fi

        echo "${SERVICES[$service]}"    

    else    echo -e "${color}📝 $service Logs (last $lines lines)${NC}"

        echo ""    echo -e "${color}$(printf '=%.0s' {1..50})${NC}"

    fi    

}    local tail_cmd="tail -n $lines '$log_file'"

    

# View logs    # Apply filters

view_logs() {    if [ "$error_only" = true ]; then

    local log_files        tail_cmd="$tail_cmd | grep -i -E '(error|exception|failed|fatal)'"

    log_files=$(get_log_files "$SERVICE")    elif [ "$warning_only" = true ]; then

            tail_cmd="$tail_cmd | grep -i -E '(warn|warning|error|exception|failed|fatal)'"

    if [ -z "$log_files" ]; then    fi

        echo -e "${RED}❌ Unknown service: $SERVICE${NC}"    

        echo -e "Available services: ${!SERVICES[*]}"    if [ -n "$filter_pattern" ]; then

        exit 1        tail_cmd="$tail_cmd | grep -i '$filter_pattern'"

    fi    fi

        

    echo -e "${BLUE}📄 Viewing logs for: $SERVICE${NC}"    # Execute command and format output

    echo -e "${BLUE}===========================================${NC}"    eval "$tail_cmd" 2>/dev/null | while IFS= read -r line; do

            format_log_line "$service" "$line"

    local cmd="tail -n $LINES"    done || echo -e "${color}📭 No matching log entries${NC}"

        

    if [ "$FOLLOW" = true ]; then    echo ""

        cmd="tail -f"}

    fi

    follow_logs() {

    if [ -n "$SINCE" ]; then    local specific_service=$1

        # Use journalctl-style since filtering (approximate with find/grep)    local filter_pattern=$2

        echo -e "${YELLOW}⚠️  Time filtering not fully implemented, showing recent entries${NC}"    local error_only=$3

    fi    local warning_only=$4

        

    # Apply log files expansion and filtering    echo -e "${BLUE}🔄 Following logs in real-time... (Press Ctrl+C to stop)${NC}"

    local files_expanded    echo -e "${BLUE}======================================================${NC}"

    files_expanded=$(eval echo "$log_files")    echo ""

        

    if [ -n "$GREP_PATTERN" ]; then    # Build tail command for following logs

        $cmd $files_expanded 2>/dev/null | grep --color=always "$GREP_PATTERN" || echo -e "${YELLOW}No matches found${NC}"    local tail_files=()

    elif [ -n "$LEVEL" ]; then    

        case "$LEVEL" in    if [ -n "$specific_service" ]; then

            error)        local log_file=$(get_log_file "$specific_service")

                $cmd $files_expanded 2>/dev/null | grep -i --color=always -E "(ERROR|CRITICAL|FATAL)" || echo -e "${YELLOW}No error logs found${NC}"        if [ -f "$log_file" ]; then

                ;;            tail_files+=("$log_file")

            warn)        fi

                $cmd $files_expanded 2>/dev/null | grep -i --color=always -E "(WARN|WARNING)" || echo -e "${YELLOW}No warning logs found${NC}"    else

                ;;        for service in $ALL_SERVICES; do

            info)            local log_file=$(get_log_file "$service")

                $cmd $files_expanded 2>/dev/null | grep -i --color=always "INFO" || echo -e "${YELLOW}No info logs found${NC}"            if [ -f "$log_file" ]; then

                ;;                tail_files+=("$log_file")

            debug)            fi

                $cmd $files_expanded 2>/dev/null | grep -i --color=always "DEBUG" || echo -e "${YELLOW}No debug logs found${NC}"        done

                ;;    fi

            *)    

                $cmd $files_expanded 2>/dev/null || echo -e "${YELLOW}No logs found${NC}"    if [ ${#tail_files[@]} -eq 0 ]; then

                ;;        echo -e "${RED}❌ No log files found to follow${NC}"

        esac        return 1

    else    fi

        $cmd $files_expanded 2>/dev/null || echo -e "${YELLOW}No logs found${NC}"    

    fi    # Use multitail if available, otherwise fall back to tail

}    if command -v multitail >/dev/null 2>&1; then

        echo -e "${GREEN}Using multitail for enhanced viewing${NC}"

# Show errors        multitail "${tail_files[@]}"

show_errors() {    else

    echo -e "${RED}🚨 Error Analysis${NC}"        # Use tail -f with multiple files

    echo -e "${RED}=================${NC}"        tail -f "${tail_files[@]}" | while IFS= read -r line; do

                # Try to identify which service the log line comes from

    local log_files            local identified_service=""

    log_files=$(get_log_files "$SERVICE")            for service in $ALL_SERVICES; do

                    local service_log_file=$(get_log_file "$service")

    if [ -z "$log_files" ]; then                if [[ "$line" == *"$service_log_file"* ]]; then

        log_files="${SERVICES[all]}"                    identified_service="$service"

    fi                    break

                    fi

    # Expand files            done

    local files_expanded            

    files_expanded=$(eval echo "$log_files")            # Apply filters

                if [ "$error_only" = true ] && ! echo "$line" | grep -qi -E '(error|exception|failed|fatal)'; then

    echo -e "${YELLOW}Recent Errors:${NC}"                continue

    grep -i --color=always -E "(ERROR|CRITICAL|FATAL)" $files_expanded 2>/dev/null | tail -20 || echo -e "${GREEN}✅ No recent errors found${NC}"            fi

                

    echo -e "\n${YELLOW}Recent Warnings:${NC}"            if [ "$warning_only" = true ] && ! echo "$line" | grep -qi -E '(warn|warning|error|exception|failed|fatal)'; then

    grep -i --color=always -E "(WARN|WARNING)" $files_expanded 2>/dev/null | tail -10 || echo -e "${GREEN}✅ No recent warnings found${NC}"                continue

}            fi

            

# Check service status            if [ -n "$filter_pattern" ] && ! echo "$line" | grep -qi "$filter_pattern"; then

check_status() {                continue

    echo -e "${BLUE}🔍 Service Status${NC}"            fi

    echo -e "${BLUE}=================${NC}"            

                # Format and display

    for service in "${!SERVICE_PORTS[@]}"; do            if [ -n "$identified_service" ]; then

        local port="${SERVICE_PORTS[$service]}"                format_log_line "$identified_service" "$line"

        local status="❌ DOWN"            else

        local color="$RED"                echo -e "${NC}$line${NC}"

                    fi

        if curl -s "http://localhost:$port" >/dev/null 2>&1 || curl -s "http://localhost:$port/health" >/dev/null 2>&1; then        done

            status="✅ UP"    fi

            color="$GREEN"}

        fi

        show_all_logs() {

        printf "%-20s Port %-6s %b%s%b\n" "$service" "$port" "$color" "$status" "$NC"    local lines=${1:-50}

    done    local filter_pattern=$2

        local error_only=$3

    echo ""    local warning_only=$4

        

    # Check processes    echo -e "${BLUE}📋 Global Log View - All Services${NC}"

    if [ -f "$PID_FILE" ]; then    echo -e "${BLUE}==================================${NC}"

        echo -e "${BLUE}📊 Process Status:${NC}"    echo ""

        while read -r service_name pid; do    

            if kill -0 "$pid" 2>/dev/null; then    # Show log sizes first

                echo -e "  ${GREEN}✅ $service_name (PID: $pid)${NC}"    check_log_sizes

            else    

                echo -e "  ${RED}❌ $service_name (PID: $pid - not running)${NC}"    # Show logs from each service

            fi    for service in $ALL_SERVICES; do

        done < "$PID_FILE"        local log_file=$(get_log_file "$service")

    else        if [ -f "$log_file" ]; then

        echo -e "${YELLOW}⚠️  No PID file found${NC}"            show_service_logs "$service" "$lines" "$filter_pattern" "$error_only" "$warning_only"

    fi        fi

}    done

}

# Health check

health_check() {# Parse command line arguments

    echo -e "${BLUE}🏥 Health Check${NC}"FOLLOW=false

    echo -e "${BLUE}===============${NC}"SPECIFIC_SERVICE=""

    FILTER_PATTERN=""

    local all_healthy=trueERROR_ONLY=false

    WARNING_ONLY=false

    for service in "${!SERVICE_PORTS[@]}"; doLINES=50

        local port="${SERVICE_PORTS[$service]}"CLEAR_LOGS=false

        echo -e "${BLUE}🔍 Checking $service...${NC}"SHOW_SIZES=false

        

        if curl -s "http://localhost:$port/health" >/dev/null 2>&1; thenwhile [[ $# -gt 0 ]]; do

            echo -e "  ${GREEN}✅ Healthy${NC}"    case $1 in

        elif curl -s "http://localhost:$port" >/dev/null 2>&1; then        -f|--follow)

            echo -e "  ${YELLOW}⚠️  Responding (no health endpoint)${NC}"            FOLLOW=true

        else            shift

            echo -e "  ${RED}❌ Unhealthy${NC}"            ;;

            all_healthy=false        -s|--service)

        fi            SPECIFIC_SERVICE="$2"

    done            shift 2

                ;;

    echo ""        -g|--grep)

    if [ "$all_healthy" = true ]; then            FILTER_PATTERN="$2"

        echo -e "${GREEN}🎉 All services are healthy!${NC}"            shift 2

    else            ;;

        echo -e "${RED}⚠️  Some services need attention${NC}"        -e|--errors)

    fi            ERROR_ONLY=true

}            shift

            ;;

# Show metrics        -w|--warnings)

show_metrics() {            WARNING_ONLY=true

    echo -e "${PURPLE}📊 Performance Metrics${NC}"            shift

    echo -e "${PURPLE}======================${NC}"            ;;

            -l|--lines)

    # System metrics            LINES="$2"

    echo -e "${CYAN}System Resources:${NC}"            shift 2

    echo -e "  CPU Usage: $(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')"            ;;

    echo -e "  Memory: $(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')"        -c|--clear)

                CLEAR_LOGS=true

    # Port usage            shift

    echo -e "\n${CYAN}Port Usage:${NC}"            ;;

    for service in "${!SERVICE_PORTS[@]}"; do        -z|--size)

        local port="${SERVICE_PORTS[$service]}"            SHOW_SIZES=true

        local connections=$(netstat -an | grep ":$port " | wc -l | xargs)            shift

        echo -e "  $service (port $port): $connections connections"            ;;

    done        -h|--help)

                show_help

    # Log file sizes            exit 0

    echo -e "\n${CYAN}Log File Sizes:${NC}"            ;;

    if [ -d "$LOGS_DIR" ]; then        *)

        du -h "$LOGS_DIR"/*.log 2>/dev/null | while read -r size file; do            echo -e "${RED}Unknown option: $1${NC}"

            local filename=$(basename "$file")            show_help

            echo -e "  $filename: $size"            exit 1

        done            ;;

    fi    esac

}done



# Analyze logs# Execute based on options

analyze_logs() {if [ "$CLEAR_LOGS" = true ]; then

    echo -e "${PURPLE}🔍 Log Analysis${NC}"    clear_logs

    echo -e "${PURPLE}===============${NC}"    exit 0

    fi

    local log_files

    log_files=$(get_log_files "$SERVICE")if [ "$SHOW_SIZES" = true ]; then

        check_log_sizes

    if [ -z "$log_files" ]; then    exit 0

        log_files="${SERVICES[all]}"fi

    fi

    # Validate specific service if provided

    # Expand filesif [ -n "$SPECIFIC_SERVICE" ]; then

    local files_expanded    valid_service=false

    files_expanded=$(eval echo "$log_files")    for service in $ALL_SERVICES; do

            if [ "$service" = "$SPECIFIC_SERVICE" ]; then

    echo -e "${CYAN}Error Summary (last 1000 lines):${NC}"            valid_service=true

    tail -1000 $files_expanded 2>/dev/null | grep -c -i "ERROR" | xargs echo "  Errors:" || echo "  Errors: 0"            break

    tail -1000 $files_expanded 2>/dev/null | grep -c -i "WARN" | xargs echo "  Warnings:" || echo "  Warnings: 0"        fi

        done

    echo -e "\n${CYAN}Top Error Messages:${NC}"    

    tail -1000 $files_expanded 2>/dev/null | grep -i "ERROR" | sort | uniq -c | sort -nr | head -5 | while read -r count message; do    if [ "$valid_service" = false ]; then

        echo -e "  $count: $message"        echo -e "${RED}❌ Invalid service name: $SPECIFIC_SERVICE${NC}"

    done        echo -e "${YELLOW}Available services: $ALL_SERVICES${NC}"

            exit 1

    echo -e "\n${CYAN}Request Volume (if available):${NC}"    fi

    tail -1000 $files_expanded 2>/dev/null | grep -c "HTTP" | xargs echo "  HTTP Requests:" || echo "  HTTP Requests: Not available"fi

}

# Main execution

# Show running processesif [ "$FOLLOW" = true ]; then

show_processes() {    follow_logs "$SPECIFIC_SERVICE" "$FILTER_PATTERN" "$ERROR_ONLY" "$WARNING_ONLY"

    echo -e "${BLUE}🏃 Running Processes${NC}"elif [ -n "$SPECIFIC_SERVICE" ]; then

    echo -e "${BLUE}===================${NC}"    show_service_logs "$SPECIFIC_SERVICE" "$LINES" "$FILTER_PATTERN" "$ERROR_ONLY" "$WARNING_ONLY"

    else

    echo -e "${CYAN}Knowledge Fusion Processes:${NC}"    show_all_logs "$LINES" "$FILTER_PATTERN" "$ERROR_ONLY" "$WARNING_ONLY"

    ps aux | grep -E "(knowledge|fusion|gateway|core)" | grep -v grep | while read -r line; dofi

        echo -e "  $line"
    done
    
    echo -e "\n${CYAN}Python Processes:${NC}"
    ps aux | grep python | grep -v grep | head -10 | while read -r line; do
        echo -e "  $line"
    done
}

# Generate summary
generate_summary() {
    echo -e "${BLUE}📋 System Summary${NC}"
    echo -e "${BLUE}=================${NC}"
    
    local current_time=$(date)
    echo -e "Generated: $current_time"
    echo ""
    
    # Quick status
    check_status
    echo ""
    
    # Recent activity
    echo -e "${CYAN}Recent Activity (last 50 lines):${NC}"
    local log_files="${SERVICES[all]}"
    local files_expanded
    files_expanded=$(eval echo "$log_files")
    tail -50 $files_expanded 2>/dev/null | tail -10
    
    echo ""
    
    # Error summary
    show_errors
}

# Main execution
main() {
    # Create logs directory if it doesn't exist
    mkdir -p "$LOGS_DIR"
    
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    parse_args "$@"
    
    case "$COMMAND" in
        logs)
            view_logs
            ;;
        tail)
            FOLLOW=true
            view_logs
            ;;
        errors)
            show_errors
            ;;
        search)
            if [ -z "$GREP_PATTERN" ]; then
                echo -e "${RED}❌ Search pattern is required${NC}"
                echo -e "Use: --grep=PATTERN"
                exit 1
            fi
            view_logs
            ;;
        status)
            check_status
            ;;
        health)
            health_check
            ;;
        metrics)
            show_metrics
            ;;
        processes)
            show_processes
            ;;
        analyze)
            analyze_logs
            ;;
        summary)
            generate_summary
            ;;
        performance)
            show_metrics
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