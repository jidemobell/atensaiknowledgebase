#!/usr/bin/env python3
"""
Enterprise-Scale Support Case Processing System
Handles thousands of IBM support cases with varying contexts and formats
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time
from dataclasses import dataclass
from collections import defaultdict, Counter

# Add the corebackend to path
sys.path.append('corebackend/implementation/backend')

try:
    from knowledge_extractor import KnowledgeExtractor
    from multi_source_manager import MultiSourceKnowledgeManager
except ImportError:
    print("⚠️  Warning: Backend modules not found. Running in analysis-only mode.")
    KnowledgeExtractor = None
    MultiSourceKnowledgeManager = None

@dataclass
class ProcessingStats:
    """Statistics for batch processing"""
    total_files: int = 0
    processed_successfully: int = 0
    failed_processing: int = 0
    skipped_files: int = 0
    total_size_mb: float = 0.0
    processing_time_seconds: float = 0.0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class EnterpriseCaseProcessor:
    """Enterprise-scale case processing with advanced features"""
    
    def __init__(self, max_workers: int = 4, batch_size: int = 100):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.stats = ProcessingStats()
        
        # Initialize components if available
        self.extractor = KnowledgeExtractor() if KnowledgeExtractor else None
        self.manager = MultiSourceKnowledgeManager() if MultiSourceKnowledgeManager else None
        
        # Setup logging
        self.setup_logging()
        
        # Pattern recognition caches
        self.service_patterns_cache = {}
        self.category_patterns_cache = {}
        self.resolution_patterns_cache = {}
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "case_processing.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def process_cases_directory(self, cases_dir: str, 
                                    output_file: str = None,
                                    filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process thousands of cases with advanced filtering and batching"""
        
        start_time = time.time()
        cases_path = Path(cases_dir)
        
        if not cases_path.exists():
            return {'error': f'Cases directory not found: {cases_dir}'}
        
        self.logger.info(f"🚀 Starting enterprise case processing from: {cases_dir}")
        self.logger.info(f"⚙️  Configuration: max_workers={self.max_workers}, batch_size={self.batch_size}")
        
        # Discover all case files
        case_files = self.discover_case_files(cases_path, filters)
        self.stats.total_files = len(case_files)
        
        if not case_files:
            return {'error': 'No case files found matching criteria'}
        
        self.logger.info(f"📁 Found {len(case_files)} case files to process")
        
        # Calculate total size
        self.stats.total_size_mb = sum(f.stat().st_size for f in case_files) / (1024 * 1024)
        self.logger.info(f"📊 Total data size: {self.stats.total_size_mb:.2f} MB")
        
        # Process in batches
        all_results = []
        processed_cases = []
        
        for i in range(0, len(case_files), self.batch_size):
            batch = case_files[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(case_files) + self.batch_size - 1) // self.batch_size
            
            self.logger.info(f"🔄 Processing batch {batch_num}/{total_batches} ({len(batch)} files)")
            
            batch_results = await self.process_batch(batch, batch_num)
            all_results.extend(batch_results)
            
            # Extract successful cases
            for result in batch_results:
                if 'case' in result and 'error' not in result:
                    processed_cases.append(result['case'])
                    self.stats.processed_successfully += 1
                else:
                    self.stats.failed_processing += 1
                    if 'error' in result:
                        self.stats.errors.append(result['error'])
            
            # Progress update
            progress = (i + len(batch)) / len(case_files) * 100
            self.logger.info(f"📈 Progress: {progress:.1f}% - Success: {self.stats.processed_successfully}, Failed: {self.stats.failed_processing}")
        
        # Final processing time
        self.stats.processing_time_seconds = time.time() - start_time
        
        # Generate comprehensive analysis
        analysis = self.generate_comprehensive_analysis(processed_cases)
        
        # Save results if requested
        if output_file:
            await self.save_processing_results(processed_cases, analysis, output_file)
        
        return {
            'stats': self.stats,
            'analysis': analysis,
            'processed_cases': len(processed_cases),
            'case_sample': processed_cases[:5] if processed_cases else []
        }
    
    def discover_case_files(self, cases_path: Path, filters: Dict[str, Any] = None) -> List[Path]:
        """Discover case files with advanced filtering"""
        case_files = []
        
        # Supported file patterns
        patterns = ['*.json', '*.txt', '*.csv']
        
        for pattern in patterns:
            case_files.extend(cases_path.rglob(pattern))
        
        # Apply filters if provided
        if filters:
            case_files = self.apply_file_filters(case_files, filters)
        
        # Sort by file size (process smaller files first for quick feedback)
        case_files.sort(key=lambda f: f.stat().st_size)
        
        return case_files
    
    def apply_file_filters(self, files: List[Path], filters: Dict[str, Any]) -> List[Path]:
        """Apply various filters to file list"""
        filtered_files = files
        
        # Size filters
        if filters.get('min_size_kb'):
            min_size = filters['min_size_kb'] * 1024
            filtered_files = [f for f in filtered_files if f.stat().st_size >= min_size]
        
        if filters.get('max_size_kb'):
            max_size = filters['max_size_kb'] * 1024
            filtered_files = [f for f in filtered_files if f.stat().st_size <= max_size]
        
        # Date filters
        if filters.get('modified_after'):
            cutoff_time = datetime.fromisoformat(filters['modified_after']).timestamp()
            filtered_files = [f for f in filtered_files if f.stat().st_mtime >= cutoff_time]
        
        # Pattern filters
        if filters.get('filename_contains'):
            pattern = filters['filename_contains'].lower()
            filtered_files = [f for f in filtered_files if pattern in f.name.lower()]
        
        # Limit number of files for testing
        if filters.get('max_files'):
            filtered_files = filtered_files[:filters['max_files']]
        
        return filtered_files
    
    async def process_batch(self, batch_files: List[Path], batch_num: int) -> List[Dict[str, Any]]:
        """Process a batch of case files with parallel processing"""
        
        results = []
        
        # Use ThreadPoolExecutor for I/O bound operations
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all files in the batch
            futures = []
            for file_path in batch_files:
                future = executor.submit(self.process_single_case_file, file_path)
                futures.append((future, file_path))
            
            # Collect results as they complete
            for future, file_path in futures:
                try:
                    result = future.result(timeout=30)  # 30 second timeout per file
                    results.append(result)
                except Exception as e:
                    error_msg = f"Error processing {file_path.name}: {str(e)}"
                    self.logger.error(error_msg)
                    results.append({'error': error_msg, 'file': str(file_path)})
        
        return results
    
    def process_single_case_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single case file with robust error handling"""
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return {'error': f'Empty file: {file_path.name}', 'file': str(file_path)}
            
            # Determine file type and process accordingly
            if file_path.suffix.lower() == '.json':
                return self.process_json_case(content, file_path)
            elif file_path.suffix.lower() in ['.txt', '.csv']:
                return self.process_text_case(content, file_path)
            else:
                return {'error': f'Unsupported file type: {file_path.suffix}', 'file': str(file_path)}
                
        except Exception as e:
            return {'error': f'File processing error: {str(e)}', 'file': str(file_path)}
    
    def process_json_case(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Process JSON case file with fallback mechanisms"""
        
        if not self.extractor:
            return self.analyze_case_without_extractor(content, file_path, 'json')
        
        try:
            # Try primary extraction method
            result = self.extractor.extract_from_support_case_json(content)
            
            if 'error' in result:
                # Try fallback JSON parsing
                return self.fallback_json_processing(content, file_path)
            
            # Add file metadata
            result['source_file'] = str(file_path)
            result['file_size_kb'] = file_path.stat().st_size / 1024
            result['processing_timestamp'] = datetime.now().isoformat()
            
            return {'case': result}
            
        except Exception as e:
            return self.fallback_json_processing(content, file_path, str(e))
    
    def process_text_case(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Process text case file with enhanced parsing"""
        
        if not self.extractor:
            return self.analyze_case_without_extractor(content, file_path, 'text')
        
        try:
            # Use the manual case extraction
            if self.manager:
                result = asyncio.run(self.manager.add_manual_case(content, {'source_file': str(file_path)}))
                return result
            else:
                # Direct extraction
                extracted = self.extractor.extract_from_salesforce_case(content)
                case = {
                    'title': extracted.title,
                    'description': extracted.description,
                    'services': extracted.affected_services,
                    'symptoms': extracted.symptoms,
                    'error_patterns': extracted.error_messages,
                    'severity': extracted.severity,
                    'tags': extracted.tags,
                    'confidence': extracted.confidence,
                    'source_file': str(file_path),
                    'processing_timestamp': datetime.now().isoformat()
                }
                return {'case': case}
                
        except Exception as e:
            return {'error': f'Text processing error: {str(e)}', 'file': str(file_path)}
    
    def fallback_json_processing(self, content: str, file_path: Path, error: str = None) -> Dict[str, Any]:
        """Fallback JSON processing for malformed or unusual structures"""
        
        try:
            # Try to parse JSON manually
            case_data = json.loads(content)
            
            # Extract basic information with flexible field mapping
            case_info = {
                'case_number': self.find_field_value(case_data, ['case_number', 'caseNumber', 'id', 'case_id']),
                'title': self.find_field_value(case_data, ['subject', 'title', 'summary']),
                'description': self.find_field_value(case_data, ['problem_description', 'description', 'issue']),
                'source_file': str(file_path),
                'raw_structure': self.analyze_json_structure(case_data),
                'confidence': 0.3,  # Low confidence for fallback processing
                'processing_method': 'fallback',
                'original_error': error
            }
            
            return {'case': case_info}
            
        except json.JSONDecodeError:
            return {'error': f'Invalid JSON format in {file_path.name}', 'file': str(file_path)}
    
    def analyze_case_without_extractor(self, content: str, file_path: Path, file_type: str) -> Dict[str, Any]:
        """Analyze case content without the full extractor (lightweight mode)"""
        
        # Basic text analysis
        words = content.lower().split()
        word_count = len(words)
        
        # Look for key indicators
        services = []
        if 'topology' in content.lower():
            services.append('topology')
        if 'kafka' in content.lower():
            services.append('kafka')
        if 'kubernetes' in content.lower() or 'k8s' in content.lower():
            services.append('kubernetes')
        
        # Extract case number if possible
        import re
        case_number_match = re.search(r'(?:case|ts|ticket)[-_]?(\w+)', content.lower())
        case_number = case_number_match.group(1) if case_number_match else 'unknown'
        
        case_info = {
            'case_number': case_number,
            'title': f'Case from {file_path.name}',
            'word_count': word_count,
            'services': services,
            'source_file': str(file_path),
            'file_type': file_type,
            'confidence': 0.2,
            'processing_method': 'lightweight',
            'content_preview': content[:200] + '...' if len(content) > 200 else content
        }
        
        return {'case': case_info}
    
    def find_field_value(self, data: Dict, field_names: List[str]) -> str:
        """Find value from multiple possible field names"""
        for field in field_names:
            if field in data and data[field]:
                return str(data[field])
        return ''
    
    def analyze_json_structure(self, data: Dict) -> Dict[str, Any]:
        """Analyze JSON structure for debugging"""
        return {
            'top_level_keys': list(data.keys()),
            'total_keys': len(data),
            'has_comments': 'comments' in data or 'public_comments' in data,
            'has_text_content': any('text' in str(v).lower() or 'description' in str(v).lower() 
                                  for v in data.values() if isinstance(v, str))
        }
    
    def generate_comprehensive_analysis(self, processed_cases: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive analysis of all processed cases"""
        
        if not processed_cases:
            return {'error': 'No cases to analyze'}
        
        analysis = {
            'total_cases': len(processed_cases),
            'processing_stats': {
                'average_confidence': sum(case.get('confidence', 0) for case in processed_cases) / len(processed_cases),
                'high_confidence_cases': len([c for c in processed_cases if c.get('confidence', 0) > 0.7]),
                'low_confidence_cases': len([c for c in processed_cases if c.get('confidence', 0) < 0.3])
            }
        }
        
        # Service analysis
        all_services = []
        for case in processed_cases:
            services = case.get('services', []) or case.get('affected_services', [])
            all_services.extend(services)
        
        service_counter = Counter(all_services)
        analysis['service_analysis'] = {
            'total_services_mentioned': len(all_services),
            'unique_services': len(service_counter),
            'top_services': service_counter.most_common(10)
        }
        
        # Category analysis
        categories = [case.get('case_category', case.get('category', 'unknown')) for case in processed_cases]
        category_counter = Counter(categories)
        analysis['category_analysis'] = {
            'categories_distribution': dict(category_counter),
            'most_common_category': category_counter.most_common(1)[0] if category_counter else None
        }
        
        # Severity analysis
        severities = [case.get('severity', 'Unknown') for case in processed_cases]
        severity_counter = Counter(severities)
        analysis['severity_analysis'] = dict(severity_counter)
        
        # Quality analysis
        text_qualities = [case.get('text_quality_score', 0) for case in processed_cases if 'text_quality_score' in case]
        if text_qualities:
            analysis['quality_analysis'] = {
                'average_text_quality': sum(text_qualities) / len(text_qualities),
                'high_quality_cases': len([q for q in text_qualities if q > 0.7])
            }
        
        # Timeline analysis
        processing_methods = [case.get('processing_method', 'standard') for case in processed_cases]
        method_counter = Counter(processing_methods)
        analysis['processing_analysis'] = dict(method_counter)
        
        return analysis
    
    async def save_processing_results(self, processed_cases: List[Dict], 
                                    analysis: Dict[str, Any], output_file: str):
        """Save comprehensive processing results"""
        
        results = {
            'metadata': {
                'processing_timestamp': datetime.now().isoformat(),
                'total_cases_processed': len(processed_cases),
                'processing_stats': self.stats.__dict__,
                'analysis_summary': analysis
            },
            'cases': processed_cases
        }
        
        # Save main results
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save analysis summary
        analysis_file = output_file.replace('.json', '_analysis.json')
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        # Save error log if there are errors
        if self.stats.errors:
            error_file = output_file.replace('.json', '_errors.txt')
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"Processing Errors ({len(self.stats.errors)} total):\n\n")
                for i, error in enumerate(self.stats.errors, 1):
                    f.write(f"{i}. {error}\n")
        
        self.logger.info(f"💾 Results saved to:")
        self.logger.info(f"  • Main results: {output_file}")
        self.logger.info(f"  • Analysis: {analysis_file}")
        if self.stats.errors:
            self.logger.info(f"  • Errors: {error_file}")

