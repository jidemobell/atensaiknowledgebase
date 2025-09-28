#!/bin/bash
# Stop All Knowledge Fusion Services
# Properly stops all services by port and process name

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 Stopping All Knowledge Fusion Services${NC}"
echo "============================================="

# Function to kill processes by port
kill_port() {
    local port=$1
    local service_name=$2
    
    echo -n "🔍 $service_name (port $port): "
    
    # Find process using the port
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        echo "Found PID(s): $pids"
        for pid in $pids; do
            echo "  🛑 Stopping PID $pid"
            kill -TERM $pid 2>/dev/null || true
        done
        
        # Wait a moment for graceful shutdown
        sleep 2
        
        # Force kill if still running
        local remaining_pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$remaining_pids" ]; then
            echo "  💀 Force killing remaining processes: $remaining_pids"
            for pid in $remaining_pids; do
                kill -KILL $pid 2>/dev/null || true
            done
        fi
        echo "  ✅ Stopped"
    else
        echo "✅ Not running"
    fi
}

# Function to kill processes by name pattern
kill_by_pattern() {
    local pattern=$1
    local service_name=$2
    
    echo -n "🔍 $service_name (by pattern): "
    
    local pids=$(pgrep -f "$pattern" 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        echo "Found PID(s): $pids"
        for pid in $pids; do
            echo "  🛑 Stopping PID $pid"
            kill -TERM $pid 2>/dev/null || true
        done
        
        sleep 2
        
        # Force kill if needed
        local remaining_pids=$(pgrep -f "$pattern" 2>/dev/null || true)
        if [ -n "$remaining_pids" ]; then
            echo "  💀 Force killing: $remaining_pids"
            for pid in $remaining_pids; do
                kill -KILL $pid 2>/dev/null || true
            done
        fi
        echo "  ✅ Stopped"
    else
        echo "✅ Not running"
    fi
}

echo -e "\n${YELLOW}🛑 Stopping Services by Port:${NC}"
kill_port 8001 "Core Backend"
kill_port 8002 "Knowledge Fusion Backend"
kill_port 9000 "Knowledge Fusion Gateway"

echo -e "\n${YELLOW}🛑 Stopping Services by Process Pattern:${NC}"
kill_by_pattern "uvicorn.*main:app" "Uvicorn processes"
kill_by_pattern "knowledge_fusion_gateway" "Gateway processes"
kill_by_pattern "python.*main.py" "Python main processes"

echo -e "\n${YELLOW}🧹 Additional Cleanup:${NC}"
# Remove PID file if it exists
PID_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.topology_pids"
if [ -f "$PID_FILE" ]; then
    rm -f "$PID_FILE"
    echo "  ✅ Removed PID file"
else
    echo "  ✅ No PID file to remove"
fi

# Final verification
echo -e "\n${GREEN}🎯 Final Status Check:${NC}"
echo -n "Port 8001: "
lsof -ti:8001 >/dev/null 2>&1 && echo -e "${RED}❌ Still occupied${NC}" || echo -e "${GREEN}✅ Free${NC}"

echo -n "Port 8002: "
lsof -ti:8002 >/dev/null 2>&1 && echo -e "${RED}❌ Still occupied${NC}" || echo -e "${GREEN}✅ Free${NC}"

echo -n "Port 9000: "
lsof -ti:9000 >/dev/null 2>&1 && echo -e "${RED}❌ Still occupied${NC}" || echo -e "${GREEN}✅ Free${NC}"

echo -n "Uvicorn processes: "
pgrep -f "uvicorn" >/dev/null 2>&1 && echo -e "${RED}❌ Still running${NC}" || echo -e "${GREEN}✅ None found${NC}"

echo -e "\n${GREEN}✅ All Knowledge Fusion services stopped!${NC}"
echo ""
echo "🚀 To restart everything: ./bin/restart_platform.sh"
echo "🔄 To start normally: ./bin/start_server_mode.sh"