import re
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from models import ExtractedKnowledge, KnowledgeSourceType

class KnowledgeExtractor:
    """Extracts structured information from raw text content"""
    
    def __init__(self):
        # Service patterns for auto-detection
        self.service_patterns = {
            'topology-merge': r'topology[-_]?merge|topology merge',
            'kafka': r'\bkafka\b',
            'cassandra': r'\bcassandra\b',
            'elasticsearch': r'elasticsearch|elastic search',
            'redis': r'\bredis\b',
            'mongodb': r'mongodb|mongo db',
            'kubernetes': r'kubernetes|k8s',
            'docker': r'\bdocker\b',
            'nginx': r'\bnginx\b',
            'apache': r'\bapache\b'
        }
        
        # Error pattern recognition
        self.error_patterns = {
            'timeout': r'timeout|timed out|time out',
            'connection_refused': r'connection refused|connection denied',
            'out_of_memory': r'out of memory|oom|memory exceeded',
            'disk_space': r'disk space|no space left|disk full',
            'permission_denied': r'permission denied|access denied|forbidden',
            'network_error': r'network error|network unreachable|dns',
            'ssl_error': r'ssl|certificate|handshake failed'
        }
        
        # Severity indicators
        self.severity_patterns = {
            'Critical': r'critical|sev[- ]?1|priority[- ]?1|urgent|emergency',
            'High': r'high|sev[- ]?2|priority[- ]?2|important',
            'Medium': r'medium|sev[- ]?3|priority[- ]?3|normal',
            'Low': r'low|sev[- ]?4|priority[- ]?4|minor'
        }

    def extract_from_salesforce_case(self, raw_content: str) -> ExtractedKnowledge:
        """Extract knowledge from Salesforce case content"""
        
        # Clean and normalize content
        content = self._clean_content(raw_content)
        
        # Extract title (usually first line or case subject)
        title = self._extract_title(content)
        
        # Extract description
        description = self._extract_description(content)
        
        # Detect affected services
        affected_services = self._detect_services(content)
        
        # Extract symptoms and error messages
        symptoms = self._extract_symptoms(content)
        error_messages = self._extract_error_messages(content)
        
        # Determine severity
        severity = self._detect_severity(content)
        
        # Generate tags
        tags = self._generate_tags(content, affected_services, symptoms)
        
        # Calculate confidence based on extraction quality
        confidence = self._calculate_extraction_confidence(
            title, description, affected_services, symptoms
        )
        
        return ExtractedKnowledge(
            title=title,
            description=description,
            affected_services=affected_services,
            symptoms=symptoms,
            error_messages=error_messages,
            severity=severity,
            tags=tags,
            confidence=confidence,
            suggested_case_type="incident"
        )

    def extract_from_asm_repository(self, repo_path: str, domain: str = None) -> Dict[str, Any]:
        """Extract knowledge from local ASM repository"""
        import os
        from pathlib import Path
        
        repo_path = Path(repo_path)
        if not repo_path.exists():
            return {'error': f'Repository path does not exist: {repo_path}'}
        
        extracted_data = {
            'repository_path': str(repo_path),
            'domain': domain or 'general',
            'files_analyzed': 0,
            'languages': [],
            'functions': [],
            'error_patterns': [],
            'config_references': [],
            'dependencies': [],
            'services': [],
            'patterns': {}
        }
        
        # Analyze all relevant files in the repository
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and self._is_analyzable_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Extract knowledge from file content
                    file_analysis = self.extract_from_code_file(content, str(file_path.relative_to(repo_path)))
                    
                    # Merge results
                    extracted_data['files_analyzed'] += 1
                    if file_analysis.get('language') and file_analysis['language'] not in extracted_data['languages']:
                        extracted_data['languages'].append(file_analysis['language'])
                    
                    extracted_data['functions'].extend(file_analysis.get('functions', []))
                    extracted_data['error_patterns'].extend(file_analysis.get('error_patterns', []))
                    extracted_data['config_references'].extend(file_analysis.get('config_references', []))
                    extracted_data['dependencies'].extend(file_analysis.get('dependencies', []))
                    extracted_data['services'].extend(file_analysis.get('services', []))
                    
                except Exception as e:
                    logging.warning(f"Error analyzing file {file_path}: {e}")
        
        # Detect ASM-specific patterns based on domain
        extracted_data['patterns'] = self._detect_asm_patterns(extracted_data, domain)
        
        return extracted_data
    
    def extract_from_code_file(self, code_content: str, file_path: str) -> Dict[str, Any]:
        """Extract knowledge from code file content (renamed from extract_from_github_code)"""
        
        # Detect programming language
        language = self._detect_language(file_path)
        
        # Extract function/method names
        functions = self._extract_functions(code_content, language)
        
        # Detect error handling patterns
        error_patterns = self._detect_error_handling(code_content, language)
        
        # Extract configuration references
        config_refs = self._extract_config_references(code_content)
        
        # Detect service dependencies
        dependencies = self._detect_dependencies(code_content, language)
        
        return {
            'language': language,
            'functions': functions,
            'error_patterns': error_patterns,
            'config_references': config_refs,
            'dependencies': dependencies,
            'services': self._detect_services(code_content)
        }

    def extract_from_documentation(self, doc_content: str, source_url: str = None) -> Dict[str, Any]:
        """Extract knowledge from documentation"""
        
        # Extract headings and structure
        headings = self._extract_headings(doc_content)
        
        # Extract code blocks
        code_blocks = self._extract_code_blocks(doc_content)
        
        # Extract links and references
        links = self._extract_links(doc_content)
        
        # Detect document type (runbook, API doc, etc.)
        doc_type = self._classify_document_type(doc_content, source_url)
        
        # Extract related services
        services = self._detect_services(doc_content)
        
        return {
            'headings': headings,
            'code_blocks': code_blocks,
            'links': links,
            'doc_type': doc_type,
            'services': services,
            'tags': self._generate_doc_tags(doc_content, doc_type)
        }

    def _clean_content(self, content: str) -> str:
        """Clean and normalize content"""
        # Remove extra whitespace and normalize line endings
        content = re.sub(r'\s+', ' ', content.strip())
        content = re.sub(r'\n\s*\n', '\n\n', content)
        return content

    def _extract_title(self, content: str) -> str:
        """Extract title from content"""
        lines = content.split('\n')
        
        # Look for patterns that indicate a title
        title_patterns = [
            r'^Subject:\s*(.+)',
            r'^Title:\s*(.+)',
            r'^Case:\s*(.+)',
            r'^Issue:\s*(.+)'
        ]
        
        for line in lines[:5]:  # Check first 5 lines
            for pattern in title_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        # Fallback: use first meaningful line
        for line in lines:
            if len(line.strip()) > 10 and not line.strip().startswith(('From:', 'To:', 'Date:')):
                return line.strip()[:100]
        
        return "Extracted Case"

    def _extract_description(self, content: str) -> str:
        """Extract description from content"""
        # Remove email headers and metadata
        lines = content.split('\n')
        description_lines = []
        skip_headers = True
        
        for line in lines:
            # Skip email headers
            if skip_headers and re.match(r'^(From|To|Date|Subject|CC):', line):
                continue
            skip_headers = False
            
            # Add meaningful lines
            if line.strip() and not re.match(r'^[-=]{3,}', line):
                description_lines.append(line.strip())
        
        description = ' '.join(description_lines)
        return description[:1000] if description else "No description available"

    def _detect_services(self, content: str) -> List[str]:
        """Detect affected services from content"""
        detected_services = []
        content_lower = content.lower()
        
        for service, pattern in self.service_patterns.items():
            if re.search(pattern, content_lower, re.IGNORECASE):
                detected_services.append(service)
        
        return list(set(detected_services))

    def _extract_symptoms(self, content: str) -> List[str]:
        """Extract symptoms from content"""
        symptoms = []
        content_lower = content.lower()
        
        for symptom, pattern in self.error_patterns.items():
            if re.search(pattern, content_lower, re.IGNORECASE):
                symptoms.append(symptom.replace('_', ' ').title())
        
        # Look for common symptom phrases
        symptom_phrases = [
            r'service (?:is )?(?:down|unavailable|not responding)',
            r'application (?:is )?(?:slow|hanging|freezing)',
            r'users (?:are )?(?:unable to|cannot) (?:access|login|connect)',
            r'(?:high|excessive) (?:cpu|memory|disk) usage',
            r'(?:slow|poor) performance',
            r'intermittent (?:issues|problems|failures)'
        ]
        
        for pattern in symptom_phrases:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            symptoms.extend([match if isinstance(match, str) else ' '.join(match) for match in matches])
        
        return list(set(symptoms))

    def _extract_error_messages(self, content: str) -> List[str]:
        """Extract error messages from content"""
        error_messages = []
        
        # Look for quoted error messages
        quoted_errors = re.findall(r'"([^"]*(?:error|exception|failed|fault)[^"]*)"', content, re.IGNORECASE)
        error_messages.extend(quoted_errors)
        
        # Look for log-style errors
        log_errors = re.findall(r'ERROR:?\s*(.+)', content, re.IGNORECASE)
        error_messages.extend(log_errors)
        
        # Look for exception patterns
        exception_patterns = [
            r'(\w+Exception: .+)',
            r'(Error: .+)',
            r'(Failed to .+)',
            r'(Cannot .+)'
        ]
        
        for pattern in exception_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            error_messages.extend(matches)
        
        return list(set(error_messages[:10]))  # Limit to 10 error messages

    def _detect_severity(self, content: str) -> str:
        """Detect severity from content"""
        content_lower = content.lower()
        
        for severity, pattern in self.severity_patterns.items():
            if re.search(pattern, content_lower, re.IGNORECASE):
                return severity
        
        # Default severity based on content analysis
        if any(word in content_lower for word in ['outage', 'down', 'critical', 'urgent']):
            return 'Critical'
        elif any(word in content_lower for word in ['slow', 'performance', 'degraded']):
            return 'High'
        else:
            return 'Medium'

    def _generate_tags(self, content: str, services: List[str], symptoms: List[str]) -> List[str]:
        """Generate relevant tags"""
        tags = []
        
        # Add service tags
        tags.extend([f"service:{service}" for service in services])
        
        # Add symptom tags
        tags.extend([f"symptom:{symptom.lower().replace(' ', '-')}" for symptom in symptoms])
        
        # Add technology tags
        tech_keywords = {
            'microservices': r'microservice|micro-service',
            'containerization': r'docker|container|kubernetes|k8s',
            'database': r'database|db|sql|nosql',
            'networking': r'network|dns|load balancer|proxy',
            'monitoring': r'monitoring|metrics|alerting|grafana|prometheus',
            'deployment': r'deployment|deploy|release|rollout'
        }
        
        content_lower = content.lower()
        for tech, pattern in tech_keywords.items():
            if re.search(pattern, content_lower):
                tags.append(f"tech:{tech}")
        
        return list(set(tags))

    def _calculate_extraction_confidence(self, title: str, description: str, 
                                       services: List[str], symptoms: List[str]) -> float:
        """Calculate confidence score for extraction quality"""
        confidence = 0.0
        
        # Title quality (20%)
        if title and len(title) > 5 and title != "Extracted Case":
            confidence += 0.2
        
        # Description quality (30%)
        if description and len(description) > 50:
            confidence += 0.3
        
        # Services detected (25%)
        if services:
            confidence += min(0.25, len(services) * 0.1)
        
        # Symptoms detected (25%)
        if symptoms:
            confidence += min(0.25, len(symptoms) * 0.05)
        
        return min(1.0, confidence)

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php',
            '.sh': 'bash',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json'
        }
        
        for ext, lang in extension_map.items():
            if file_path.endswith(ext):
                return lang
        
        return 'unknown'

    def _extract_functions(self, code: str, language: str) -> List[str]:
        """Extract function names from code"""
        functions = []
        
        patterns = {
            'python': r'def\s+(\w+)\s*\(',
            'javascript': r'function\s+(\w+)\s*\(|(\w+)\s*[:=]\s*(?:function|\()',
            'java': r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(',
            'go': r'func\s+(\w+)\s*\(',
            'bash': r'(\w+)\s*\(\)\s*{'
        }
        
        if language in patterns:
            matches = re.findall(patterns[language], code)
            functions = [match if isinstance(match, str) else next(m for m in match if m) for match in matches]
        
        return list(set(functions))

    def _detect_error_handling(self, code: str, language: str) -> List[str]:
        """Detect error handling patterns in code"""
        patterns = {
            'python': [r'except\s+(\w+)', r'raise\s+(\w+)', r'try:'],
            'javascript': [r'catch\s*\(\s*(\w+)', r'throw\s+new\s+(\w+)', r'try\s*{'],
            'java': [r'catch\s*\(\s*(\w+)', r'throws?\s+(\w+)', r'try\s*{'],
            'go': [r'if\s+err\s*!=\s*nil', r'return\s+.*,\s*err']
        }
        
        error_patterns = []
        if language in patterns:
            for pattern in patterns[language]:
                matches = re.findall(pattern, code)
                error_patterns.extend(matches)
        
        return list(set(error_patterns))

    def _extract_config_references(self, code: str) -> List[str]:
        """Extract configuration references from code"""
        config_patterns = [
            r'config\.get\(["\']([^"\']+)["\']',
            r'os\.environ\.["\']([^"\']+)["\']',
            r'process\.env\.(\w+)',
            r'@Value\(["\']([^"\']+)["\']',
            r'getenv\(["\']([^"\']+)["\']'
        ]
        
        configs = []
        for pattern in config_patterns:
            matches = re.findall(pattern, code)
            configs.extend(matches)
        
        return list(set(configs))

    def _detect_dependencies(self, code: str, language: str) -> List[str]:
        """Detect service dependencies from code"""
        dependency_patterns = {
            'python': [r'import\s+(\w+)', r'from\s+(\w+)\s+import'],
            'javascript': [r'require\(["\']([^"\']+)["\']', r'import\s+.*\s+from\s+["\']([^"\']+)["\']'],
            'java': [r'import\s+([\w.]+)'],
            'go': [r'import\s+["\']([^"\']+)["\']']
        }
        
        dependencies = []
        if language in dependency_patterns:
            for pattern in dependency_patterns[language]:
                matches = re.findall(pattern, code)
                dependencies.extend(matches)
        
        return list(set(dependencies))

    def _extract_headings(self, content: str) -> List[str]:
        """Extract headings from markdown/text"""
        headings = []
        
        # Markdown headings
        markdown_headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        headings.extend(markdown_headings)
        
        # Underlined headings
        lines = content.split('\n')
        for i, line in enumerate(lines[:-1]):
            next_line = lines[i + 1]
            if re.match(r'^[=-]{3,}$', next_line.strip()):
                headings.append(line.strip())
        
        return headings

    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract code blocks from documentation"""
        code_blocks = []
        
        # Markdown code blocks
        fenced_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
        for lang, code in fenced_blocks:
            code_blocks.append({'language': lang or 'unknown', 'code': code.strip()})
        
        # Indented code blocks
        indented_blocks = re.findall(r'\n((?:    .+\n)+)', content)
        for block in indented_blocks:
            code_blocks.append({'language': 'unknown', 'code': block.strip()})
        
        return code_blocks

    def _extract_links(self, content: str) -> List[str]:
        """Extract links from content"""
        # Markdown links
        md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        links = [url for text, url in md_links]
        
        # URL patterns
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)
        links.extend(urls)
        
        return list(set(links))

    def _classify_document_type(self, content: str, source_url: str = None) -> str:
        """Classify document type"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['runbook', 'procedure', 'steps to', 'how to']):
            return 'runbook'
        elif any(word in content_lower for word in ['api', 'endpoint', 'request', 'response']):
            return 'api_doc'
        elif any(word in content_lower for word in ['troubleshoot', 'debug', 'diagnose', 'fix']):
            return 'troubleshooting'
        elif source_url and 'wiki' in source_url:
            return 'wiki'
        else:
            return 'documentation'

    def _generate_doc_tags(self, content: str, doc_type: str) -> List[str]:
        """Generate tags for documentation"""
        tags = [f"type:{doc_type}"]
        
        # Add content-based tags
        content_lower = content.lower()
        
        if 'installation' in content_lower:
            tags.append('category:installation')
        if 'configuration' in content_lower:
            tags.append('category:configuration')
        if 'monitoring' in content_lower:
            tags.append('category:monitoring')
        if 'deployment' in content_lower:
            tags.append('category:deployment')
        
        return tags
    
    def _is_analyzable_file(self, file_path) -> bool:
        """Check if file should be analyzed for knowledge extraction"""
        analyzable_extensions = {
            '.py', '.java', '.js', '.ts', '.go', '.rs', '.cpp', '.c', '.h',
            '.yaml', '.yml', '.json', '.xml', '.properties', '.conf', '.cfg',
            '.md', '.txt', '.rst', '.sql', '.sh', '.bash', '.ps1',
            '.dockerfile', '.docker', 'Dockerfile', 'Makefile'
        }
        
        # Check extension
        if file_path.suffix.lower() in analyzable_extensions:
            return True
        
        # Check specific filenames
        if file_path.name in ['Dockerfile', 'Makefile', 'README', 'CHANGELOG']:
            return True
        
        return False
    
    def _detect_asm_patterns(self, data: Dict[str, Any], domain: str = None) -> Dict[str, Any]:
        """Detect ASM-specific patterns in the extracted data"""
        patterns = {
            'architecture_patterns': [],
            'integration_patterns': [],
            'operational_patterns': [],
            'domain_specific': []
        }
        
        # Architecture patterns
        if 'microservice' in ' '.join(data.get('services', [])).lower():
            patterns['architecture_patterns'].append('microservices_architecture')
        
        if any('kafka' in dep.lower() for dep in data.get('dependencies', [])):
            patterns['architecture_patterns'].append('event_driven_architecture')
        
        # Integration patterns
        if any('rest' in func.lower() or 'api' in func.lower() for func in data.get('functions', [])):
            patterns['integration_patterns'].append('rest_api_integration')
        
        # Operational patterns
        if any('health' in func.lower() or 'status' in func.lower() for func in data.get('functions', [])):
            patterns['operational_patterns'].append('health_monitoring')
        
        # Domain-specific patterns based on domain
        if domain:
            if domain == 'core_services':
                patterns['domain_specific'].extend(self._detect_core_services_patterns(data))
            elif domain == 'topology':
                patterns['domain_specific'].extend(self._detect_topology_patterns(data))
            elif domain == 'observers':
                patterns['domain_specific'].extend(self._detect_observer_patterns(data))
            elif domain == 'ui':
                patterns['domain_specific'].extend(self._detect_ui_patterns(data))
        
        return patterns
    
    def _detect_core_services_patterns(self, data: Dict[str, Any]) -> List[str]:
        """Detect ASM core/backend services patterns"""
        patterns = []
        functions = ' '.join(data.get('functions', [])).lower()
        dependencies = ' '.join(data.get('dependencies', [])).lower()
        
        # Backend service patterns
        if 'service' in functions and ('topology' in functions or 'merge' in functions):
            patterns.append('asm_backend_service_pattern')
        
        # Kafka integration patterns
        if 'kafka' in dependencies or 'producer' in functions or 'consumer' in functions:
            patterns.append('kafka_messaging_pattern')
        
        # Database patterns
        if 'cassandra' in dependencies or 'cql' in functions:
            patterns.append('cassandra_graph_pattern')
        if 'postgresql' in dependencies or 'sql' in functions:
            patterns.append('postgresql_relational_pattern')
        
        # ASM-specific service patterns
        if 'merge' in functions and 'composite' in functions:
            patterns.append('merge_service_pattern')
        if 'status' in functions and 'event' in functions:
            patterns.append('status_service_pattern')
        if 'inventory' in functions:
            patterns.append('inventory_service_pattern')
        
        return patterns
    
    def _detect_topology_patterns(self, data: Dict[str, Any]) -> List[str]:
        """Detect topology-specific patterns"""
        patterns = []
        functions = ' '.join(data.get('functions', [])).lower()
        
        if 'merge' in functions:
            patterns.append('topology_merge_pattern')
        if 'inventory' in functions:
            patterns.append('inventory_management_pattern')
        if 'sync' in functions:
            patterns.append('synchronization_pattern')
        
        return patterns
    
    def _detect_observer_patterns(self, data: Dict[str, Any]) -> List[str]:
        """Detect observer-specific patterns"""
        patterns = []
        functions = ' '.join(data.get('functions', [])).lower()
        
        if 'observe' in functions or 'watch' in functions:
            patterns.append('observer_pattern')
        if 'event' in functions:
            patterns.append('event_handling_pattern')
        if 'poll' in functions:
            patterns.append('polling_pattern')
        
        return patterns
    
    def _detect_ui_patterns(self, data: Dict[str, Any]) -> List[str]:
        """Detect UI-specific patterns"""
        patterns = []
        functions = ' '.join(data.get('functions', [])).lower()
        languages = data.get('languages', [])
        
        if 'react' in ' '.join(languages).lower():
            patterns.append('react_component_pattern')
        if 'component' in functions:
            patterns.append('ui_component_pattern')
        if 'render' in functions:
            patterns.append('rendering_pattern')
        
        return patterns
