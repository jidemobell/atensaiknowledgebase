#!/usr/bin/env python3
"""
Test script to validate the new ASM local repository integration
"""

import os
import sys
import json
from pathlib import Path

# Add the corebackend to path for imports
sys.path.append('corebackend/implementation/backend')

try:
    from knowledge_extractor import KnowledgeExtractor
    from multi_source_manager import MultiSourceManager
    print("✅ Successfully imported updated Core Backend modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Note: This is expected if not in the virtual environment")

def test_asm_directory_structure():
    """Test if ASM directory structure exists"""
    asm_dir = Path("data/asm_repositories")
    
    print(f"\n🔍 Checking ASM directory structure at {asm_dir}")
    
    if asm_dir.exists():
        print("✅ ASM repositories directory exists")
        
        subdirs = [d for d in asm_dir.iterdir() if d.is_dir()]
        if subdirs:
            print(f"✅ Found {len(subdirs)} domain directories:")
            for subdir in subdirs:
                print(f"   - {subdir.name}")
        else:
            print("⚠️  No domain directories found. Run: ./bin/manage_asm_repos.sh --init")
    else:
        print("⚠️  ASM repositories directory doesn't exist")
        print("   Run: ./bin/manage_asm_repos.sh --init")

def test_knowledge_extractor():
    """Test the knowledge extractor with sample code"""
    print(f"\n🧪 Testing Knowledge Extractor (ASM repository methods)")
    
    try:
        extractor = KnowledgeExtractor()
        
        # Test sample code analysis
        sample_code = """
        def handle_topology_merge(service_data):
            '''Handle topology merge for ASM services'''
            try:
                kafka_client = KafkaClient()
                result = kafka_client.publish_topology_event(service_data)
                return {"status": "success", "result": result}
            except KafkaException as e:
                logger.error(f"Topology merge failed: {e}")
                raise ServiceError("Merge operation failed")
        """
        
        analysis = extractor.extract_from_code_file(sample_code, "topology_service.py")
        print("✅ Code analysis successful:")
        print(f"   - Language: {analysis.get('language', 'unknown')}")
        print(f"   - Functions: {len(analysis.get('functions', []))}")
        print(f"   - Dependencies: {len(analysis.get('dependencies', []))}")
        print(f"   - Services: {analysis.get('services', [])}")
        
    except Exception as e:
        print(f"⚠️  Knowledge extractor test failed: {e}")

def test_asm_scripts():
    """Test if ASM-related scripts exist and are executable"""
    print(f"\n🔧 Checking ASM management scripts")
    
    scripts = [
        "bin/manage_asm_repos.sh",
        "bin/asm_knowledge_extractor.py"
    ]
    
    for script in scripts:
        script_path = Path(script)
        if script_path.exists():
            if os.access(script_path, os.X_OK):
                print(f"✅ {script} exists and is executable")
            else:
                print(f"⚠️  {script} exists but not executable. Run: chmod +x {script}")
        else:
            print(f"❌ {script} not found")

def main():
    print("🚀 ASM Local Repository Integration Test")
    print("=" * 50)
    
    test_asm_directory_structure()
    test_knowledge_extractor()
    test_asm_scripts()
    
    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    print("1. Run: ./bin/manage_asm_repos.sh --init")
    print("2. Clone your ASM repos into data/asm_repositories/")
    print("3. Run: ./bin/asm_knowledge_extractor.py")
    print("4. Start services: ./bin/start_server_mode.sh")
    print("5. Test queries through OpenWebUI")

if __name__ == "__main__":
    main()