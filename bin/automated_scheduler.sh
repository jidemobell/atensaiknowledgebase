#!/bin/bash

# Automated Knowledge Source Update Scheduler
# Manages scheduled updates for GitHub repositories and hybrid sources

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
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEDULER_CONFIG="$PROJECT_ROOT/scheduler_config.json"
LOGS_DIR="$PROJECT_ROOT/logs"
SCRIPTS_DIR="$PROJECT_ROOT"

# Ensure dependencies
ADD_KNOWLEDGE_SCRIPT="$SCRIPTS_DIR/add_knowledge_source.sh"
HYBRID_SOURCES_SCRIPT="$SCRIPTS_DIR/manage_hybrid_sources.sh"

show_help() {
    echo -e "${BLUE}Automated Knowledge Source Update Scheduler${NC}"
    echo -e "${BLUE}=============================================${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo -e "${CYAN}Scheduling Commands:${NC}"
    echo "  setup          Set up automated scheduling"
    echo "  add-schedule   Add a new scheduled update"
    echo "  list           List all scheduled tasks"
    echo "  run-now        Run specific scheduled task immediately"
    echo "  status         Show scheduler status"
    echo ""
    echo -e "${CYAN}Management Commands:${NC}"
    echo "  enable         Enable automated scheduling"
    echo "  disable        Disable automated scheduling"
    echo "  logs           Show scheduler logs"
    echo "  cleanup        Clean up old logs and temporary files"
    echo ""
    echo -e "${CYAN}Options:${NC}"
    echo "  --schedule=CRON    Cron schedule (e.g., '0 */6 * * *' for every 6 hours)"
    echo "  --type=TYPE        Update type (github, web, api, documents, all)"
    echo "  --source=NAME      Specific source name to schedule"
    echo "  --days=N           Update every N days (alternative to cron)"
    echo "  --enabled          Enable the schedule immediately"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0 setup"
    echo "  $0 add-schedule --type=github --days=3 --enabled"
    echo "  $0 add-schedule --type=web --schedule='0 2 * * *' --enabled"
    echo "  $0 run-now github-updates"
    echo "  $0 status"
}

# Initialize scheduler configuration
init_scheduler() {
    if [ ! -f "$SCHEDULER_CONFIG" ]; then
        cat > "$SCHEDULER_CONFIG" << 'EOF'
{
  "version": "1.0",
  "enabled": false,
  "schedules": {},
  "settings": {
    "max_concurrent_updates": 3,
    "retry_attempts": 3,
    "retry_delay": 300,
    "log_retention_days": 30,
    "notification_enabled": false,
    "conflict_resolution": "latest_wins"
  },
  "last_run": {},
  "statistics": {
    "total_runs": 0,
    "successful_runs": 0,
    "failed_runs": 0
  }
}
EOF
        echo -e "${GREEN}✅ Initialized scheduler configuration${NC}"
    fi
    
    mkdir -p "$LOGS_DIR/scheduler"
    
    # Ensure required scripts exist
    if [ ! -f "$ADD_KNOWLEDGE_SCRIPT" ]; then
        echo -e "${RED}❌ Required script not found: $ADD_KNOWLEDGE_SCRIPT${NC}"
        exit 1
    fi
    
    if [ ! -f "$HYBRID_SOURCES_SCRIPT" ]; then
        echo -e "${RED}❌ Required script not found: $HYBRID_SOURCES_SCRIPT${NC}"
        exit 1
    fi
}

# Set up automated scheduling
setup_scheduler() {
    echo -e "${BLUE}🔧 Setting up Automated Knowledge Source Scheduler${NC}"
    echo -e "${BLUE}==================================================${NC}"
    
    init_scheduler
    
    # Check if cron is available
    if ! command -v crontab >/dev/null 2>&1; then
        echo -e "${RED}❌ crontab is not available. Scheduling features will be limited.${NC}"
        return 1
    fi
    
    # Create default schedules
    echo -e "${CYAN}Creating default update schedules...${NC}"
    
    # GitHub repositories - every 3 days at 2 AM
    add_schedule "github-updates" "github" "0 2 */3 * *" true
    
    # Web content - daily at 3 AM
    add_schedule "web-content-updates" "web" "0 3 * * *" true
    
    # API data - every 6 hours
    add_schedule "api-data-updates" "api" "0 */6 * * *" true
    
    # Documents - weekly on Sunday at 4 AM
    add_schedule "document-updates" "documents" "0 4 * * 0" true
    
    echo -e "${GREEN}✅ Default schedules created${NC}"
    
    # Enable scheduler
    enable_scheduler
    
    echo -e "${GREEN}🎉 Scheduler setup completed!${NC}"
    echo -e "Use '$0 status' to view current schedules"
    echo -e "Use '$0 logs' to monitor execution"
}

