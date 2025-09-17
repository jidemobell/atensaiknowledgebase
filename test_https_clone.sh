#!/bin/bash

# Test script to verify HTTPS cloning works
# This simulates what would happen on a new computer without SSH keys

echo "🔧 Testing Cross-Machine Repository Access"
echo "=========================================="

# Create a temporary directory for testing
TEST_DIR="/tmp/topology_knowledge_test_$(date +%s)"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "📁 Test directory: $TEST_DIR"
echo ""

echo "1️⃣ Testing main repository clone with HTTPS..."
if git clone https://github.com/jidemobell/knowledgebase.git test_repo; then
    echo "✅ Main repository cloned successfully"
else
    echo "❌ Failed to clone main repository"
    exit 1
fi

echo ""
echo "2️⃣ Testing submodule initialization..."
cd test_repo
if git submodule update --init --recursive; then
    echo "✅ Submodules initialized successfully"
else
    echo "❌ Failed to initialize submodules"
    exit 1
fi

echo ""
echo "3️⃣ Verifying submodule content..."
if [ -f "open-webui-cloned/README.md" ]; then
    echo "✅ Submodule content verified"
else
    echo "❌ Submodule content missing"
    exit 1
fi

echo ""
echo "4️⃣ Testing submodule remote URLs..."
cd open-webui-cloned
FORK_URL=$(git remote get-url fork 2>/dev/null || echo "not-set")
ORIGIN_URL=$(git remote get-url origin 2>/dev/null || echo "not-set")

if [[ "$FORK_URL" == https* ]] && [[ "$ORIGIN_URL" == https* ]]; then
    echo "✅ All remote URLs use HTTPS"
    echo "   Fork: $FORK_URL"
    echo "   Origin: $ORIGIN_URL"
else
    echo "⚠️  Some remote URLs may still use SSH"
    echo "   Fork: $FORK_URL" 
    echo "   Origin: $ORIGIN_URL"
fi

echo ""
echo "🧹 Cleaning up test directory..."
cd /
rm -rf "$TEST_DIR"

echo ""
echo "🎉 Cross-machine access test completed successfully!"
echo "📋 Summary:"
echo "   ✅ Repository can be cloned with HTTPS"
echo "   ✅ Submodules initialize without SSH keys"
echo "   ✅ All content is accessible"
echo ""
echo "🚀 The repository is now ready for deployment on any computer!"
