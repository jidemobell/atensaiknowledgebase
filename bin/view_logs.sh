#!/bin/bash

# Simple log viewer for Knowledge Fusion Platform

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS_DIR="$PROJECT_ROOT/logs"

show_help() {
    echo "🔍 Topology Knowledge - Log Viewer"
    echo "=================================="
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help"
    echo "  -z, --size           Show log file sizes"
    echo "  -c, --clear          Clear all log files"
    echo "  -f, --follow         Follow logs in real-time"
    echo "  -s, --service NAME   Show specific service (core, fusion, gateway)"
    echo ""
    echo "Examples:"
    echo "  $0                   # Show recent logs"
    echo "  $0 -z                # Show log sizes"
    echo "  $0 -s fusion         # Show fusion logs"
}

check_log_sizes() {
    echo "📊 Log File Sizes"
    echo "================="
    
    mkdir -p "$LOGS_DIR"
    
    for log in "$LOGS_DIR"/*.log; do
        if [ -f "$log" ]; then
            size=$(du -h "$log" | cut -f1)
            lines=$(wc -l < "$log" 2>/dev/null || echo "0")
            basename_log=$(basename "$log")
            echo "$basename_log: $size ($lines lines)"
        fi
    done
    
    if [ ! -f "$LOGS_DIR"/*.log ] 2>/dev/null; then
        echo "No log files found in $LOGS_DIR"
    fi
}

clear_logs() {
    echo "🧹 Clearing all log files..."
    mkdir -p "$LOGS_DIR"
    
    for log in "$LOGS_DIR"/*.log; do
        if [ -f "$log" ]; then
            > "$log"
            echo "✅ Cleared $(basename "$log")"
        fi
    done
    echo "All logs cleared!"
}

show_logs() {
    local service=${1:-"all"}
    local follow=${2:-false}
    
    mkdir -p "$LOGS_DIR"
    
    if [ "$service" = "all" ]; then
        echo "📋 Recent logs from all services:"
        echo "================================="
        for log in "$LOGS_DIR"/*.log; do
            if [ -f "$log" ]; then
                echo ""
                echo "=== $(basename "$log") ==="
                tail -n 20 "$log" 2>/dev/null || echo "Empty or unreadable"
            fi
        done
    else
        case "$service" in
            "core") log_file="$LOGS_DIR/core_backend.log" ;;
            "fusion") log_file="$LOGS_DIR/knowledge_fusion.log" ;;
            "gateway") log_file="$LOGS_DIR/gateway.log" ;;
            *) log_file="$LOGS_DIR/${service}.log" ;;
        esac
        
        if [ -f "$log_file" ]; then
            echo "=== $(basename "$log_file") ==="
            if [ "$follow" = true ]; then
                echo "Following logs... (Press Ctrl+C to stop)"
                tail -f "$log_file"
            else
                tail -n 50 "$log_file"
            fi
        else
            echo "❌ Log file not found: $log_file"
        fi
    fi
}

# Parse arguments
FOLLOW=false
SERVICE="all"
SHOW_SIZES=false
CLEAR_LOGS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -z|--size)
            SHOW_SIZES=true
            shift
            ;;
        -c|--clear)
            CLEAR_LOGS=true
            shift
            ;;
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -s|--service)
            SERVICE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Execute
if [ "$CLEAR_LOGS" = true ]; then
    clear_logs
    exit 0
fi

if [ "$SHOW_SIZES" = true ]; then
    check_log_sizes
    exit 0
fi

show_logs "$SERVICE" "$FOLLOW"