# Add a new schedule
add_schedule() {
    local name="$1"
    local type="$2"
    local schedule="$3"
    local enabled="${4:-false}"
    
    init_scheduler
    
    echo -e "${BLUE}📅 Adding schedule: $name${NC}"
    
    # Create schedule configuration
    local schedule_config=$(cat << EOF
{
  "type": "$type",
  "schedule": "$schedule",
  "enabled": $enabled,
  "created": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "last_run": null,
  "next_run": null,
  "run_count": 0,
  "success_count": 0,
  "failure_count": 0,
  "average_duration": 0,
  "description": "Automated update for $type sources"
}
EOF
    )
    
    # Update configuration
    local temp_file=$(mktemp)
    jq --arg name "$name" --argjson config "$schedule_config" '.schedules[$name] = $config' "$SCHEDULER_CONFIG" > "$temp_file"
    mv "$temp_file" "$SCHEDULER_CONFIG"
    
    # Add to crontab if enabled
    if [ "$enabled" = true ]; then
        add_to_crontab "$name" "$schedule"
    fi
    
    echo -e "${GREEN}✅ Schedule '$name' added successfully${NC}"
    echo -e "   Type: $type"
    echo -e "   Schedule: $schedule"
    echo -e "   Enabled: $enabled"
}

# Add schedule to crontab
add_to_crontab() {
    local name="$1"
    local schedule="$2"
    
    local script_path="$0"
    local cron_command="$schedule $script_path run-scheduled $name >> $LOGS_DIR/scheduler/cron.log 2>&1"
    
    # Get current crontab
    local current_crontab
    current_crontab=$(crontab -l 2>/dev/null || echo "")
    
    # Check if this schedule already exists
    if echo "$current_crontab" | grep -q "run-scheduled $name"; then
        echo -e "${YELLOW}⚠️  Crontab entry for '$name' already exists${NC}"
        return
    fi
    
    # Add new crontab entry
    (echo "$current_crontab"; echo "$cron_command") | crontab -
    echo -e "${GREEN}✅ Added crontab entry for '$name'${NC}"
}

# Remove schedule from crontab
remove_from_crontab() {
    local name="$1"
    
    local current_crontab
    current_crontab=$(crontab -l 2>/dev/null || echo "")
    
    # Remove the specific crontab entry
    echo "$current_crontab" | grep -v "run-scheduled $name" | crontab -
    echo -e "${GREEN}✅ Removed crontab entry for '$name'${NC}"
}

