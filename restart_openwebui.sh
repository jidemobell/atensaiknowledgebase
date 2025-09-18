#!/bin/bash

# Quick OpenWebUI Restart Script
# Restarts only OpenWebUI without affecting other services

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENWEBUI_PATH="$PROJECT_ROOT/open-webui-cloned"
VENV_PATH="$PROJECT_ROOT/openwebui_venv"
PID_FILE="$PROJECT_ROOT/.topology_pids"

echo -e "${BLUE}🔄 OpenWebUI Quick Restart${NC}"
echo "=========================="

# Function to find OpenWebUI process
find_openwebui_process() {
    ps aux | grep -E "uvicorn.*open_webui.*3000" | grep -v grep | awk '{print $2}'
}

# Kill existing OpenWebUI process
echo "🛑 Stopping OpenWebUI..."
OPENWEBUI_PID=$(find_openwebui_process)

if [ -n "$OPENWEBUI_PID" ]; then
    echo "  Found OpenWebUI process: $OPENWEBUI_PID"
    kill $OPENWEBUI_PID
    
    # Wait for process to shut down
    for i in {1..10}; do
        if ! kill -0 $OPENWEBUI_PID 2>/dev/null; then
            echo -e "  ${GREEN}✅ OpenWebUI stopped${NC}"
            break
        fi
        echo "  Waiting for shutdown..."
        sleep 1
    done
    
    # Force kill if still running
    if kill -0 $OPENWEBUI_PID 2>/dev/null; then
        echo "  Force killing..."
        kill -9 $OPENWEBUI_PID
    fi
else
    echo "  No OpenWebUI process found"
fi

# Update PID file (remove old OpenWebUI entry)
if [ -f "$PID_FILE" ]; then
    grep -v "OpenWebUI" "$PID_FILE" > "${PID_FILE}.tmp" || true
    mv "${PID_FILE}.tmp" "$PID_FILE"
fi

echo ""
echo "🚀 Starting OpenWebUI..."

# Check if directory exists
if [ ! -d "$OPENWEBUI_PATH" ]; then
    echo -e "${RED}❌ OpenWebUI directory not found: $OPENWEBUI_PATH${NC}"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Start OpenWebUI
cd "$OPENWEBUI_PATH"
echo "  Starting on http://localhost:3000..."

# Start in background
nohup python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 3000 --app-dir backend > "$PROJECT_ROOT/logs/openwebui.log" 2>&1 &
NEW_PID=$!

# Add to PID file
echo "OpenWebUI $NEW_PID" >> "$PID_FILE"

echo "  Started with PID: $NEW_PID"

# Wait for it to be ready
echo "  Waiting for OpenWebUI to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅ OpenWebUI is ready!${NC}"
        echo ""
        echo -e "${GREEN}🎉 OpenWebUI restarted successfully${NC}"
        echo "📱 Access at: http://localhost:3000"
        echo ""
        echo "💡 If CSS issues persist, try:"
        echo "   • Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)"
        echo "   • Clear browser cache"
        echo "   • Try incognito/private browsing"
        exit 0
    fi
    echo -n "."
    sleep 2
done

echo -e "\n${YELLOW}⚠️  OpenWebUI started but may still be initializing${NC}"
echo "📱 Check: http://localhost:3000"
echo "📋 Logs: tail -f logs/openwebui.log"