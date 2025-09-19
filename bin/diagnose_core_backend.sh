#!/bin/bash

# =============================================================================
# CORE BACKEND API DIAGNOSTIC SCRIPT
# =============================================================================
# Use this script on your second computer to diagnose the OpenAPI issue
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CORE_BACKEND_URL="http://localhost:8001"
TIMEOUT=10

echo -e "${BLUE}🔍 Core Backend API Diagnostic${NC}"
echo -e "${BLUE}==============================${NC}"
echo ""

# Function to test endpoint
test_endpoint() {
    local endpoint="$1"
    local description="$2"
    local expected_status="${3:-200}"
    
    echo -n "Testing $description... "
    
    # Test with curl
    response=$(curl -s -w "\n%{http_code}\n%{time_total}\n%{size_download}" \
                   --connect-timeout $TIMEOUT \
                   --max-time $TIMEOUT \
                   "$CORE_BACKEND_URL$endpoint" 2>/dev/null || echo "FAILED\n000\n0\n0")
    
    # Parse response
    http_code=$(echo "$response" | tail -3 | head -1)
    time_total=$(echo "$response" | tail -2 | head -1)
    size_download=$(echo "$response" | tail -1)
    body=$(echo "$response" | sed '$d' | sed '$d' | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ OK${NC} (${time_total}s, ${size_download} bytes)"
        return 0
    elif [ "$http_code" = "000" ]; then
        echo -e "${RED}❌ CONNECTION FAILED${NC}"
        return 1
    else
        echo -e "${YELLOW}⚠️  HTTP $http_code${NC} (expected $expected_status)"
        if [ ${#body} -lt 200 ]; then
            echo "   Response: $body"
        fi
        return 1
    fi
}

# Function to check process
check_process() {
    echo -e "\n${BLUE}📊 Process Information${NC}"
    echo -e "${BLUE}=====================${NC}"
    
    # Check if anything is listening on port 8001
    port_check=$(lsof -i :8001 2>/dev/null || echo "")
    if [ -n "$port_check" ]; then
        echo -e "${GREEN}✅ Port 8001 is in use:${NC}"
        echo "$port_check"
    else
        echo -e "${RED}❌ Nothing listening on port 8001${NC}"
        return 1
    fi
    
    # Check for Python/uvicorn processes
    echo -e "\n${BLUE}Python/Uvicorn processes:${NC}"
    ps aux | grep -E "(uvicorn|python.*8001)" | grep -v grep || echo "No relevant processes found"
}

# Function to check network connectivity
check_network() {
    echo -e "\n${BLUE}🌐 Network Connectivity${NC}"
    echo -e "${BLUE}=======================${NC}"
    
    # Check if we can reach localhost
    if ping -c 1 localhost >/dev/null 2>&1; then
        echo -e "${GREEN}✅ localhost reachable${NC}"
    else
        echo -e "${RED}❌ localhost not reachable${NC}"
    fi
    
    # Check if port 8001 is reachable
    if nc -z localhost 8001 2>/dev/null; then
        echo -e "${GREEN}✅ Port 8001 is reachable${NC}"
    else
        echo -e "${RED}❌ Port 8001 is not reachable${NC}"
    fi
}

# Function to get system info
get_system_info() {
    echo -e "\n${BLUE}💻 System Information${NC}"
    echo -e "${BLUE}=====================${NC}"
    
    echo "OS: $(uname -s) $(uname -r)"
    echo "Architecture: $(uname -m)"
    echo "Python version: $(python3 --version 2>/dev/null || echo 'Python3 not found')"
    echo "Current working directory: $(pwd)"
    echo "User: $(whoami)"
    echo "Date: $(date)"
}

# Function to test specific content
test_openapi_content() {
    echo -e "\n${BLUE}📄 OpenAPI Content Analysis${NC}"
    echo -e "${BLUE}===========================${NC}"
    
    # Get openapi.json content
    openapi_content=$(curl -s --connect-timeout $TIMEOUT --max-time $TIMEOUT \
                          "$CORE_BACKEND_URL/openapi.json" 2>/dev/null || echo "")
    
    if [ -n "$openapi_content" ]; then
        # Check if it's valid JSON
        if echo "$openapi_content" | python3 -m json.tool >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Valid JSON format${NC}"
            
            # Extract key information
            title=$(echo "$openapi_content" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('info', {}).get('title', 'Unknown'))" 2>/dev/null || echo "Unknown")
            version=$(echo "$openapi_content" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('info', {}).get('version', 'Unknown'))" 2>/dev/null || echo "Unknown")
            paths_count=$(echo "$openapi_content" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('paths', {})))" 2>/dev/null || echo "0")
            
            echo "   Title: $title"
            echo "   Version: $version"
            echo "   Endpoints: $paths_count"
            
            # Show first 200 characters
            echo "   Content preview:"
            echo "$openapi_content" | head -c 200
            echo "..."
        else
            echo -e "${RED}❌ Invalid JSON format${NC}"
            echo "   Content preview:"
            echo "$openapi_content" | head -c 200
        fi
    else
        echo -e "${RED}❌ No content received${NC}"
    fi
}

# Main diagnostic sequence
main() {
    get_system_info
    check_network
    check_process
    
    echo -e "\n${BLUE}🧪 API Endpoint Tests${NC}"
    echo -e "${BLUE}=====================${NC}"
    
    # Test basic endpoints
    test_endpoint "/health" "Health endpoint"
    test_endpoint "/docs" "Documentation page"
    test_endpoint "/openapi.json" "OpenAPI specification"
    test_endpoint "/status" "Status endpoint"
    
    # Test invalid endpoint
    test_endpoint "/nonexistent" "Invalid endpoint (should fail)" "404"
    
    # Detailed OpenAPI analysis
    test_openapi_content
    
    echo -e "\n${BLUE}📋 Summary${NC}"
    echo -e "${BLUE}==========${NC}"
    echo "If you see failures above, the issue is likely:"
    echo "1. Core Backend not running on the second computer"
    echo "2. Network connectivity issues"
    echo "3. Different port configuration"
    echo "4. Firewall blocking the connection"
    echo ""
    echo "To fix:"
    echo "1. Make sure to run: ./bin/start_server_mode.sh"
    echo "2. Check if port 8001 is free: lsof -i :8001"
    echo "3. Try accessing from browser: http://localhost:8001/docs"
    echo "4. Check logs: ./bin/view_logs.sh"
}

# Run diagnostics
main