# List all scheduled tasks
list_schedules() {
    init_scheduler
    
    echo -e "${BLUE}📋 Scheduled Knowledge Source Updates${NC}"
    echo -e "${BLUE}=====================================${NC}"
    
    local schedule_count=$(jq '.schedules | length' "$SCHEDULER_CONFIG")
    local enabled_status=$(jq -r '.enabled' "$SCHEDULER_CONFIG")
    
    echo -e "Scheduler Status: $([ "$enabled_status" = "true" ] && echo "${GREEN}Enabled${NC}" || echo "${RED}Disabled${NC}")"
    echo -e "Total Schedules: $schedule_count"
    echo ""
    
    if [ "$schedule_count" -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No schedules configured${NC}"
        echo -e "Use '$0 add-schedule' to add new schedules"
        return
    fi
    
    # List schedules
    echo -e "${CYAN}Schedule Details:${NC}"
    jq -r '.schedules | to_entries[] | "\(.key):\n  Type: \(.value.type)\n  Schedule: \(.value.schedule)\n  Enabled: \(.value.enabled)\n  Last Run: \(.value.last_run // "Never")\n  Success Rate: \(if .value.run_count > 0 then (.value.success_count * 100 / .value.run_count | floor) else 0 end)%\n"' "$SCHEDULER_CONFIG"
    
    # Show next runs if cron is available
    if command -v crontab >/dev/null 2>&1; then
        echo -e "${CYAN}Active Crontab Entries:${NC}"
        crontab -l 2>/dev/null | grep "run-scheduled" | while read -r line; do
            local schedule_name=$(echo "$line" | grep -o "run-scheduled [^ ]*" | cut -d' ' -f2)
            echo -e "  $schedule_name: $(echo "$line" | cut -d' ' -f1-5)"
        done || echo -e "  ${YELLOW}No active crontab entries found${NC}"
    fi
}

# Run specific scheduled task immediately
run_now() {
    local schedule_name="$1"
    
    init_scheduler
    
    echo -e "${BLUE}🚀 Running scheduled task: $schedule_name${NC}"
    echo -e "${BLUE}======================================${NC}"
    
    # Get schedule configuration
    local schedule_exists=$(jq -r --arg name "$schedule_name" '.schedules | has($name)' "$SCHEDULER_CONFIG")
    
    if [ "$schedule_exists" != "true" ]; then
        echo -e "${RED}❌ Schedule '$schedule_name' not found${NC}"
        exit 1
    fi
    
    local schedule_type=$(jq -r --arg name "$schedule_name" '.schedules[$name].type' "$SCHEDULER_CONFIG")
    
    echo -e "${CYAN}Schedule Type: $schedule_type${NC}"
    echo -e "${CYAN}Started: $(date)${NC}"
    
    # Execute the update based on type
    local start_time=$(date +%s)
    local success=false
    
    case "$schedule_type" in
        "github")
            run_github_updates && success=true
            ;;
        "web")
            run_web_updates && success=true
            ;;
        "api")
            run_api_updates && success=true
            ;;
        "documents")
            run_document_updates && success=true
            ;;
        "all")
            run_all_updates && success=true
            ;;
        *)
            echo -e "${RED}❌ Unknown schedule type: $schedule_type${NC}"
            ;;
    esac
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Update statistics
    update_schedule_stats "$schedule_name" "$success" "$duration"
    
    if [ "$success" = true ]; then
        echo -e "${GREEN}✅ Scheduled task '$schedule_name' completed successfully${NC}"
        echo -e "   Duration: ${duration}s"
    else
        echo -e "${RED}❌ Scheduled task '$schedule_name' failed${NC}"
        echo -e "   Duration: ${duration}s"
    fi
}

# Run scheduled task (called by cron)
run_scheduled() {
    local schedule_name="$1"
    
    # Log to scheduler log
    local log_file="$LOGS_DIR/scheduler/${schedule_name}_$(date +%Y%m%d).log"
    mkdir -p "$(dirname "$log_file")"
    
    {
        echo "=== Scheduled run: $(date) ==="
        run_now "$schedule_name"
        echo "=== Completed: $(date) ==="
        echo ""
    } >> "$log_file" 2>&1
}

# Update specific types
run_github_updates() {
    echo -e "${CYAN}📦 Updating GitHub repositories...${NC}"
    if [ -f "$ADD_KNOWLEDGE_SCRIPT" ]; then
        "$ADD_KNOWLEDGE_SCRIPT" update-all
    else
        echo -e "${RED}❌ GitHub update script not found${NC}"
        return 1
    fi
}

run_web_updates() {
    echo -e "${CYAN}🌐 Updating web content sources...${NC}"
    if [ -f "$HYBRID_SOURCES_SCRIPT" ]; then
        "$HYBRID_SOURCES_SCRIPT" sync-web
    else
        echo -e "${RED}❌ Hybrid sources script not found${NC}"
        return 1
    fi
}

run_api_updates() {
    echo -e "${CYAN}🔌 Updating API data sources...${NC}"
    if [ -f "$HYBRID_SOURCES_SCRIPT" ]; then
        "$HYBRID_SOURCES_SCRIPT" sync-apis
    else
        echo -e "${RED}❌ Hybrid sources script not found${NC}"
        return 1
    fi
}

run_document_updates() {
    echo -e "${CYAN}📄 Updating document collections...${NC}"
    if [ -f "$HYBRID_SOURCES_SCRIPT" ]; then
        # In a real implementation, this would sync document sources
        echo -e "${YELLOW}⚠️  Document sync not yet implemented${NC}"
        return 0
    else
        echo -e "${RED}❌ Hybrid sources script not found${NC}"
        return 1
    fi
}

run_all_updates() {
    echo -e "${CYAN}🔄 Running all scheduled updates...${NC}"
    local all_success=true
    
    run_github_updates || all_success=false
    run_web_updates || all_success=false
    run_api_updates || all_success=false
    run_document_updates || all_success=false
    
    return $([ "$all_success" = true ] && echo 0 || echo 1)
}

