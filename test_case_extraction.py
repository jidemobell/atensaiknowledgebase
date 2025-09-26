#!/usr/bin/env python3
"""
Simple Support Case Tester
Test the support case extraction functionality with your sample case
"""

import json
import sys
import os
from pathlib import Path

# Add the corebackend to path
sys.path.insert(0, 'corebackend/implementation/backend')

def test_case_extraction():
    """Test the support case extraction with sample data"""
    print("🧪 Testing Support Case Extraction")
    print("="*50)
    
    try:
        from knowledge_extractor import KnowledgeExtractor
        
        # Initialize extractor
        extractor = KnowledgeExtractor()
        
        # Load sample case
        case_file = "data/support_cases/case_TS019888217.json"
        
        if not os.path.exists(case_file):
            print(f"❌ Sample case file not found: {case_file}")
            return False
        
        print(f"📄 Loading case file: {case_file}")
        
        with open(case_file, 'r', encoding='utf-8') as f:
            case_content = f.read()
        
        # Extract knowledge
        print("🔍 Extracting knowledge from support case...")
        extracted = extractor.extract_from_support_case_json(case_content)
        
        if 'error' in extracted:
            print(f"❌ Extraction failed: {extracted['error']}")
            return False
        
        # Display results
        print("✅ Extraction successful!")
        print(f"\n📊 Extracted Information:")
        print(f"  • Case Number: {extracted['case_number']}")
        print(f"  • Subject: {extracted['subject']}")
        print(f"  • Confidence: {extracted['confidence']:.2f}")
        print(f"  • Knowledge Type: {extracted['knowledge_type']}")
        
        print(f"\n🔧 Services Detected:")
        for service in extracted['services'][:10]:
            print(f"  • {service}")
        
        print(f"\n🛠️ Resolution Patterns:")
        for pattern in extracted['resolution_patterns']:
            print(f"  • {pattern}")
        
        print(f"\n🏷️ Tags Generated:")
        for tag in extracted['tags'][:15]:
            print(f"  • {tag}")
        
        print(f"\n💉 Hotfix Information:")
        hotfix = extracted['hotfix_info']
        print(f"  • Images: {len(hotfix['images'])}")
        print(f"  • Digests: {len(hotfix['digests'])}")
        print(f"  • Tags: {len(hotfix['tags'])}")
        print(f"  • Procedures: {len(hotfix['procedures'])}")
        
        if hotfix['images']:
            print(f"  • Sample image: {hotfix['images'][0]}")
        
        if hotfix['digests']:
            print(f"  • Sample digest: sha256:{hotfix['digests'][0][:16]}...")
        
        print(f"\n⚡ Command Patterns:")
        for cmd in extracted['command_patterns'][:5]:
            print(f"  • {cmd[:80]}...")
        
        print(f"\n🚨 Error Patterns:")
        for error in extracted['error_patterns'][:5]:
            print(f"  • {error}")
        
        print(f"\n🎯 Symptoms:")
        for symptom in extracted['symptoms'][:5]:
            print(f"  • {symptom}")
        
        # Save detailed extraction for review
        output_file = "case_extraction_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted, f, indent=2, default=str)
        
        print(f"\n💾 Detailed extraction saved to: {output_file}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running from the TOPOLOGYKNOWLEDGE directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_multiple_cases():
    """Test processing multiple case files if they exist"""
    print("\n🧪 Testing Multiple Case Processing")
    print("="*50)
    
    cases_dir = Path("data/support_cases")
    json_files = list(cases_dir.glob("*.json"))
    
    print(f"📁 Found {len(json_files)} JSON case files")
    
    if not json_files:
        print("💡 Add more .json case files to data/support_cases/ to test batch processing")
        return
    
    try:
        from knowledge_extractor import KnowledgeExtractor
        extractor = KnowledgeExtractor()
        
        successful = 0
        failed = 0
        
        for json_file in json_files[:5]:  # Test first 5 files
            print(f"\n📄 Processing: {json_file.name}")
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                result = extractor.extract_from_support_case_json(content)
                
                if 'error' in result:
                    print(f"  ❌ Failed: {result['error']}")
                    failed += 1
                else:
                    print(f"  ✅ Success: Case {result['case_number']}, Confidence: {result['confidence']:.2f}")
                    successful += 1
                    
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                failed += 1
        
        print(f"\n📊 Batch Processing Results:")
        print(f"  • Successful: {successful}")
        print(f"  • Failed: {failed}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")

if __name__ == "__main__":
    print("🚀 IBM Support Case Knowledge Extraction Test")
    print("="*60)
    
    # Test single case extraction
    success = test_case_extraction()
    
    if success:
        # Test multiple cases if available
        test_multiple_cases()
        
        print("\n" + "="*60)
        print("✅ Testing complete!")
        print("\n💡 Next steps:")
        print("  1. Copy your extracted case JSON files to data/support_cases/")
        print("  2. Run: python process_support_cases.py")
        print("  3. Review the generated knowledge_base_with_cases.json")
        print("  4. Use the knowledge base with your Core Backend for intelligent queries")
    else:
        print("\n❌ Testing failed. Please check the setup and try again.")