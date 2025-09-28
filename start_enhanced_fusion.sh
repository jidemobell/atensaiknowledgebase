#!/bin/bash
# Start the enhanced unified knowledge fusion system with case retrieval

echo "🚀 Starting Enhanced Knowledge Fusion System with Multi-Source Retrieval"
echo "========================================================================"

# Check if Core Backend is running
echo "🔍 Checking Core Backend (port 8001)..."
if ! curl -s http://localhost:8001/api/cases > /dev/null 2>&1; then
    echo "⚠️  Core Backend not running on port 8001"
    echo "   Please start it first with: python corebackend/implementation/backend/main_enhanced.py"
    echo ""
else
    echo "✅ Core Backend is running"
fi

# Check if granite model is available
echo "🔍 Checking Granite model..."
if ! curl -s http://localhost:11434/api/tags | grep -q "granite3.2:8b"; then
    echo "⚠️  Granite model not available"
    echo "   Please ensure Ollama is running with granite3.2:8b model"
    echo ""
else
    echo "✅ Granite model is available"
fi

# Check multi-source knowledge base
echo "🔍 Checking multi-source knowledge base..."
if [ -f "enterprise_knowledge_base.json" ]; then
    python3 -c "
import json
try:
    with open('enterprise_knowledge_base.json') as f:
        data = json.load(f)
    cases = len(data.get('cases', []))
    code = len(data.get('code', []))
    docs = len(data.get('documentation', []))
    asm = len(data.get('asm_repositories', []))
    total = cases + code + docs + asm
    print(f'✅ Multi-source knowledge base found: {total} total entries')
    print(f'   📋 Cases: {cases}, 💻 Code: {code}, 📚 Docs: {docs}, 🔧 ASM: {asm}')
except Exception as e:
    print(f'⚠️  Error reading knowledge base: {e}')
    "
else
    echo "⚠️  enterprise_knowledge_base.json not found"
    echo "   Please ensure your multi-source knowledge base is available"
    echo ""
fi

echo ""
echo "🔗 Starting Enhanced Unified Knowledge Fusion on port 8002..."
echo "   - Uses Core Backend search API for multi-source retrieval"
echo "   - Enhanced prompts with cases, code, docs, and ASM repo content"
echo "   - Granite AI synthesis with comprehensive retrieved knowledge"
echo "   - Supports: Cases, Code, Documentation, ASM Repositories"
echo ""

# Start the enhanced unified fusion system
python unified_knowledge_fusion.py