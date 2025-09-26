#!/usr/bin/env python3
"""
Support Case Processing Script
Processes IBM support case JSON files and integrates them into the Knowledge Fusion Platform
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add the corebackend to path
sys.path.append('corebackend/implementation/backend')

from multi_source_manager import MultiSourceKnowledgeManager

class SupportCaseProcessor:
    """Processes support case files and integrates them into the knowledge base"""
    
    def __init__(self):
        self.manager = MultiSourceKnowledgeManager()
        self.processed_cases = []
        
    async def process_case_directory(self, cases_dir: str = "data/support_cases"):
        """Process all support case files in a directory"""
        print(f"🔍 Processing support cases from: {cases_dir}")
        
        # Load all support cases
        results = await self.manager.load_support_cases_directory(cases_dir)
        
        if 'error' in results:
            print(f"❌ Error: {results['error']}")
            return results
        
        # Display results
        print(f"📊 Processing Results:")
        print(f"  • Cases processed: {results['cases_processed']}")
        print(f"  • JSON files found: {results['json_files_found']}")
        print(f"  • Text files found: {results['text_files_found']}")
        
        if results['errors']:
            print(f"  • Errors: {len(results['errors'])}")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"    - {error}")
        
        if results['case_numbers']:
            print(f"  • Case numbers processed: {', '.join(results['case_numbers'][:10])}")
            if len(results['case_numbers']) > 10:
                print(f"    ...and {len(results['case_numbers']) - 10} more")
        
        return results
    
    async def process_single_case(self, case_file: str):
        """Process a single support case file"""
        file_path = Path(case_file)
        
        if not file_path.exists():
            print(f"❌ File not found: {case_file}")
            return None
        
        print(f"📄 Processing case file: {file_path.name}")
        
        try:
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_content = f.read()
                
                result = await self.manager.add_support_case_json(json_content, str(file_path))
                
                if 'error' in result:
                    print(f"❌ Error processing JSON: {result['error']}")
                    return None
                
                case = result['case']
                print(f"✅ Successfully processed case: {case['case_number']}")
                print(f"  • Subject: {case['title']}")
                print(f"  • Services: {', '.join(case['services'][:5])}")
                print(f"  • Resolution patterns: {', '.join(case['resolution_patterns'][:3])}")
                print(f"  • Confidence: {case['confidence']:.2f}")
                print(f"  • Tags: {len(case['tags'])} tags")
                
                if case['hotfix_info']['images']:
                    print(f"  • Hotfix images: {len(case['hotfix_info']['images'])}")
                
                if result['similar_cases']:
                    print(f"  • Similar cases found: {len(result['similar_cases'])}")
                
                return result
            
            elif file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                
                result = await self.manager.add_manual_case(text_content, {'source_file': str(file_path)})
                
                case = result['case']
                print(f"✅ Successfully processed text case: {case['title']}")
                print(f"  • Services: {', '.join(case['affected_services'][:5])}")
                print(f"  • Severity: {case['severity']}")
                print(f"  • Confidence: {case['confidence']:.2f}")
                
                return result
            
            else:
                print(f"❌ Unsupported file format: {file_path.suffix}")
                return None
                
        except Exception as e:
            print(f"❌ Error processing file: {str(e)}")
            return None
    
    def save_knowledge_base(self, output_file: str = "knowledge_base_with_cases.json"):
        """Save the complete knowledge base to a file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.manager.knowledge_store, f, indent=2, default=str)
            
            print(f"💾 Knowledge base saved to: {output_file}")
            print(f"  • Total cases: {len(self.manager.knowledge_store['cases'])}")
            print(f"  • Total code entries: {len(self.manager.knowledge_store.get('code', []))}")
            print(f"  • Total documentation: {len(self.manager.knowledge_store.get('documentation', []))}")
            print(f"  • ASM repositories: {len(self.manager.knowledge_store.get('asm_repositories', []))}")
            
        except Exception as e:
            print(f"❌ Error saving knowledge base: {str(e)}")
    
    async def analyze_case_patterns(self):
        """Analyze patterns across all processed cases"""
        cases = self.manager.knowledge_store['cases']
        
        if not cases:
            print("📊 No cases to analyze")
            return
        
        print(f"📊 Case Analysis Report ({len(cases)} cases):")
        
        # Analyze services
        all_services = []
        for case in cases:
            all_services.extend(case.get('services', []) or case.get('affected_services', []))
        
        service_counts = {}
        for service in all_services:
            service_counts[service] = service_counts.get(service, 0) + 1
        
        print(f"  • Top services mentioned:")
        for service, count in sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"    - {service}: {count} cases")
        
        # Analyze resolution patterns
        all_patterns = []
        for case in cases:
            all_patterns.extend(case.get('resolution_patterns', []))
        
        pattern_counts = {}
        for pattern in all_patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        print(f"  • Top resolution patterns:")
        for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"    - {pattern}: {count} cases")
        
        # Analyze confidence scores
        confidences = [case.get('confidence', 0) for case in cases]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        print(f"  • Average confidence score: {avg_confidence:.2f}")

async def main():
    """Main function to process support cases"""
    processor = SupportCaseProcessor()
    
    print("🚀 IBM Support Case Knowledge Processor")
    print("="*50)
    
    # Check if there are command line arguments
    if len(sys.argv) > 1:
        # Process specific file
        case_file = sys.argv[1]
        await processor.process_single_case(case_file)
    else:
        # Process entire directory
        await processor.process_case_directory()
    
    # Analyze patterns
    print("\n" + "="*50)
    await processor.analyze_case_patterns()
    
    # Save knowledge base
    print("\n" + "="*50)
    processor.save_knowledge_base()
    
    print("\n✅ Processing complete!")
    print("\n💡 Usage examples:")
    print("  • Process all cases: python process_support_cases.py")
    print("  • Process single case: python process_support_cases.py data/support_cases/case_TS019888217.json")
    print("  • Check knowledge_base_with_cases.json for the complete knowledge base")

if __name__ == "__main__":
    asyncio.run(main())