#!/usr/bin/env python3
"""
Knowledge Fusion Integration Verification Script
This script verifies if the IBM Knowledge Fusion functionality 
is properly integrated into the OpenWebUI installation.
"""

import sys
import os
import json
import asyncio
import aiohttp
from pathlib import Path

# Add paths for verification
project_root = Path(__file__).parent
openwebui_path = project_root / "openwebuibase"
knowledge_fusion_path = openwebui_path / "knowledge-fusion"

def check_file_exists(file_path, description):
    """Check if a file exists and report status"""
    if file_path.exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (NOT FOUND)")
        return False

def check_directory_structure():
    """Verify the knowledge fusion directory structure"""
    print("🔍 Checking Knowledge Fusion Directory Structure:")
    print("=" * 60)
    
    # Key directories and files
    checks = [
        (knowledge_fusion_path, "Knowledge Fusion Root Directory"),
        (knowledge_fusion_path / "functions/ibm_knowledge_fusion.py", "OpenWebUI Function"),
        (knowledge_fusion_path / "enhanced_backend/main_enhanced.py", "Enhanced Backend"),
        (knowledge_fusion_path / "enhanced_backend/main_novel_architecture.py", "Novel Architecture Backend"),
        (knowledge_fusion_path / "integration/knowledge_synthesis_integrator.py", "Integration Module"),
        (knowledge_fusion_path / "tools/github_repository_analyzer.py", "GitHub Analyzer"),
        (knowledge_fusion_path / "config/github_sources.yml", "GitHub Sources Config"),
        (knowledge_fusion_path / "run_knowledge_fusion.py", "Main Runner"),
        (knowledge_fusion_path / "requirements.txt", "Knowledge Fusion Requirements"),
    ]
    
    all_good = True
    for path, description in checks:
        if not check_file_exists(path, description):
            all_good = False
    
    return all_good

def check_openwebui_integration():
    """Check if OpenWebUI can access the knowledge fusion function"""
    print("\n🔍 Checking OpenWebUI Integration:")
    print("=" * 60)
    
    # Check if function is in the right place for OpenWebUI to find it
    function_file = knowledge_fusion_path / "functions/ibm_knowledge_fusion.py"
    
    if function_file.exists():
        print("✅ IBM Knowledge Fusion function file exists")
        
        # Check function content
        try:
            with open(function_file, 'r') as f:
                content = f.read()
                
            if "class Function:" in content:
                print("✅ Function class definition found")
            else:
                print("❌ Function class definition not found")
                
            if "__call__" in content:
                print("✅ Function __call__ method found")
            else:
                print("❌ Function __call__ method not found")
                
            if "IBM Knowledge Fusion" in content:
                print("✅ IBM Knowledge Fusion branding found")
            else:
                print("❌ IBM Knowledge Fusion branding not found")
                
        except Exception as e:
            print(f"❌ Error reading function file: {e}")
            return False
    else:
        print("❌ IBM Knowledge Fusion function file not found")
        return False
    
    return True

async def check_backend_connectivity():
    """Check if the knowledge fusion backend endpoints are accessible"""
    print("\n🔍 Checking Backend Connectivity:")
    print("=" * 60)
    
    # Test URLs for the enhanced backends
    test_urls = [
        ("http://localhost:8001/health", "Enhanced Backend Health"),
        ("http://localhost:8002/health", "Novel Architecture Backend Health"),
        ("http://localhost:8001/knowledge-fusion/status", "Knowledge Fusion Status"),
    ]
    
    connectivity_results = []
    
    for url, description in test_urls:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        print(f"✅ {description}: {url}")
                        connectivity_results.append(True)
                    else:
                        print(f"❌ {description}: {url} (Status: {response.status})")
                        connectivity_results.append(False)
        except Exception as e:
            print(f"❌ {description}: {url} (Error: {str(e)[:50]})")
            connectivity_results.append(False)
    
    return any(connectivity_results)

def check_openwebui_status():
    """Check if OpenWebUI is running and accessible"""
    print("\n🔍 Checking OpenWebUI Status:")
    print("=" * 60)
    
    # Check if OpenWebUI process is running
    try:
        import requests
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ OpenWebUI is running on http://localhost:3000")
            return True
        else:
            print(f"❌ OpenWebUI returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OpenWebUI not accessible: {str(e)[:50]}")
        return False

def generate_integration_report():
    """Generate a comprehensive integration report"""
    print("\n📊 INTEGRATION VERIFICATION REPORT")
    print("=" * 60)
    
    # Run all checks
    structure_ok = check_directory_structure()
    integration_ok = check_openwebui_integration()
    
    print(f"\n📋 Summary:")
    print(f"Directory Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")
    print(f"OpenWebUI Integration: {'✅ PASS' if integration_ok else '❌ FAIL'}")
    
    # Instructions based on results
    print(f"\n📝 Instructions:")
    
    if structure_ok and integration_ok:
        print("""
✅ Knowledge Fusion appears to be properly integrated!

Next steps to use it:
1. Start the knowledge fusion backend:
   cd openwebuibase/knowledge-fusion
   python run_knowledge_fusion.py

2. Start OpenWebUI (if not already running):
   ./start_openwebui.sh

3. In OpenWebUI interface:
   - Go to Settings → Functions
   - Look for "IBM Knowledge Fusion" function
   - Enable/activate it
   - Test it in a chat conversation

4. Test the integration by asking questions that would benefit from
   multi-source knowledge synthesis.
        """)
    else:
        print("""
❌ Integration issues detected. Please check:

1. Ensure all knowledge fusion files are in place
2. Verify the function follows OpenWebUI function format
3. Check that backends can be started without errors
4. Confirm OpenWebUI can load custom functions
        """)
    
    return structure_ok and integration_ok

async def main():
    """Main verification function"""
    print("🚀 IBM Knowledge Fusion Integration Verification")
    print("=" * 60)
    print(f"Project Root: {project_root}")
    print(f"OpenWebUI Path: {openwebui_path}")
    print(f"Knowledge Fusion Path: {knowledge_fusion_path}")
    
    # Run verification
    overall_status = generate_integration_report()
    
    # Also check connectivity (async)
    print("\n🔍 Testing Backend Connectivity (Async):")
    print("=" * 60)
    connectivity_ok = await check_backend_connectivity()
    
    openwebui_ok = check_openwebui_status()
    
    print(f"\n🎯 FINAL STATUS:")
    print(f"Knowledge Fusion Integration: {'✅ READY' if overall_status else '❌ NEEDS SETUP'}")
    print(f"Backend Connectivity: {'✅ AVAILABLE' if connectivity_ok else '❌ OFFLINE'}")
    print(f"OpenWebUI Status: {'✅ RUNNING' if openwebui_ok else '❌ NOT RUNNING'}")
    
    if overall_status:
        print(f"\n🎉 Your Knowledge Fusion integration is set up correctly!")
        if not connectivity_ok:
            print(f"💡 Tip: Start the knowledge fusion backends for full functionality")
        if not openwebui_ok:
            print(f"💡 Tip: Start OpenWebUI to access the interface")
    else:
        print(f"\n⚠️  Integration setup needs attention. See instructions above.")

if __name__ == "__main__":
    asyncio.run(main())
