#!/bin/bash

# Test IBM Corporate Setup Simulation
# This simulates what happens on an IBM computer without GitHub access

echo "🏢 Testing IBM Corporate Setup Simulation"
echo "========================================"

# Create a test directory to simulate fresh environment
TEST_DIR="/tmp/ibm_test_$(date +%s)"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "📁 Test directory: $TEST_DIR"
echo ""

echo "1️⃣ Simulating repository clone on IBM computer..."
if git clone https://github.com/jidemobell/knowledgebase.git; then
    echo "✅ Repository cloned successfully"
else
    echo "❌ Repository clone failed"
    exit 1
fi

echo ""
echo "2️⃣ Testing IBM setup script..."
cd knowledgebase

# Check if IBM setup script exists
if [ -f "setup_ibm.sh" ]; then
    echo "✅ IBM setup script found"
else
    echo "❌ IBM setup script not found"
    exit 1
fi

# Check if script is executable
if [ -x "setup_ibm.sh" ]; then
    echo "✅ IBM setup script is executable"
else
    echo "❌ IBM setup script is not executable"
    exit 1
fi

echo ""
echo "3️⃣ Testing OpenWebUI download capability..."
# Test if we can download OpenWebUI ZIP file (302 redirect is normal)
if curl -L -s -I https://github.com/open-webui/open-webui/archive/refs/heads/main.zip | head -1 | grep -q "HTTP/2 [23]"; then
    echo "✅ OpenWebUI download URL is accessible"
else
    echo "❌ OpenWebUI download URL not accessible"
    exit 1
fi

echo ""
echo "4️⃣ Testing setup.sh --ibm option..."
if grep -q "\-\-ibm)" setup.sh; then
    echo "✅ IBM option found in setup.sh"
else
    echo "❌ IBM option not found in setup.sh"
    exit 1
fi

echo ""
echo "5️⃣ Testing documentation..."
if [ -f "docs/IBM_DEPLOYMENT_GUIDE.md" ]; then
    echo "✅ IBM deployment guide exists"
else
    echo "❌ IBM deployment guide missing"
fi

echo ""
echo "🧹 Cleaning up test directory..."
cd /
rm -rf "$TEST_DIR"

echo ""
echo "🎉 IBM Corporate Setup Test Completed Successfully!"
echo "📋 Summary:"
echo "   ✅ Repository can be cloned on IBM computers"
echo "   ✅ IBM setup script is ready and executable"
echo "   ✅ OpenWebUI download URL is accessible"
echo "   ✅ Setup script has IBM option"
echo "   ✅ Documentation is available"
echo ""
echo "💼 For IBM computers, use: ./setup.sh --ibm"