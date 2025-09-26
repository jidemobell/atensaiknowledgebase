import re
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from models import ExtractedKnowledge, KnowledgeSourceType

class KnowledgeExtractor:
    """Extracts structured information from raw text content"""
    
    def __init__(self):
        # Enhanced service patterns for auto-detection - more comprehensive
        self.service_patterns = {
            # ASM/NOI specific services
            'topology-service': r'topology[-_]?service|nasm-topology|topology[-_]?merge|topology merge',
            'layout-service': r'layout[-_]?service|nasm-layout',
            'status-service': r'status[-_]?service|nasm-status',
            'inventory-service': r'inventory[-_]?service|nasm-inventory',
            'observer': r'\bobserver\b|file[-_]?observer|rest[-_]?observer',
            'ui-content': r'ui[-_]?content|hdm[-_]?common[-_]?ui|user[-_]?interface',
            'asm-mime': r'asm[-_]?mime|ea[-_]?asm[-_]?mime',
            'aggregation-dedup': r'aggregation[-_]?dedup|dedup[-_]?service',
            'analytics': r'analytics|hdm[-_]?analytics',
            'spark': r'\bspark\b|apache[-_]?spark',
            
            # Infrastructure services
            'kafka': r'\bkafka\b|apache[-_]?kafka',
            'cassandra': r'\bcassandra\b|apache[-_]?cassandra',
            'elasticsearch': r'elasticsearch|elastic[-_]?search',
            'redis': r'\bredis\b',
            'mongodb': r'mongodb|mongo[-_]?db',
            'postgresql': r'postgresql|postgres|postgre',
            
            # Container/K8s services
            'kubernetes': r'kubernetes|k8s|openshift|ocp',
            'docker': r'\bdocker\b|container',
            'helm': r'\bhelm\b|helm[-_]?chart',
            'operator': r'operator|csv|clusterserviceversion',
            
            # Web services
            'nginx': r'\bnginx\b',
            'apache': r'\bapache\b|httpd',
            'node': r'node\.js|nodejs',
            
            # IBM specific
            'cp4aiops': r'cp4aiops|cloud[-_]?pak|aiops',
            'noi': r'\bnoi\b|netcool|event[-_]?manager',
            'watson': r'watson|watsonx',
            'cognos': r'cognos'
        }
        
        # Comprehensive error pattern recognition
        self.error_patterns = {
            # Resource issues
            'timeout': r'timeout|timed out|time out|connection timeout',
            'connection_refused': r'connection refused|connection denied|connection reset',
            'out_of_memory': r'out of memory|oom|memory exceeded|heap space',
            'disk_space': r'disk space|no space left|disk full|storage full',
            'cpu_high': r'high cpu|cpu usage|cpu spike|cpu load',
            
            # Security/Access issues
            'permission_denied': r'permission denied|access denied|forbidden|unauthorized',
            'authentication_failed': r'authentication failed|auth failed|login failed',
            'certificate_error': r'certificate|ssl|tls|handshake failed|cert expired',
            
            # Network issues
            'network_error': r'network error|network unreachable|dns|host not found',
            'port_blocked': r'port blocked|firewall|connection blocked',
            'dns_resolution': r'dns resolution|name not resolved|nslookup failed',
            
            # Application issues
            'pod_restart': r'pod restart|container restart|crashloopbackoff',
            'service_unavailable': r'service unavailable|service down|endpoint not found',
            'deployment_failed': r'deployment failed|rollout failed|image pull',
            'config_error': r'config error|configuration|invalid config',
            
            # Database issues
            'database_connection': r'database connection|db connection|connection pool',
            'query_timeout': r'query timeout|slow query|deadlock',
            'table_lock': r'table lock|lock timeout|blocked query',
            
            # Performance issues
            'slow_response': r'slow response|performance|response time|latency',
            'high_load': r'high load|load average|system overload',
            'memory_leak': r'memory leak|heap dump|gc overhead',
            
            # Version/Compatibility issues
            'version_mismatch': r'version mismatch|incompatible|version conflict',
            'api_deprecated': r'deprecated|api version|unsupported version',
            'upgrade_issue': r'upgrade issue|migration failed|version upgrade'
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

    def extract_from_support_case_json(self, json_content: str) -> Dict[str, Any]:
        """Extract knowledge from support case JSON files with adaptive context handling"""
        try:
            case_data = json.loads(json_content) if isinstance(json_content, str) else json_content
        except json.JSONDecodeError as e:
            return {'error': f'Invalid JSON format: {e}'}
        
        # Flexible extraction - handle various JSON structures
        case_info = self._extract_flexible_case_info(case_data)
        
        # Extract and analyze comments for resolution patterns
        comments = case_data.get('public_comments', []) or case_data.get('comments', []) or []
        resolution_patterns = self._extract_resolution_patterns(comments)
        hotfix_info = self._extract_hotfix_information(comments)
        command_patterns = self._extract_command_patterns(comments)
        
        # Analyze all available text content
        all_text_content = self._gather_all_text_content(case_data)
        
        # Enhanced analysis with multiple text sources
        services = self._detect_services_enhanced(all_text_content)
        error_patterns = self._extract_error_messages_enhanced(all_text_content)
        symptoms = self._extract_symptoms_enhanced(all_text_content)
        severity = self._detect_severity_enhanced(all_text_content, case_data)
        
        # Enhanced categorization
        case_category = self._categorize_case(case_data, all_text_content)
        impact_assessment = self._assess_impact(case_data, services, symptoms)
        
        # Generate comprehensive tags
        tags = self._generate_comprehensive_tags(case_data, services, resolution_patterns, case_category)
        
        # Advanced confidence calculation
        confidence = self._calculate_advanced_confidence(case_info, resolution_patterns, hotfix_info, all_text_content)
        
        # Extract timeline if available
        timeline = self._extract_case_timeline(comments)
        
        return {
            **case_info,
            'services': services,
            'resolution_patterns': resolution_patterns,
            'hotfix_info': hotfix_info,
            'command_patterns': command_patterns,
            'error_patterns': error_patterns,
            'symptoms': symptoms,
            'severity': severity,
            'case_category': case_category,
            'impact_assessment': impact_assessment,
            'timeline': timeline,
            'tags': tags,
            'confidence': confidence,
            'knowledge_type': 'support_case',
            'text_quality_score': self._assess_text_quality(all_text_content)
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
                # Core services includes topology patterns
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
    
    def _extract_resolution_patterns(self, comments: List[Dict]) -> List[str]:
        """Extract resolution patterns from case comments"""
        patterns = []
        
        # Common resolution patterns for ASM/NOI cases
        resolution_keywords = [
            'hotfix', 'patch', 'upgrade', 'rollback', 'restart',
            'oc patch', 'csv', 'deployment', 'image digest',
            'must-gather', 'logs', 'describe pod', 'configmap'
        ]
        
        for comment in comments:
            message = comment.get('message', '').lower()
            for keyword in resolution_keywords:
                if keyword in message and keyword not in patterns:
                    patterns.append(keyword)
        
        return patterns
    
    def _extract_hotfix_information(self, comments: List[Dict]) -> Dict[str, Any]:
        """Extract hotfix-related information from comments"""
        hotfix_info = {
            'images': [],
            'digests': [],
            'tags': [],
            'procedures': []
        }
        
        for comment in comments:
            message = comment.get('message', '')
            
            # Extract image references
            image_pattern = r'(cp\.icr\.io/cp/noi/[\w-]+)'
            images = re.findall(image_pattern, message)
            hotfix_info['images'].extend(images)
            
            # Extract SHA digests
            digest_pattern = r'sha256:([a-f0-9]{64})'
            digests = re.findall(digest_pattern, message)
            hotfix_info['digests'].extend(digests)
            
            # Extract version tags
            tag_pattern = r'v\d+\.\d+\.\d+-\d+-[a-f0-9]+'
            tags = re.findall(tag_pattern, message)
            hotfix_info['tags'].extend(tags)
            
            # Extract procedure steps
            if 'solution attempt' in message.lower() or 'installation instructions' in message.lower():
                hotfix_info['procedures'].append(message[:500])  # First 500 chars
        
        # Remove duplicates
        for key in ['images', 'digests', 'tags']:
            hotfix_info[key] = list(set(hotfix_info[key]))
        
        return hotfix_info
    
    def _extract_command_patterns(self, comments: List[Dict]) -> List[str]:
        """Extract command patterns from case comments"""
        commands = []
        
        for comment in comments:
            message = comment.get('message', '')
            
            # Extract oc commands
            oc_pattern = r'(oc (?:patch|get|describe|edit|delete)\s+[^\n]+)'
            oc_commands = re.findall(oc_pattern, message, re.IGNORECASE)
            commands.extend(oc_commands)
            
            # Extract skopeo commands
            skopeo_pattern = r'(skopeo (?:copy|inspect)\s+[^\n]+)'
            skopeo_commands = re.findall(skopeo_pattern, message, re.IGNORECASE)
            commands.extend(skopeo_commands)
            
            # Extract kubectl commands
            kubectl_pattern = r'(kubectl (?:get|describe|logs|apply)\s+[^\n]+)'
            kubectl_commands = re.findall(kubectl_pattern, message, re.IGNORECASE)
            commands.extend(kubectl_commands)
        
        return list(set(commands))
    
    def _generate_case_tags(self, case_data: Dict, services: List[str], resolution_patterns: List[str]) -> List[str]:
        """Generate tags for support case"""
        tags = []
        
        # Add case number as tag
        if case_data.get('case_number'):
            tags.append(f"case_{case_data['case_number']}")
        
        # Add service tags
        tags.extend([f"service_{service}" for service in services])
        
        # Add resolution pattern tags
        tags.extend([f"resolution_{pattern.replace(' ', '_')}" for pattern in resolution_patterns])
        
        # Add version tags if mentioned
        problem_desc = case_data.get('problem_description', '').lower()
        if '1.6.14' in problem_desc:
            tags.append('version_1.6.14')
        if '1.6.15' in problem_desc:
            tags.append('version_1.6.15')
        if '1.6.13' in problem_desc:
            tags.append('version_1.6.13')
        
        # Add component tags
        if 'topology' in problem_desc:
            tags.append('component_topology')
        if 'ui' in problem_desc or 'interface' in problem_desc:
            tags.append('component_ui')
        if 'observer' in problem_desc:
            tags.append('component_observer')
        
        return list(set(tags))
    
    def _calculate_case_confidence(self, case_info: Dict, resolution_patterns: List[str], hotfix_info: Dict) -> float:
        """Calculate confidence score for case extraction"""
        confidence = 0.0
        
        # Base confidence from case completeness
        if case_info.get('case_number'):
            confidence += 0.2
        if case_info.get('problem_description'):
            confidence += 0.2
        if case_info.get('resolution_description'):
            confidence += 0.2
        
        # Bonus for resolution patterns
        if resolution_patterns:
            confidence += min(0.2, len(resolution_patterns) * 0.05)
        
        # Bonus for hotfix information
        if hotfix_info.get('images') or hotfix_info.get('digests'):
            confidence += 0.1
        
        # Bonus for procedures
        if hotfix_info.get('procedures'):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _extract_flexible_case_info(self, case_data: Dict) -> Dict[str, Any]:
        """Flexibly extract case information from various JSON structures"""
        # Handle different field names and structures
        case_info = {}
        
        # Case number variations
        case_info['case_number'] = (
            case_data.get('case_number') or 
            case_data.get('caseNumber') or 
            case_data.get('case_id') or 
            case_data.get('id') or 
            case_data.get('ticket_number') or 
            'Unknown'
        )
        
        # Subject/title variations
        case_info['subject'] = (
            case_data.get('subject') or 
            case_data.get('title') or 
            case_data.get('summary') or 
            case_data.get('description', '')[:100] or 
            ''
        )
        
        # Problem description variations
        case_info['problem_description'] = (
            case_data.get('problem_description') or 
            case_data.get('description') or 
            case_data.get('issue_description') or 
            case_data.get('problem') or 
            ''
        )
        
        # Resolution variations
        case_info['resolution_description'] = (
            case_data.get('resolution_description') or 
            case_data.get('resolution') or 
            case_data.get('solution') or 
            case_data.get('fix') or 
            ''
        )
        
        # Timestamps
        case_info['parsed_at'] = (
            case_data.get('parsed_at') or 
            case_data.get('created_at') or 
            case_data.get('timestamp') or 
            ''
        )
        
        case_info['case_type'] = 'support_case'
        
        return case_info
    
    def _gather_all_text_content(self, case_data: Dict) -> str:
        """Gather all available text content from the case data"""
        text_parts = []
        
        # Add main text fields
        for field in ['subject', 'title', 'problem_description', 'description', 
                     'resolution_description', 'resolution', 'full_text_for_rag', 'summary']:
            if case_data.get(field):
                text_parts.append(str(case_data[field]))
        
        # Add comments/conversations
        comments = case_data.get('public_comments', []) or case_data.get('comments', []) or []
        for comment in comments:
            if isinstance(comment, dict):
                message = comment.get('message', '') or comment.get('text', '') or comment.get('content', '')
                if message:
                    text_parts.append(str(message))
            elif isinstance(comment, str):
                text_parts.append(comment)
        
        # Add any other text fields
        for key, value in case_data.items():
            if isinstance(value, str) and len(value) > 20 and key not in ['case_number', 'id', 'parsed_at']:
                if key not in ['subject', 'title', 'problem_description', 'description', 'resolution_description']:
                    text_parts.append(value)
        
        return ' '.join(text_parts)
    
    def _detect_services_enhanced(self, text_content: str) -> List[str]:
        """Enhanced service detection with context awareness"""
        services = []
        text_lower = text_content.lower()
        
        # Use enhanced service patterns
        for service, pattern in self.service_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                services.append(service)
        
        # Context-specific detection
        # IBM Cloud Pak services
        if 'cloud pak' in text_lower or 'cp4aiops' in text_lower:
            services.append('cp4aiops')
        
        # Version-specific detection
        version_pattern = r'(?:noi|event manager|aiops)\s*(?:v?(\d+\.\d+(?:\.\d+)?))'
        versions = re.findall(version_pattern, text_lower)
        for version in versions:
            services.append(f'noi-{version}')
        
        # Remove duplicates and return
        return list(set(services))
    
    def _extract_error_messages_enhanced(self, text_content: str) -> List[str]:
        """Enhanced error message extraction"""
        error_messages = []
        
        # Use enhanced error patterns
        for error_type, pattern in self.error_patterns.items():
            if re.search(pattern, text_content, re.IGNORECASE):
                error_messages.append(error_type)
        
        # Extract actual error text
        error_text_patterns = [
            r'ERROR:?\s*(.+)',
            r'Exception:?\s*(.+)',
            r'Failed:?\s*(.+)',
            r'Error:?\s*(.+)',
            r'"([^"]*(?:error|exception|failed|fault)[^"]*)"',
            r'Stack trace:?\s*(.+)',
            r'(?:could not|cannot|unable to)\s+(.+?)(?:\.|$)'
        ]
        
        for pattern in error_text_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match.strip()) > 10:  # Filter out very short matches
                    error_messages.append(match.strip()[:200])  # Limit length
        
        return list(set(error_messages))
    
    def _extract_symptoms_enhanced(self, text_content: str) -> List[str]:
        """Enhanced symptom extraction with better pattern matching"""
        symptoms = []
        text_lower = text_content.lower()
        
        # Enhanced symptom patterns
        symptom_patterns = {
            'pod_restarting': r'pod\s+(?:is\s+)?(?:restart|restarting|restart)',
            'service_down': r'service\s+(?:is\s+)?(?:down|unavailable|not responding|offline)',
            'slow_performance': r'(?:slow|poor|degraded)\s+(?:performance|response|speed)',
            'memory_issues': r'(?:memory|heap)\s+(?:issues?|problems?|errors?|full|exceeded)',
            'connection_issues': r'(?:connection|connectivity)\s+(?:issues?|problems?|errors?|failed)',
            'timeout_issues': r'(?:timeout|time\s+out)\s+(?:issues?|problems?|errors?)',
            'authentication_problems': r'(?:authentication|auth|login)\s+(?:issues?|problems?|failed)',
            'deployment_failures': r'(?:deployment|deploy)\s+(?:failed|failures?|issues?)',
            'data_inconsistency': r'(?:data|database)\s+(?:inconsistency|corruption|issues?)',
            'ui_problems': r'(?:ui|interface|dashboard)\s+(?:issues?|problems?|not\s+working)'
        }
        
        for symptom, pattern in symptom_patterns.items():
            if re.search(pattern, text_lower):
                symptoms.append(symptom.replace('_', ' ').title())
        
        # Look for user-reported symptoms
        user_symptom_patterns = [
            r'users?\s+(?:are\s+)?(?:unable to|cannot|can\'t)\s+(.+?)(?:\.|,|$)',
            r'experiencing\s+(.+?)(?:\.|,|when)',
            r'having\s+(?:issues?|problems?)\s+(?:with\s+)?(.+?)(?:\.|,|$)',
            r'seeing\s+(.+?)(?:\.|,|error|issue)',
            r'getting\s+(.+?)(?:\.|,|error|when)'
        ]
        
        for pattern in user_symptom_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match.strip()) > 5:
                    symptoms.append(match.strip()[:100])
        
        return list(set(symptoms))
    
    def _detect_severity_enhanced(self, text_content: str, case_data: Dict) -> str:
        """Enhanced severity detection with multiple indicators"""
        text_lower = text_content.lower()
        
        # Check explicit severity indicators
        severity_indicators = {
            'Critical': [
                r'critical|sev[- ]?1|priority[- ]?1|urgent|emergency',
                r'production\s+down|outage|system\s+down',
                r'data\s+loss|corruption|security\s+breach'
            ],
            'High': [
                r'high|sev[- ]?2|priority[- ]?2|important',
                r'performance\s+degradation|significant\s+impact',
                r'multiple\s+users?\s+affected'
            ],
            'Medium': [
                r'medium|moderate|sev[- ]?3|priority[- ]?3|normal',
                r'some\s+users?\s+affected|partial\s+functionality'
            ],
            'Low': [
                r'low|minor|sev[- ]?4|priority[- ]?4',
                r'cosmetic|enhancement|feature\s+request'
            ]
        }
        
        for severity, patterns in severity_indicators.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return severity
        
        # Infer severity from context
        if any(word in text_lower for word in ['hotfix', 'patch', 'urgent', 'asap']):
            return 'High'
        elif any(word in text_lower for word in ['question', 'how to', 'documentation']):
            return 'Low'
        
        return 'Medium'
    
    def _categorize_case(self, case_data: Dict, text_content: str) -> str:
        """Categorize the case based on content analysis"""
        text_lower = text_content.lower()
        
        # Category patterns
        category_patterns = {
            'hotfix_deployment': r'hotfix|patch|image\s+digest|csv\s+patch|oc\s+patch',
            'version_upgrade': r'upgrade|migration|version\s+update|rollback',
            'performance_issue': r'performance|slow|timeout|resource\s+usage|memory|cpu',
            'configuration_issue': r'configuration|config|setup|deployment\s+failed',
            'authentication_issue': r'authentication|auth|login|permission|rbac',
            'networking_issue': r'network|connectivity|dns|firewall|port',
            'data_issue': r'data\s+loss|corruption|sync|database|cassandra|postgres',
            'ui_issue': r'ui|interface|dashboard|browser|display',
            'integration_issue': r'integration|observer|kafka|api|webhook',
            'documentation_request': r'documentation|how\s+to|example|guide|tutorial'
        }
        
        for category, pattern in category_patterns.items():
            if re.search(pattern, text_lower):
                return category
        
        return 'general_issue'
    
    def _assess_impact(self, case_data: Dict, services: List[str], symptoms: List[str]) -> Dict[str, Any]:
        """Assess the impact of the case"""
        impact = {
            'scope': 'unknown',
            'affected_components': len(services),
            'symptom_count': len(symptoms),
            'business_impact': 'low'
        }
        
        # Determine scope
        text = str(case_data).lower()
        if any(word in text for word in ['all users', 'entire system', 'production']):
            impact['scope'] = 'system-wide'
        elif any(word in text for word in ['multiple users', 'several', 'many']):
            impact['scope'] = 'multi-user'
        elif any(word in text for word in ['single user', 'one user', 'specific']):
            impact['scope'] = 'single-user'
        
        # Assess business impact
        if any(word in text for word in ['revenue', 'business critical', 'sla', 'customer']):
            impact['business_impact'] = 'high'
        elif any(word in text for word in ['important', 'significant', 'priority']):
            impact['business_impact'] = 'medium'
        
        return impact
    
    def _generate_comprehensive_tags(self, case_data: Dict, services: List[str], 
                                   resolution_patterns: List[str], case_category: str) -> List[str]:
        """Generate comprehensive tags for better searchability"""
        tags = []
        
        # Basic case tags
        if case_data.get('case_number'):
            tags.append(f"case_{case_data['case_number']}")
        
        # Service tags
        tags.extend([f"service_{service}" for service in services])
        
        # Resolution pattern tags
        tags.extend([f"resolution_{pattern.replace(' ', '_')}" for pattern in resolution_patterns])
        
        # Category tag
        tags.append(f"category_{case_category}")
        
        # Version tags
        text = str(case_data).lower()
        version_patterns = [
            (r'1\.6\.14', 'version_1.6.14'),
            (r'1\.6\.15', 'version_1.6.15'),
            (r'1\.6\.13', 'version_1.6.13'),
            (r'cp4aiops', 'product_cp4aiops'),
            (r'event\s+manager', 'product_event_manager'),
            (r'noi', 'product_noi')
        ]
        
        for pattern, tag in version_patterns:
            if re.search(pattern, text):
                tags.append(tag)
        
        # Component tags
        component_patterns = {
            'topology': r'topology|nasm-topology',
            'ui': r'ui|interface|dashboard',
            'observer': r'observer|file-observer',
            'kafka': r'kafka',
            'cassandra': r'cassandra',
            'kubernetes': r'kubernetes|k8s|openshift'
        }
        
        for component, pattern in component_patterns.items():
            if re.search(pattern, text):
                tags.append(f"component_{component}")
        
        return list(set(tags))
    
    def _calculate_advanced_confidence(self, case_info: Dict, resolution_patterns: List[str], 
                                     hotfix_info: Dict, text_content: str) -> float:
        """Advanced confidence calculation based on multiple factors"""
        confidence = 0.0
        
        # Base confidence from case completeness
        if case_info.get('case_number') and case_info['case_number'] != 'Unknown':
            confidence += 0.15
        if case_info.get('problem_description') and len(case_info['problem_description']) > 50:
            confidence += 0.15
        if case_info.get('resolution_description') and len(case_info['resolution_description']) > 20:
            confidence += 0.15
        
        # Confidence from resolution patterns
        if resolution_patterns:
            confidence += min(0.2, len(resolution_patterns) * 0.04)
        
        # Confidence from hotfix information
        if hotfix_info.get('images') or hotfix_info.get('digests'):
            confidence += 0.1
        if hotfix_info.get('procedures'):
            confidence += 0.1
        
        # Confidence from text quality
        text_length = len(text_content)
        if text_length > 500:
            confidence += 0.05
        if text_length > 2000:
            confidence += 0.05
        
        # Confidence from structured data
        if 'oc patch' in text_content or 'kubectl' in text_content:
            confidence += 0.05
        if re.search(r'sha256:[a-f0-9]{64}', text_content):
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def _extract_case_timeline(self, comments: List[Dict]) -> List[Dict]:
        """Extract timeline from case comments"""
        timeline = []
        
        for comment in comments:
            if isinstance(comment, dict) and comment.get('timestamp'):
                timeline.append({
                    'timestamp': comment['timestamp'],
                    'author': comment.get('author', 'Unknown'),
                    'action': self._identify_comment_action(comment.get('message', ''))
                })
        
        return sorted(timeline, key=lambda x: x['timestamp'])
    
    def _identify_comment_action(self, message: str) -> str:
        """Identify the type of action in a comment"""
        message_lower = message.lower()
        
        if 'solution attempt' in message_lower:
            return 'solution_provided'
        elif 'case closed' in message_lower or 'resolved' in message_lower:
            return 'case_closed'
        elif 'customer' in message_lower and 'reply' in message_lower:
            return 'customer_response'
        elif 'escalat' in message_lower:
            return 'escalation'
        elif 'assign' in message_lower:
            return 'assignment'
        else:
            return 'communication'
    
    def _assess_text_quality(self, text_content: str) -> float:
        """Assess the quality of text content for knowledge extraction"""
        if not text_content:
            return 0.0
        
        score = 0.0
        
        # Length factor
        length = len(text_content)
        if length > 100:
            score += 0.2
        if length > 1000:
            score += 0.2
        if length > 5000:
            score += 0.1
        
        # Structure indicators
        if re.search(r'##?\s+', text_content):  # Headers
            score += 0.1
        if re.search(r'^\d+\.', text_content, re.MULTILINE):  # Numbered lists
            score += 0.1
        if re.search(r'```|`[^`]+`', text_content):  # Code blocks
            score += 0.1
        
        # Technical content indicators
        if re.search(r'[a-f0-9]{8,}', text_content):  # Hashes/IDs
            score += 0.1
        if re.search(r'https?://', text_content):  # URLs
            score += 0.05
        if re.search(r'\b\w+\.\w+\.\w+', text_content):  # Version numbers
            score += 0.05
        
        return min(1.0, score)
