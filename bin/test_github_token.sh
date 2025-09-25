#!/bin/bash
# GitHub Token Test Script
# Validates your GitHub token setup

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 GitHub Token Test${NC}"
echo "==================="

# Check if token is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}❌ GITHUB_TOKEN environment variable is not set${NC}"
    echo ""
    echo "Please run: ./bin/setup_github_token.sh"
    exit 1
fi

echo -e "${GREEN}✅ GITHUB_TOKEN is set${NC}"
echo "   Token preview: ${GITHUB_TOKEN:0:8}..."
echo ""

# Test basic API access
echo "🔍 Testing GitHub API access..."
response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)

if [ $? -eq 0 ]; then
    username=$(echo "$response" | grep -o '"login":"[^"]*' | cut -d'"' -f4)
    if [ -n "$username" ]; then
        echo -e "${GREEN}✅ API access successful${NC}"
        echo "   Authenticated as: $username"
    else
        echo -e "${RED}❌ API access failed - invalid token${NC}"
        echo "Response: $response"
        exit 1
    fi
else
    echo -e "${RED}❌ Network error accessing GitHub API${NC}"
    exit 1
fi

# Test rate limits
echo ""
echo "📊 Checking rate limits..."
rate_response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit)
remaining=$(echo "$rate_response" | grep -o '"remaining":[0-9]*' | cut -d':' -f2)
limit=$(echo "$rate_response" | grep -o '"limit":[0-9]*' | cut -d':' -f2)

if [ -n "$remaining" ] && [ -n "$limit" ]; then
    echo -e "${GREEN}✅ Rate limit info retrieved${NC}"
    echo "   Remaining requests: $remaining/$limit"
else
    echo -e "${YELLOW}⚠️  Could not retrieve rate limit info${NC}"
fi

# Test repository access (using a public repo)
echo ""
echo "🔍 Testing repository access..."
repo_response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/octocat/Hello-World)
repo_name=$(echo "$repo_response" | grep -o '"name":"[^"]*' | cut -d'"' -f4)

if [ "$repo_name" = "Hello-World" ]; then
    echo -e "${GREEN}✅ Repository access successful${NC}"
else
    echo -e "${YELLOW}⚠️  Repository access test inconclusive${NC}"
fi

echo ""
echo -e "${GREEN}🎯 GitHub token setup appears to be working correctly!${NC}"
echo ""
echo "Your token can be used with:"
echo "• github_sources.yml configuration"
echo "• Knowledge Fusion GitHub integration"
echo "• Private repository access"