# Update schedule statistics
update_schedule_stats() {
    local schedule_name="$1"
    local success="$2"
    local duration="$3"
    
    local temp_file=$(mktemp)
    
    jq --arg name "$schedule_name" --arg success "$success" --arg duration "$duration" --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" '
    .schedules[$name].last_run = $timestamp |
    .schedules[$name].run_count += 1 |
    if $success == "true" then
        .schedules[$name].success_count += 1
    else
        .schedules[$name].failure_count += 1
    end |
    .schedules[$name].average_duration = ((.schedules[$name].average_duration * (.schedules[$name].run_count - 1) + ($duration | tonumber)) / .schedules[$name].run_count) |
    .statistics.total_runs += 1 |
    if $success == "true" then
        .statistics.successful_runs += 1
    else
        .statistics.failed_runs += 1
    end
    ' "$SCHEDULER_CONFIG" > "$temp_file"
    
    mv "$temp_file" "$SCHEDULER_CONFIG"
}

# Show scheduler status
show_status() {
    init_scheduler
    
    echo -e "${BLUE}📊 Scheduler Status Report${NC}"
    echo -e "${BLUE}==========================${NC}"
    
    local enabled=$(jq -r '.enabled' "$SCHEDULER_CONFIG")
    local total_schedules=$(jq '.schedules | length' "$SCHEDULER_CONFIG")
    local active_schedules=$(jq '.schedules | to_entries[] | select(.value.enabled == true) | length' "$SCHEDULER_CONFIG")
    
    echo -e "Scheduler Status: $([ "$enabled" = "true" ] && echo "${GREEN}Enabled${NC}" || echo "${RED}Disabled${NC}")"
    echo -e "Total Schedules: $total_schedules"
    echo -e "Active Schedules: $active_schedules"
    echo ""
    
    # Statistics
    echo -e "${CYAN}Execution Statistics:${NC}"
    local total_runs=$(jq -r '.statistics.total_runs' "$SCHEDULER_CONFIG")
    local successful_runs=$(jq -r '.statistics.successful_runs' "$SCHEDULER_CONFIG")
    local failed_runs=$(jq -r '.statistics.failed_runs' "$SCHEDULER_CONFIG")
    local success_rate=0
    
    if [ "$total_runs" -gt 0 ]; then
        success_rate=$((successful_runs * 100 / total_runs))
    fi
    
    echo -e "  Total Runs: $total_runs"
    echo -e "  Successful: $successful_runs"
    echo -e "  Failed: $failed_runs"
    echo -e "  Success Rate: $success_rate%"
    echo ""
    
    # Recent activity
    echo -e "${CYAN}Recent Activity:${NC}"
    if [ -d "$LOGS_DIR/scheduler" ]; then
        find "$LOGS_DIR/scheduler" -name "*.log" -type f -mtime -1 | head -5 | while read -r log_file; do
            local filename=$(basename "$log_file")
            local size=$(du -h "$log_file" | cut -f1)
            local modified=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$log_file" 2>/dev/null || stat -c "%y" "$log_file" | cut -d' ' -f1-2)
            echo -e "  $filename ($size) - Modified: $modified"
        done
    else
        echo -e "  ${YELLOW}No recent activity${NC}"
    fi
}

# Enable scheduler
enable_scheduler() {
    init_scheduler
    
    echo -e "${BLUE}🔧 Enabling Knowledge Source Scheduler${NC}"
    
    # Update configuration
    local temp_file=$(mktemp)
    jq '.enabled = true' "$SCHEDULER_CONFIG" > "$temp_file"
    mv "$temp_file" "$SCHEDULER_CONFIG"
    
    # Add enabled schedules to crontab
    local enabled_schedules
    enabled_schedules=$(jq -r '.schedules | to_entries[] | select(.value.enabled == true) | .key' "$SCHEDULER_CONFIG")
    
    while IFS= read -r schedule_name; do
        if [ -n "$schedule_name" ]; then
            local schedule=$(jq -r --arg name "$schedule_name" '.schedules[$name].schedule' "$SCHEDULER_CONFIG")
            add_to_crontab "$schedule_name" "$schedule"
        fi
    done <<< "$enabled_schedules"
    
    echo -e "${GREEN}✅ Scheduler enabled${NC}"
}

