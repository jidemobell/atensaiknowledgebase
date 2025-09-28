# Testing Enhanced Multi-Source Knowledge Retrieval

## What Was Fixed

The unified knowledge fusion system was only calling Core Backend's `/query` endpoint, which doesn't search through your knowledge sources. It has been enhanced to:

1. **Call `/api/search` endpoint** - Uses Core Backend's unified search across all knowledge sources
2. **Enhanced prompts** - Now includes actual retrieved content from cases, code, documentation, and ASM repositories
3. **Multi-source retrieval** - Searches through all 52 cases + code + docs + ASM repos on your IBM computer

## Testing Steps

### 1. Start Core Backend (if not already running)
```bash
cd /path/to/your/project
python corebackend/implementation/backend/main_enhanced.py
```

### 2. Start Enhanced Unified Fusion System
```bash
./start_enhanced_fusion.sh
```

### 3. Run Multi-Source Retrieval Test
```bash
python test_case_retrieval.py
```

### 4. Test with Real Query
```bash
curl -X POST http://localhost:8002/fuse \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I resolve OpenStack topology merge conflicts in ASM Kubernetes environment?",
    "conversation_id": "test",
    "include_technical_details": true
  }'
```

## What to Look For

### Good Signs (System Working):
- ✅ Test shows "Multi-source search successful" with results from multiple sources
- ✅ Response references specific cases, code examples, or documentation
- ✅ High confidence scores (>0.7)
- ✅ Core analysis shows retrieved knowledge from cases/code/docs
- ✅ Response mentions case numbers, repositories, or specific technical details

### Warning Signs (System Not Working):
- ⚠️  "No knowledge sources found" or zero results
- ⚠️  Generic responses without specific case references
- ⚠️  Low confidence scores (<0.3)
- ⚠️  Response doesn't mention retrieved knowledge

## Example Good Response Should Include:
- References to actual case numbers from your 52 cases
- Code snippets from ASM repositories
- Documentation references
- Specific technical solutions based on retrieved knowledge
- High relevance to your query

## Troubleshooting

### If Core Backend Search Fails:
1. Check Core Backend is running: `curl http://localhost:8001/api/cases`
2. Verify enterprise_knowledge_base.json exists and has your 52 cases
3. Check Core Backend logs for search errors

### If Unified Fusion Fails:
1. Check Granite model: `curl http://localhost:11434/api/tags | grep granite`
2. Verify unified_knowledge_fusion.py is using updated code
3. Check port 8002 is available

### If No Knowledge Retrieved:
1. Verify your enterprise_knowledge_base.json contains multiple source types
2. Check Core Backend enhanced mode is enabled
3. Test Core Backend search directly: `curl -X POST http://localhost:8001/api/search -H "Content-Type: application/json" -d '{"query":"test","search_mode":"all"}'`

## Compare with Original Granite Template

The enhanced system should now provide:
- **Specific case references** instead of generic responses
- **Code examples** from your ASM repositories
- **Documentation quotes** when relevant
- **Multi-source intelligence** combining cases + code + docs
- **High confidence** when relevant knowledge is found

This addresses the performance degradation you experienced when moving from the granite retrieval agent template to the unified system.