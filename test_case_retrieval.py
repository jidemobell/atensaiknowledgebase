#!/usr/bin/env python3
"""
Test script to verify multi-source knowledge retrieval in unified knowledge fusion
Tests retrieval from: Cases, Code, Documentation, ASM Repositories
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

# Configuration
CORE_BACKEND_URL = "http://localhost:8001"
UNIFIED_FUSION_URL = "http://localhost:8002"

async def test_core_backend_search():
    """Test the Core Backend multi-source search endpoint"""
    print("🔍 Testing Core Backend multi-source search...")
    
    try:
        async with aiohttp.ClientSession() as session:
            search_request = {
                "query": "OpenStack topology merge issue kubernetes",
                "search_mode": "all",  # Search ALL knowledge sources
                "session_id": "test_session",
                "filters": {}
            }
            
            async with session.post(
                f"{CORE_BACKEND_URL}/api/search",
                json=search_request,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Multi-source search successful!")
                    print(f"   Total results: {result.get('total_results', 0)}")
                    print(f"   📋 Cases found: {len(result.get('case_results', []))}")
                    print(f"   💻 Code results: {len(result.get('code_results', []))}")
                    print(f"   📚 Doc results: {len(result.get('doc_results', []))}")
                    print(f"   🔧 ASM repo results: {len(result.get('asm_results', []))}")
                    
                    # Show samples from each source type
                    case_results = result.get('case_results', [])
                    if case_results:
                        first_case = case_results[0]
                        print(f"\n📋 Sample case:")
                        print(f"   Case: {first_case.get('case_number', 'Unknown')}")
                        print(f"   Title: {first_case.get('title', 'No title')[:80]}...")
                        print(f"   Services: {first_case.get('affected_services', [])}")
                        print(f"   Search Score: {first_case.get('search_score', 0):.2f}")
                    
                    code_results = result.get('code_results', [])
                    if code_results:
                        first_code = code_results[0]
                        print(f"\n💻 Sample code:")
                        print(f"   Repo: {first_code.get('repository', 'Unknown')}")
                        print(f"   File: {first_code.get('file_path', 'Unknown')}")
                        print(f"   Content: {first_code.get('code_content', '')[:100]}...")
                    
                    doc_results = result.get('doc_results', [])
                    if doc_results:
                        first_doc = doc_results[0]
                        print(f"\n📚 Sample documentation:")
                        print(f"   Title: {first_doc.get('title', 'Unknown')}")
                        print(f"   Type: {first_doc.get('doc_type', 'Unknown')}")
                        print(f"   Content: {first_doc.get('content', '')[:100]}...")
                    
                    return result
                else:
                    print(f"❌ Multi-source search failed: {response.status}")
                    text = await response.text()
                    print(f"   Error response: {text[:200]}")
                    
    except Exception as e:
        print(f"❌ Multi-source search error: {e}")
    
    return None

async def test_unified_fusion():
    """Test the unified knowledge fusion system with multi-source retrieval"""
    print("\n🔗 Testing Unified Knowledge Fusion with Multi-Source Retrieval...")
    
    try:
        async with aiohttp.ClientSession() as session:
            fusion_request = {
                "query": "How do I resolve OpenStack topology merge conflicts in ASM Kubernetes environment?",
                "conversation_id": "test_fusion",
                "include_technical_details": True
            }
            
            async with session.post(
                f"{UNIFIED_FUSION_URL}/fuse",
                json=fusion_request,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Unified fusion successful!")
                    print(f"   Response length: {len(result.get('response', ''))}")
                    print(f"   Confidence: {result.get('confidence', 0):.2f}")
                    print(f"   Sources used: {result.get('sources_used', [])}")
                    
                    # Show part of the response
                    response_text = result.get('response', '')
                    if response_text:
                        print(f"\n💬 Response preview:")
                        print(f"   {response_text[:300]}...")
                        
                        # Check if response mentions specific retrieved knowledge
                        knowledge_indicators = ['Case', 'case', 'repository', 'documentation', 'code', 'similar']
                        found_indicators = [ind for ind in knowledge_indicators if ind in response_text]
                        if found_indicators:
                            print(f"   ✅ Response references retrieved knowledge: {found_indicators}")
                        else:
                            print(f"   ⚠️  Response may not be using retrieved knowledge")
                    
                    # Show detailed retrieval analysis
                    core_analysis = result.get('core_analysis', {})
                    if core_analysis:
                        print(f"\n🔍 Multi-source retrieval analysis:")
                        print(f"   Total results: {core_analysis.get('total_results', 0)}")
                        print(f"   📋 Cases: {len(core_analysis.get('case_results', []))}")
                        print(f"   💻 Code: {len(core_analysis.get('code_results', []))}")
                        print(f"   📚 Docs: {len(core_analysis.get('doc_results', []))}")
                        
                        search_metadata = core_analysis.get('search_metadata', {})
                        if search_metadata:
                            print(f"   Search metadata:")
                            print(f"     - Has case matches: {search_metadata.get('has_case_matches', False)}")
                            print(f"     - Has code matches: {search_metadata.get('has_code_matches', False)}")
                            print(f"     - Has doc matches: {search_metadata.get('has_doc_matches', False)}")
                    
                    return result
                else:
                    print(f"❌ Unified fusion failed: {response.status}")
                    text = await response.text()
                    print(f"   Error response: {text[:200]}")
                    
    except Exception as e:
        print(f"❌ Unified fusion error: {e}")
    
    return None

async def check_knowledge_sources():
    """Check all knowledge sources available"""
    print("\n📚 Checking multi-source knowledge base...")
    
    total_sources = 0
    
    # Check enterprise knowledge base (cases)
    try:
        with open("enterprise_knowledge_base.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cases = data.get('cases', [])
        code_entries = data.get('code', [])
        docs = data.get('documentation', [])
        asm_repos = data.get('asm_repositories', [])
        
        print(f"✅ Enterprise knowledge base loaded:")
        print(f"   📋 Cases: {len(cases)}")
        print(f"   💻 Code entries: {len(code_entries)}")
        print(f"   📚 Documentation: {len(docs)}")
        print(f"   🔧 ASM repositories: {len(asm_repos)}")
        
        total_sources = len(cases) + len(code_entries) + len(docs) + len(asm_repos)
        
        if cases:
            # Show some case statistics
            services_count = {}
            for case in cases:
                for service in case.get('services', []):
                    services_count[service] = services_count.get(service, 0) + 1
            
            print(f"   Top case services:")
            for service, count in sorted(services_count.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"     - {service}: {count} cases")
        
        if code_entries:
            repos = set(entry.get('repository', 'Unknown') for entry in code_entries)
            print(f"   Code repositories: {list(repos)[:3]}")
        
        if docs:
            doc_types = set(doc.get('doc_type', 'Unknown') for doc in docs)
            print(f"   Documentation types: {list(doc_types)}")
            
    except FileNotFoundError:
        print("❌ enterprise_knowledge_base.json not found")
    except Exception as e:
        print(f"❌ Error reading knowledge base: {e}")
    
    # Check other knowledge sources
    try:
        if total_sources == 0:
            print("⚠️  Checking individual knowledge files...")
            
            # Check if knowledge_base.json exists
            try:
                with open("knowledge_base.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                alt_cases = data.get('cases', [])
                if alt_cases:
                    print(f"   Found alternative knowledge_base.json: {len(alt_cases)} cases")
                    total_sources += len(alt_cases)
            except FileNotFoundError:
                pass
    except Exception as e:
        print(f"⚠️  Error checking alternative sources: {e}")
    
    return total_sources

async def main():
    """Main test function"""
    print("🧪 Testing Multi-Source Knowledge Retrieval in Unified Fusion System")
    print("=" * 70)
    
    # Check all knowledge sources first
    total_sources = await check_knowledge_sources()
    if total_sources == 0:
        print("⚠️  No knowledge sources found - retrieval test may not be meaningful")
    
    # Test Core Backend search
    core_result = await test_core_backend_search()
    
    # Test unified fusion
    fusion_result = await test_unified_fusion()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)
    
    if core_result:
        print(f"✅ Core Backend search: Working ({core_result.get('total_results', 0)} results)")
    else:
        print("❌ Core Backend search: Failed")
    
    if fusion_result:
        print(f"✅ Unified fusion: Working (confidence: {fusion_result.get('confidence', 0):.2f})")
        
        # Check if fusion is using case results
        core_analysis = fusion_result.get('core_analysis', {})
        case_results = core_analysis.get('case_results', [])
        if case_results:
            print(f"✅ Multi-source retrieval: Working ({len(case_results)} total sources retrieved)")
            
            # Check specific source types
            core_analysis = fusion_result.get('core_analysis', {})
            case_count = len(core_analysis.get('case_results', []))
            code_count = len(core_analysis.get('code_results', []))
            doc_count = len(core_analysis.get('doc_results', []))
            
            print(f"   📋 Cases: {case_count}, 💻 Code: {code_count}, 📚 Docs: {doc_count}")
        else:
            print("⚠️  Multi-source retrieval: No knowledge sources retrieved")
    else:
        print("❌ Unified fusion: Failed")
    
    print(f"\n💡 Total knowledge sources: {total_sources} entries")
    
if __name__ == "__main__":
    asyncio.run(main())