"""
Document Processor for IBM AIOps Knowledge System
Handles Salesforce cases, documentation, and other text sources
"""

import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import tiktoken

# Try to import optional dependencies
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

class DocumentProcessor:
    def __init__(self):
        if EMBEDDINGS_AVAILABLE:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.embedder = None
            
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def process_salesforce_case(self, case_text: str, case_id: str) -> Dict[str, Any]:
        """Process a Salesforce case export"""
        # Extract metadata
        metadata = self._extract_case_metadata(case_text)
        
        # Detect affected services
        services = self._detect_services(case_text)
        
        # Split into chunks
        chunks = self._intelligent_chunk(case_text, case_id)
        
        # Generate embeddings if available
        if self.embedder:
            embeddings = self.embedder.encode([chunk['text'] for chunk in chunks])
            
            # Enhance chunks with embeddings and metadata
            for i, chunk in enumerate(chunks):
                chunk.update({
                    'case_id': case_id,
                    'embedding': embeddings[i].tolist(),
                    'services': services,
                    'source_type': 'salesforce_case',
                    'confidence': metadata.get('confidence', 0.5)
                })
        else:
            # No embeddings available
            for chunk in chunks:
                chunk.update({
                    'case_id': case_id,
                    'embedding': None,
                    'services': services,
                    'source_type': 'salesforce_case',
                    'confidence': metadata.get('confidence', 0.5)
                })
        
        return {
            'case_id': case_id,
            'chunks': chunks,
            'metadata': metadata,
            'services': services,
            'processed_at': datetime.now().isoformat()
        }
    
    def _extract_case_metadata(self, text: str) -> Dict[str, Any]:
        """Extract structured metadata from case text"""
        metadata = {}
        
        # Look for common patterns
        priority_match = re.search(r'Priority:\s*(\w+)', text, re.IGNORECASE)
        if priority_match:
            metadata['priority'] = priority_match.group(1).lower()
        
        severity_match = re.search(r'Severity:\s*(\w+)', text, re.IGNORECASE)
        if severity_match:
            metadata['severity'] = severity_match.group(1).lower()
        
        version_match = re.search(r'Version:\s*([\d\.]+)', text, re.IGNORECASE)
        if version_match:
            metadata['version'] = version_match.group(1)
        
        environment_patterns = ['production', 'staging', 'development', 'prod', 'dev', 'test']
        for env in environment_patterns:
            if env.lower() in text.lower():
                metadata['environment'] = env.lower()
                break
        
        # Extract resolution status
        resolution_keywords = ['resolved', 'closed', 'fixed', 'solution', 'workaround']
        if any(keyword in text.lower() for keyword in resolution_keywords):
            metadata['resolution_status'] = 'resolved'
            metadata['confidence'] = 0.9
        else:
            metadata['resolution_status'] = 'open'
            metadata['confidence'] = 0.3
        
        return metadata
    
    def _detect_services(self, text: str) -> List[str]:
        """Enhanced service detection for IBM AIOps"""
        text_lower = text.lower()
        services = []
        
        # Service patterns - both exact names and variations
        service_patterns = {
            'topology-merge': [
                'topology-merge', 'topology merge', 'merge service',
                'topo-merge', 'topo merge'
            ],
            'topology-inventory': [
                'topology-inventory', 'inventory service', 'topology inventory',
                'topo-inventory', 'topo inventory'
            ],
            'topology-status': [
                'topology-status', 'status service', 'topology status',
                'topo-status', 'topo status'
            ],
            'observer-core': [
                'observer-core', 'observer core', 'core observer'
            ],
            'kubernetes-observer': [
                'kubernetes-observer', 'k8s observer', 'kubernetes observer',
                'kube-observer', 'k8s-observer'
            ],
            'servicenow-observer': [
                'servicenow-observer', 'snow observer', 'servicenow',
                'service-now-observer'
            ],
            'file-observer': [
                'file-observer', 'file observer'
            ],
            'rest-observer': [
                'rest-observer', 'rest observer'
            ],
            'kafka': [
                'kafka', 'message queue', 'streaming', 'consumer lag',
                'kafka cluster', 'kafka consumer', 'kafka producer'
            ],
            'cassandra': [
                'cassandra', 'database', 'cql', 'keyspace',
                'cassandra cluster', 'cassandra node'
            ],
            'postgres': [
                'postgres', 'postgresql', 'pg_', 'postgres database'
            ],
            'redis': [
                'redis', 'cache', 'caching', 'redis cluster'
            ],
            'elasticsearch': [
                'elasticsearch', 'elastic', 'es cluster'
            ],
            'ingress': [
                'ingress', 'nginx', 'haproxy', 'load balancer'
            ],
            'etcd': [
                'etcd', 'etcd cluster'
            ]
        }
        
        for service, patterns in service_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                services.append(service)
        
        return list(set(services))  # Remove duplicates
    
    def _intelligent_chunk(self, text: str, case_id: str) -> List[Dict[str, Any]]:
        """Create intelligent chunks based on content structure"""
        # Split by common delimiters in Salesforce cases
        sections = self._split_by_sections(text)
        
        chunks = []
        for i, section in enumerate(sections):
            if len(section.strip()) < 50:  # Skip very short sections
                continue
            
            # Determine chunk type
            chunk_type = self._classify_chunk(section)
            
            chunks.append({
                'text': section.strip(),
                'chunk_id': f"{case_id}_{i}",
                'chunk_type': chunk_type,
                'position': i,
                'token_count': len(self.tokenizer.encode(section)),
                'hash': hashlib.md5(section.encode()).hexdigest()
            })
        
        return chunks
    
    def _split_by_sections(self, text: str) -> List[str]:
        """Split text by logical sections"""
        # Common Salesforce case section markers
        section_markers = [
            'Problem Description:',
            'Steps to Reproduce:',
            'Expected Behavior:',
            'Actual Behavior:',
            'Resolution:',
            'Root Cause:',
            'Workaround:',
            'Additional Information:',
            'Log Analysis:',
            'From:',  # Email headers
            'Subject:',
            '---',  # Common separators
            'Customer Update:',
            'Internal Update:',
            'Case Description:',
            'Issue Summary:',
            'Technical Details:',
            'Environment Details:',
            'Error Details:',
            'Solution:',
            'Next Steps:'
        ]
        
        # Start with full text
        sections = [text]
        
        # Split by each marker
        for marker in section_markers:
            new_sections = []
            for section in sections:
                if marker in section:
                    parts = section.split(marker)
                    new_sections.extend(parts)
                else:
                    new_sections.append(section)
            sections = new_sections
        
        # Filter out very short sections
        return [s.strip() for s in sections if len(s.strip()) > 50]
    
    def _classify_chunk(self, text: str) -> str:
        """Classify chunk type for better retrieval"""
        text_lower = text.lower()
        
        # Error/problem patterns
        error_keywords = ['error', 'exception', 'failed', 'timeout', 'crash', 'down', 'unavailable']
        if any(word in text_lower for word in error_keywords):
            return 'error_description'
        
        # Resolution patterns
        resolution_keywords = ['resolution', 'solution', 'fix', 'resolved', 'workaround', 'solved']
        if any(word in text_lower for word in resolution_keywords):
            return 'resolution'
        
        # Steps/procedure patterns
        steps_keywords = ['steps', 'reproduce', 'procedure', 'instructions', 'how to']
        if any(word in text_lower for word in steps_keywords):
            return 'reproduction_steps'
        
        # Log analysis patterns
        log_keywords = ['log', 'trace', 'stack', 'debug', 'warning', 'info']
        if any(word in text_lower for word in log_keywords):
            return 'log_analysis'
        
        # Configuration patterns
        config_keywords = ['config', 'configuration', 'setting', 'parameter', 'property']
        if any(word in text_lower for word in config_keywords):
            return 'configuration'
        
        # Environment patterns
        env_keywords = ['environment', 'deployment', 'cluster', 'node', 'pod']
        if any(word in text_lower for word in env_keywords):
            return 'environment_info'
        
        return 'general'

    def process_text_document(self, text: str, doc_id: str, doc_type: str = 'general') -> Dict[str, Any]:
        """Process any text document (not just Salesforce cases)"""
        
        # Basic metadata
        metadata = {
            'doc_type': doc_type,
            'processed_at': datetime.now().isoformat(),
            'word_count': len(text.split()),
            'char_count': len(text)
        }
        
        # Detect services regardless of document type
        services = self._detect_services(text)
        
        # Simple chunking for non-case documents
        chunks = self._simple_chunk(text, doc_id, doc_type)
        
        # Generate embeddings if available
        if self.embedder and chunks:
            embeddings = self.embedder.encode([chunk['text'] for chunk in chunks])
            
            for i, chunk in enumerate(chunks):
                chunk.update({
                    'doc_id': doc_id,
                    'embedding': embeddings[i].tolist(),
                    'services': services,
                    'source_type': doc_type
                })
        else:
            for chunk in chunks:
                chunk.update({
                    'doc_id': doc_id,
                    'embedding': None,
                    'services': services,
                    'source_type': doc_type
                })
        
        return {
            'doc_id': doc_id,
            'chunks': chunks,
            'metadata': metadata,
            'services': services
        }
    
    def _simple_chunk(self, text: str, doc_id: str, chunk_size: int = 1000) -> List[Dict[str, Any]]:
        """Simple chunking for general documents"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if len(chunk_text.strip()) < 50:  # Skip very short chunks
                continue
            
            chunks.append({
                'text': chunk_text.strip(),
                'chunk_id': f"{doc_id}_chunk_{i // chunk_size}",
                'chunk_type': 'general',
                'position': i // chunk_size,
                'token_count': len(self.tokenizer.encode(chunk_text)),
                'hash': hashlib.md5(chunk_text.encode()).hexdigest()
            })
        
        return chunks
