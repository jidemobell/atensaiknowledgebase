#!/bin/bash

# =============================================================================
# CORE BACKEND MANUAL TEST
# =============================================================================
# Test Core Backend endpoints manually
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_URL="http://localhost:8001"

echo -e "${BLUE}🧪 Core Backend Manual Test${NC}"
echo -e "${BLUE}===========================${NC}"
echo ""

test_endpoint() {
    local endpoint="$1"
    local method="${2:-GET}"
    local description="$3"
    
    echo -n "Testing $description... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" "$BASE_URL$endpoint" 2>/dev/null)
        http_code="${response: -3}"
        body="${response%???}"
    else
        # For POST requests, we'll add later if needed
        response=$(curl -s -w "%{http_code}" -X "$method" "$BASE_URL$endpoint" 2>/dev/null)
        http_code="${response: -3}"
        body="${response%???}"
    fi
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        if [ ${#body} -gt 0 ] && [ ${#body} -lt 200 ]; then
            echo "   Response: $body"
        elif [ ${#body} -gt 200 ]; then
            echo "   Response: ${body:0:100}... (truncated)"
        fi
    else
        echo -e "${RED}❌ HTTP $http_code${NC}"
        if [ ${#body} -gt 0 ] && [ ${#body} -lt 200 ]; then
            echo "   Error: $body"
        fi
    fi
    echo ""
}

# Check if Core Backend is running
if ! curl -s "$BASE_URL/health" >/dev/null 2>&1; then
    echo -e "${RED}❌ Core Backend is not running on $BASE_URL${NC}"
    echo -e "${YELLOW}Start it with: ./bin/run_core_backend_standalone.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Core Backend is running${NC}"
echo ""

# Test all endpoints
test_endpoint "/health" "GET" "Health check"
test_endpoint "/status" "GET" "System status"
test_endpoint "/openapi.json" "GET" "OpenAPI specification"
test_endpoint "/docs" "GET" "API documentation"
test_endpoint "/cases/list" "GET" "List cases"

echo -e "${BLUE}🌐 Browser Tests:${NC}"
echo -e "1. Open: ${YELLOW}$BASE_URL/docs${NC}"
echo -e "2. Open: ${YELLOW}$BASE_URL/health${NC}"
echo -e "3. Open: ${YELLOW}$BASE_URL/openapi.json${NC}"
echo ""

echo -e "${BLUE}📱 Quick curl tests:${NC}"
echo -e "curl $BASE_URL/health"
echo -e "curl $BASE_URL/openapi.json | jq ."
echo -e "curl $BASE_URL/status"