async def main():
    """Main function for enterprise case processing"""
    
    print("🏢 IBM Enterprise Support Case Processing System")
    print("="*60)
    
    # Configuration
    cases_dir = "data/support_cases"
    max_workers = 8  # Adjust based on your system
    batch_size = 50  # Process 50 files at a time
    
    # Check for custom directory
    if len(sys.argv) > 1:
        cases_dir = sys.argv[1]
    
    # Initialize processor
    processor = EnterpriseCaseProcessor(max_workers=max_workers, batch_size=batch_size)
    
    # Optional filters for large datasets
    filters = {
        'max_files': 1000,  # Limit for testing - remove for full processing
        # 'min_size_kb': 1,   # Skip very small files
        # 'max_size_kb': 1024,  # Skip very large files
        # 'filename_contains': 'case'  # Only process files with 'case' in name
    }
    
    # Process cases
    results = await processor.process_cases_directory(
        cases_dir=cases_dir,
        output_file="enterprise_knowledge_base.json",
        filters=filters
    )
    
    # Display results
    if 'error' in results:
        print(f"❌ Processing failed: {results['error']}")
        return
    
    stats = results['stats']
    analysis = results['analysis']
    
    print(f"\n📊 Processing Complete!")
    print(f"  • Files processed: {stats.processed_successfully}/{stats.total_files}")
    print(f"  • Success rate: {(stats.processed_successfully/stats.total_files*100):.1f}%")
    print(f"  • Processing time: {stats.processing_time_seconds:.1f} seconds")
    print(f"  • Throughput: {stats.total_size_mb/stats.processing_time_seconds:.2f} MB/s")
    
    if 'error' not in analysis:
        print(f"\n🔍 Analysis Summary:")
        print(f"  • Average confidence: {analysis['processing_stats']['average_confidence']:.2f}")
        print(f"  • High confidence cases: {analysis['processing_stats']['high_confidence_cases']}")
        print(f"  • Top services: {', '.join([s[0] for s in analysis['service_analysis']['top_services'][:5]])}")
    
    if stats.errors:
        print(f"\n⚠️  Errors encountered: {len(stats.errors)}")
        print("  Check the error log for details")
    
    print(f"\n✅ Enterprise knowledge base ready for deployment!")
    print(f"  • Main file: enterprise_knowledge_base.json")
    print(f"  • Analysis: enterprise_knowledge_base_analysis.json")

if __name__ == "__main__":
    asyncio.run(main())