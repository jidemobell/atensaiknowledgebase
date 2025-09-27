#!/usr/bin/env python3
"""
Multi-Agent System Diagnostic Tool
Check if Phase 2 Multi-Agent Intelligence is working on your system
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_gateway_endpoints():
    """Test all gateway endpoints to verify multi-agent availability"""
    print("🔍 Testing Gateway Endpoints...")
    
    try:
        import aiohttp
    except ImportError:
        print("❌ aiohttp not installed. Install with: pip install aiohttp")
        return False
    
    gateway_url = "http://localhost:9000"
    endpoints_to_test = [
        ("/health", "Health Check"),
        ("/knowledge-fusion/query", "Phase 1 Standard Processing"),
        ("/knowledge-fusion/intelligent", "Phase 2 Intelligent Routing"),
        ("/knowledge-fusion/multi-agent", "Phase 2 Multi-Agent Processing")
    ]
    
    results = {}
    
    async with aiohttp.ClientSession() as session:
        for endpoint, description in endpoints_to_test:
            try:
                print(f"  Testing {endpoint} ({description})...")
                
                if endpoint == "/health":
                    async with session.get(f"{gateway_url}{endpoint}") as response:
                        if response.status == 200:
                            data = await response.json()
                            results[endpoint] = {
                                "status": "✅ Available",
                                "capabilities": data.get("capabilities", {}),
                                "version": data.get("version", "unknown")
                            }
                        else:
                            results[endpoint] = {"status": f"❌ HTTP {response.status}"}
                else:
                    # Test with a simple query
                    test_query = {
                        "query": "What is ASM topology service nasm-topology?",
                        "conversation_id": "diagnostic_test",
                        "context": {"test_mode": True}
                    }
                    
                    async with session.post(
                        f"{gateway_url}{endpoint}",
                        json=test_query,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            processing_details = data.get("processing_details", {})
                            agents_consulted = processing_details.get("agents_consulted", 0)
                            multi_agent_enabled = processing_details.get("multi_agent_enabled", False)
                            
                            results[endpoint] = {
                                "status": "✅ Available",
                                "multi_agent_enabled": multi_agent_enabled,
                                "agents_consulted": agents_consulted,
                                "response_length": len(data.get("response", "")),
                                "confidence": data.get("confidence", 0)
                            }
                        elif response.status == 404:
                            results[endpoint] = {"status": "❌ Not Available (404)"}
                        else:
                            results[endpoint] = {"status": f"❌ HTTP {response.status}"}
                            
            except asyncio.TimeoutError:
                results[endpoint] = {"status": "⏱️ Timeout (>10s)"}
            except aiohttp.ClientConnectorError:
                results[endpoint] = {"status": "🔌 Connection Failed"}
            except Exception as e:
                results[endpoint] = {"status": f"❌ Error: {str(e)}"}
    
    return results

async def check_multi_agent_dependencies():
    """Check if multi-agent system dependencies are available"""
    print("\n🧪 Checking Multi-Agent Dependencies...")
    
    dependencies = [
        ("multi_agent_foundation", "Multi-Agent Foundation Classes"),
        ("specialized_knowledge_agents", "Specialized Knowledge Agents"),
        ("multi_agent_orchestrator", "Multi-Agent Orchestrator"),
        ("simple_case_clustering", "Case Clustering System")
    ]
    
    available_deps = {}
    
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            available_deps[module_name] = {"status": "✅ Available", "description": description}
        except ImportError as e:
            available_deps[module_name] = {"status": f"❌ Missing: {str(e)}", "description": description}
        except Exception as e:
            available_deps[module_name] = {"status": f"⚠️ Error: {str(e)}", "description": description}
    
    return available_deps

async def check_knowledge_sources():
    """Check if knowledge sources are properly configured"""
    print("\n📚 Checking Knowledge Sources...")
    
    knowledge_sources = {
        "enterprise_knowledge_base.json": "Processed Support Cases",
        "knowledge_base.json": "Core Knowledge Base",
        "data/asm_repositories/": "ASM Repository Data",
        "data/support_cases/": "Support Case Files",
        "data/case_studies/": "Case Study Files"
    }
    
    source_status = {}
    
    for source, description in knowledge_sources.items():
        if os.path.exists(source):
            if os.path.isfile(source):
                size = os.path.getsize(source)
                source_status[source] = {
                    "status": "✅ Available",
                    "description": description,
                    "size": f"{size:,} bytes"
                }
            else:
                # Directory
                try:
                    files = os.listdir(source)
                    source_status[source] = {
                        "status": "✅ Available",
                        "description": description,
                        "files": len(files)
                    }
                except:
                    source_status[source] = {
                        "status": "⚠️ Directory exists but not accessible",
                        "description": description
                    }
        else:
            source_status[source] = {
                "status": "❌ Not Found",
                "description": description
            }
    
    return source_status

def print_diagnostic_results(endpoint_results, dependency_results, source_results):
    """Print comprehensive diagnostic results"""
    print("\n" + "="*80)
    print("🎯 MULTI-AGENT SYSTEM DIAGNOSTIC RESULTS")
    print("="*80)
    
    # Gateway Endpoints
    print("\n📡 GATEWAY ENDPOINT STATUS:")
    print("-" * 40)
    
    multi_agent_working = False
    
    for endpoint, result in endpoint_results.items():
        status = result["status"]
        print(f"{endpoint:<35} {status}")
        
        if endpoint == "/health" and "✅" in status:
            capabilities = result.get("capabilities", {})
            version = result.get("version", "unknown")
            print(f"   Version: {version}")
            if capabilities.get("multi_agent_system"):
                print(f"   Multi-Agent System: ✅ Enabled")
                multi_agent_working = True
            else:
                print(f"   Multi-Agent System: ❌ Disabled")
        
        elif "multi-agent" in endpoint and "✅" in status:
            agents_consulted = result.get("agents_consulted", 0)
            multi_agent_enabled = result.get("multi_agent_enabled", False)
            confidence = result.get("confidence", 0)
            
            if multi_agent_enabled and agents_consulted > 0:
                print(f"   Agents Consulted: {agents_consulted}")
                print(f"   Confidence: {confidence:.1%}")
                multi_agent_working = True
    
    # Dependencies
    print("\n🧪 MULTI-AGENT DEPENDENCIES:")
    print("-" * 40)
    
    all_deps_available = True
    for module, result in dependency_results.items():
        status = result["status"]
        description = result["description"]
        print(f"{description:<35} {status}")
        if "❌" in status:
            all_deps_available = False
    
    # Knowledge Sources
    print("\n📚 KNOWLEDGE SOURCES:")
    print("-" * 40)
    
    sources_available = 0
    for source, result in source_results.items():
        status = result["status"]
        description = result["description"]
        print(f"{description:<35} {status}")
        if "✅" in status:
            sources_available += 1
            if "size" in result:
                print(f"   Size: {result['size']}")
            elif "files" in result:
                print(f"   Files: {result['files']}")
    
    # Overall Assessment
    print("\n🎯 OVERALL ASSESSMENT:")
    print("-" * 40)
    
    if multi_agent_working and all_deps_available:
        print("✅ Multi-Agent System: FULLY OPERATIONAL")
        print("   Phase 2 Intelligence is working correctly")
    elif multi_agent_working:
        print("⚠️ Multi-Agent System: PARTIALLY WORKING")
        print("   Some dependencies missing but core functionality available")
    elif all_deps_available:
        print("⚠️ Multi-Agent System: READY BUT NOT ACTIVE")
        print("   Dependencies available but system not responding")
    else:
        print("❌ Multi-Agent System: NOT OPERATIONAL")
        print("   Missing dependencies and/or not responding")
    
    print(f"\nKnowledge Sources: {sources_available}/{len(source_results)} available")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 40)
    
    if not multi_agent_working:
        print("1. Restart the Knowledge Fusion Gateway:")
        print("   ./bin/start_server_mode.sh")
        print("   OR manually restart the gateway service")
    
    if not all_deps_available:
        print("2. Install missing dependencies:")
        print("   pip install -r requirements.txt")
        print("   pip install -r requirements_clustering.txt")
    
    if sources_available < 2:
        print("3. Set up knowledge sources:")
        print("   python enterprise_case_processor.py")
        print("   mkdir -p data/support_cases data/case_studies")
    
    if multi_agent_working:
        print("4. ✅ Update OpenWebUI function to use multi-agent endpoints")
        print("   Re-upload the updated knowledge_fusion_function.py")

async def main():
    """Main diagnostic execution"""
    print("🎯 Multi-Agent System Diagnostic Tool")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Run all diagnostic checks
    endpoint_results = await test_gateway_endpoints()
    dependency_results = await check_multi_agent_dependencies()
    source_results = await check_knowledge_sources()
    
    # Print comprehensive results
    print_diagnostic_results(endpoint_results, dependency_results, source_results)
    
    # Save results to file
    diagnostic_data = {
        "timestamp": datetime.now().isoformat(),
        "gateway_endpoints": endpoint_results,
        "dependencies": dependency_results,
        "knowledge_sources": source_results
    }
    
    with open("multi_agent_diagnostic_results.json", "w") as f:
        json.dump(diagnostic_data, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: multi_agent_diagnostic_results.json")
    print("\n🚀 To fix issues, run the recommended commands above.")

if __name__ == "__main__":
    asyncio.run(main())