# Disable scheduler
disable_scheduler() {
    init_scheduler
    
    echo -e "${BLUE}🔧 Disabling Knowledge Source Scheduler${NC}"
    
    # Update configuration
    local temp_file=$(mktemp)
    jq '.enabled = false' "$SCHEDULER_CONFIG" > "$temp_file"
    mv "$temp_file" "$SCHEDULER_CONFIG"
    
    # Remove all scheduler entries from crontab
    local current_crontab
    current_crontab=$(crontab -l 2>/dev/null || echo "")
    echo "$current_crontab" | grep -v "run-scheduled" | crontab -
    
    echo -e "${GREEN}✅ Scheduler disabled${NC}"
}

# Show scheduler logs
show_logs() {
    local lines="${1:-50}"
    
    echo -e "${BLUE}📄 Scheduler Logs${NC}"
    echo -e "${BLUE}=================${NC}"
    
    if [ -d "$LOGS_DIR/scheduler" ]; then
        echo -e "${CYAN}Recent Log Files:${NC}"
        find "$LOGS_DIR/scheduler" -name "*.log" -type f | sort -r | head -5 | while read -r log_file; do
            local filename=$(basename "$log_file")
            echo -e "\n${YELLOW}=== $filename ===${NC}"
            tail -n "$lines" "$log_file" 2>/dev/null || echo -e "${RED}Unable to read log file${NC}"
        done
    else
        echo -e "${YELLOW}⚠️  No scheduler logs found${NC}"
    fi
}

# Clean up old files
cleanup() {
    echo -e "${BLUE}🧹 Cleaning up Scheduler Files${NC}"
    echo -e "${BLUE}===============================${NC}"
    
    local retention_days=30
    local files_cleaned=0
    
    # Clean old log files
    if [ -d "$LOGS_DIR/scheduler" ]; then
        find "$LOGS_DIR/scheduler" -name "*.log" -type f -mtime +$retention_days -delete 2>/dev/null || true
        files_cleaned=$((files_cleaned + $(find "$LOGS_DIR/scheduler" -name "*.log" -type f -mtime +$retention_days | wc -l)))
    fi
    
    # Clean temporary files
    find /tmp -name "scheduler_*" -type f -mtime +1 -delete 2>/dev/null || true
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
    echo -e "   Removed $files_cleaned old log files"
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
        setup)
            setup_scheduler
            ;;
        add-schedule)
            # Parse options
            local schedule_name=""
            local schedule_type=""
            local cron_schedule=""
            local days=""
            local enabled=false
            
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --name=*)
                        schedule_name="${1#*=}"
                        shift
                        ;;
                    --type=*)
                        schedule_type="${1#*=}"
                        shift
                        ;;
                    --schedule=*)
                        cron_schedule="${1#*=}"
                        shift
                        ;;
                    --days=*)
                        days="${1#*=}"
                        shift
                        ;;
                    --enabled)
                        enabled=true
                        shift
                        ;;
                    *)
                        echo -e "${RED}Unknown option: $1${NC}"
                        exit 1
                        ;;
                esac
            done
            
            # Validate required parameters
            if [ -z "$schedule_type" ]; then
                echo -e "${RED}❌ --type is required${NC}"
                exit 1
            fi
            
            # Generate schedule name if not provided
            if [ -z "$schedule_name" ]; then
                schedule_name="${schedule_type}-updates"
            fi
            
            # Convert days to cron if provided
            if [ -n "$days" ] && [ -z "$cron_schedule" ]; then
                cron_schedule="0 2 */$days * *"  # Every N days at 2 AM
            fi
            
            # Default cron if none provided
            if [ -z "$cron_schedule" ]; then
                cron_schedule="0 2 */3 * *"  # Every 3 days at 2 AM
            fi
            
            add_schedule "$schedule_name" "$schedule_type" "$cron_schedule" "$enabled"
            ;;
        list)
            list_schedules
            ;;
        run-now)
            if [ $# -eq 0 ]; then
                echo -e "${RED}❌ Schedule name is required${NC}"
                exit 1
            fi
            run_now "$1"
            ;;
        run-scheduled)
            # Called by cron
            if [ $# -eq 0 ]; then
                echo -e "${RED}❌ Schedule name is required${NC}"
                exit 1
            fi
            run_scheduled "$1"
            ;;
        status)
            show_status
            ;;
        enable)
            enable_scheduler
            ;;
        disable)
            disable_scheduler
            ;;
        logs)
            show_logs "${1:-50}"
            ;;
        cleanup)
            cleanup
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