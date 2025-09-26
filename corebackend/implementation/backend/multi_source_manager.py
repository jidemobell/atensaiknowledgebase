from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import uuid
from knowledge_extractor import KnowledgeExtractor

class MultiSourceKnowledgeManager:
    """Manages knowledge from multiple sources with learning capabilities"""
    
    def __init__(self):
        self.extractor = KnowledgeExtractor()
        self.knowledge_store = {
            'cases': [],
            'code': [],
            'documentation': [],
            'search_history': [],
            'diagnostic_sessions': [],
            'feedback': []
        }
        self.learning_engine = LearningEngine()

    # Case Management
    async def add_manual_case(self, raw_content: str, user_metadata: Dict = None) -> Dict[str, Any]:
        """Add a manually entered case with smart extraction"""
        
        # Extract structured data from raw content
        extracted = self.extractor.extract_from_salesforce_case(raw_content)
        
        # Create case entry
        case = {
            'id': str(uuid.uuid4()),
            'title': extracted.title,
            'description': extracted.description,
            'raw_content': raw_content,
            'affected_services': extracted.affected_services,
            'symptoms': extracted.symptoms,
            'error_messages': extracted.error_messages,
            'severity': extracted.severity,
            'tags': extracted.tags,
            'confidence': extracted.confidence,
            'manual_entry': True,
            'created_date': datetime.now().isoformat(),
            'source_type': 'salesforce_case',
            'extraction_metadata': {
                'auto_extracted': True,
                'confidence_score': extracted.confidence,
                'extraction_timestamp': datetime.now().isoformat()
            }
        }
        
        # Apply user overrides if provided
        if user_metadata:
            case.update(user_metadata)
        
        # Store case
        self.knowledge_store['cases'].append(case)
        
        # Find similar cases
        similar_cases = await self.find_similar_cases(case)
        
        return {
            'case': case,
            'similar_cases': similar_cases,
            'suggestions': self._generate_case_suggestions(case, similar_cases)
        }

    async def add_code_knowledge(self, repo: str, file_path: str, 
                               code_content: str, commit_info: Dict = None) -> Dict[str, Any]:
        """Add code knowledge from local repository sources"""
        
        # Extract code intelligence using the new method
        extracted = self.extractor.extract_from_code_file(code_content, file_path)
        
        code_entry = {
            'id': str(uuid.uuid4()),
            'repository': repo,
            'file_path': file_path,
            'code_snippet': code_content,
            'language': extracted['language'],
            'functions': extracted['functions'],
            'error_patterns': extracted['error_patterns'],
            'config_references': extracted['config_references'],
            'dependencies': extracted['dependencies'],
            'related_services': extracted['services'],
            'commit_info': commit_info or {},
            'created_date': datetime.now().isoformat(),
            'tags': [f"lang:{extracted['language']}", f"repo:{repo}"]
        }
        
        self.knowledge_store['code'].append(code_entry)
        return code_entry

    async def load_asm_repositories(self, asm_repos_dir: str = "data/asm_repositories") -> Dict[str, Any]:
        """Load and analyze all ASM repositories from local directory"""
        import os
        from pathlib import Path
        
        asm_path = Path(asm_repos_dir)
        if not asm_path.exists():
            return {'error': f'ASM repositories directory not found: {asm_repos_dir}'}
        
        results = {
            'repositories_processed': 0,
            'total_files_analyzed': 0,
            'domains_found': [],
            'patterns_detected': {},
            'errors': []
        }
        
        # Process each domain directory
        for domain_dir in asm_path.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                results['domains_found'].append(domain)
                
                try:
                    # Extract knowledge from the entire domain repository
                    extracted = self.extractor.extract_from_asm_repository(str(domain_dir), domain)
                    
                    if 'error' not in extracted:
                        results['repositories_processed'] += 1
                        results['total_files_analyzed'] += extracted.get('files_analyzed', 0)
                        results['patterns_detected'][domain] = extracted.get('patterns', {})
                        
                        # Store the extracted knowledge
                        asm_entry = {
                            'id': str(uuid.uuid4()),
                            'domain': domain,
                            'repository_path': str(domain_dir),
                            'analysis_data': extracted,
                            'created_date': datetime.now().isoformat(),
                            'tags': [f"domain:{domain}", "source:asm_repository"]
                        }
                        
                        # Add to our knowledge store under a new 'asm_repositories' category
                        if 'asm_repositories' not in self.knowledge_store:
                            self.knowledge_store['asm_repositories'] = []
                        self.knowledge_store['asm_repositories'].append(asm_entry)
                    else:
                        results['errors'].append(f"Error analyzing {domain}: {extracted['error']}")
                        
                except Exception as e:
                    results['errors'].append(f"Error processing domain {domain}: {str(e)}")
        
        return results

    async def add_documentation(self, title: str, content: str, 
                              source_url: str = None, doc_type: str = None) -> Dict[str, Any]:
        """Add documentation knowledge"""
        
        # Extract documentation intelligence
        extracted = self.extractor.extract_from_documentation(content, source_url)
        
        doc_entry = {
            'id': str(uuid.uuid4()),
            'title': title,
            'content': content,
            'source_url': source_url,
            'doc_type': extracted['doc_type'],
            'headings': extracted['headings'],
            'code_blocks': extracted['code_blocks'],
            'links': extracted['links'],
            'related_services': extracted['services'],
            'tags': extracted['tags'],
            'created_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        self.knowledge_store['documentation'].append(doc_entry)
        return doc_entry

    # Unified Search
    async def unified_search(self, query: str, search_mode: str = "all", 
                           session_id: str = None, filters: Dict = None) -> Dict[str, Any]:
        """Search across all knowledge sources"""
        
        # Create or get session
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Record search interaction
        search_record = {
            'session_id': session_id,
            'query': query,
            'search_mode': search_mode,
            'timestamp': datetime.now().isoformat(),
            'filters': filters or {}
        }
        self.knowledge_store['search_history'].append(search_record)
        
        results = {
            'query': query,
            'session_id': session_id,
            'total_results': 0,
            'case_results': [],
            'code_results': [],
            'doc_results': [],
            'historical_searches': [],
            'suggestions': [],
            'diagnostic_confidence': 0.0
        }
        
        # Search cases
        if search_mode in ['all', 'cases']:
            case_results = await self._search_cases(query, filters)
            results['case_results'] = case_results
            results['total_results'] += len(case_results)
        
        # Search code
        if search_mode in ['all', 'code']:
            code_results = await self._search_code(query, filters)
            results['code_results'] = code_results
            results['total_results'] += len(code_results)
        
        # Search documentation
        if search_mode in ['all', 'docs']:
            doc_results = await self._search_documentation(query, filters)
            results['doc_results'] = doc_results
            results['total_results'] += len(doc_results)
        
        # Search history
        if search_mode in ['all', 'history']:
            historical_results = await self._search_history(query, session_id)
            results['historical_searches'] = historical_results
        
        # Generate suggestions and diagnostic confidence
        results['suggestions'] = await self._generate_search_suggestions(query, results)
        results['diagnostic_confidence'] = await self._calculate_diagnostic_confidence(query, results)
        
        return results

    async def start_diagnostic_session(self, initial_query: str, user_id: str = None) -> str:
        """Start a new diagnostic session"""
        
        session_id = str(uuid.uuid4())
        
        session = {
            'id': session_id,
            'initial_query': initial_query,
            'user_id': user_id,
            'search_history': [],
            'knowledge_sources_accessed': [],
            'cases_viewed': [],
            'resolution_attempted': False,
            'created_date': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self.knowledge_store['diagnostic_sessions'].append(session)
        return session_id

    async def track_interaction(self, session_id: str, interaction_type: str, 
                              content: Dict, effectiveness: int = None):
        """Track user interactions during diagnostic session"""
        
        # Find session
        session = next((s for s in self.knowledge_store['diagnostic_sessions'] 
                       if s['id'] == session_id), None)
        
        if session:
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'type': interaction_type,
                'content': content,
                'effectiveness_score': effectiveness
            }
            session['search_history'].append(interaction)

    async def record_feedback(self, session_id: str, item_id: str, item_type: str,
                            feedback_type: str, rating: int = None, comments: str = None):
        """Record user feedback on knowledge items"""
        
        feedback = {
            'id': str(uuid.uuid4()),
            'session_id': session_id,
            'item_id': item_id,
            'item_type': item_type,
            'feedback_type': feedback_type,
            'rating': rating,
            'comments': comments,
            'timestamp': datetime.now().isoformat()
        }
        
        self.knowledge_store['feedback'].append(feedback)
        
        # Update learning engine
        await self.learning_engine.process_feedback(feedback)

    async def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from the learning engine"""
        return await self.learning_engine.generate_insights(self.knowledge_store)

    # Private methods for searching
    async def _search_cases(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search through cases"""
        query_lower = query.lower()
        results = []
        
        for case in self.knowledge_store['cases']:
            score = 0
            
            # Title match
            if query_lower in case.get('title', '').lower():
                score += 3
            
            # Description match
            if query_lower in case.get('description', '').lower():
                score += 2
            
            # Service match
            for service in case.get('affected_services', []):
                if query_lower in service.lower():
                    score += 4
            
            # Symptom match
            for symptom in case.get('symptoms', []):
                if query_lower in symptom.lower():
                    score += 3
            
            # Apply filters
            if filters:
                if filters.get('service') and filters['service'] not in case.get('affected_services', []):
                    continue
                if filters.get('severity') and filters['severity'] != case.get('severity'):
                    continue
            
            if score > 0:
                case_result = case.copy()
                case_result['search_score'] = score
                results.append(case_result)
        
        # Sort by score
        results.sort(key=lambda x: x['search_score'], reverse=True)
        return results[:20]  # Top 20 results

    async def _search_code(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search through code knowledge"""
        query_lower = query.lower()
        results = []
        
        for code in self.knowledge_store['code']:
            score = 0
            
            # File path match
            if query_lower in code.get('file_path', '').lower():
                score += 2
            
            # Function name match
            for func in code.get('functions', []):
                if query_lower in func.lower():
                    score += 3
            
            # Error pattern match
            for pattern in code.get('error_patterns', []):
                if query_lower in pattern.lower():
                    score += 4
            
            # Service match
            for service in code.get('related_services', []):
                if query_lower in service.lower():
                    score += 3
            
            if score > 0:
                code_result = code.copy()
                code_result['search_score'] = score
                results.append(code_result)
        
        results.sort(key=lambda x: x['search_score'], reverse=True)
        return results[:10]

    async def _search_documentation(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search through documentation"""
        query_lower = query.lower()
        results = []
        
        for doc in self.knowledge_store['documentation']:
            score = 0
            
            # Title match
            if query_lower in doc.get('title', '').lower():
                score += 3
            
            # Content match
            if query_lower in doc.get('content', '').lower():
                score += 1
            
            # Heading match
            for heading in doc.get('headings', []):
                if query_lower in heading.lower():
                    score += 2
            
            # Service match
            for service in doc.get('related_services', []):
                if query_lower in service.lower():
                    score += 3
            
            if score > 0:
                doc_result = doc.copy()
                doc_result['search_score'] = score
                results.append(doc_result)
        
        results.sort(key=lambda x: x['search_score'], reverse=True)
        return results[:10]

    async def _search_history(self, query: str, current_session_id: str) -> List[Dict]:
        """Search through historical searches"""
        query_lower = query.lower()
        results = []
        
        # Get recent searches from other sessions
        recent_searches = [
            s for s in self.knowledge_store['search_history']
            if s['session_id'] != current_session_id
            and datetime.fromisoformat(s['timestamp']) > (datetime.now() - timedelta(days=30))
        ]
        
        for search in recent_searches:
            if query_lower in search['query'].lower():
                results.append(search)
        
        return results[:5]

    async def find_similar_cases(self, case: Dict) -> List[Dict]:
        """Find cases similar to the given case"""
        similar_cases = []
        
        for other_case in self.knowledge_store['cases']:
            if other_case['id'] == case.get('id'):
                continue
            
            similarity_score = 0
            
            # Service overlap
            common_services = set(case.get('affected_services', [])) & set(other_case.get('affected_services', []))
            similarity_score += len(common_services) * 2
            
            # Symptom overlap
            common_symptoms = set(case.get('symptoms', [])) & set(other_case.get('symptoms', []))
            similarity_score += len(common_symptoms) * 3
            
            # Severity match
            if case.get('severity') == other_case.get('severity'):
                similarity_score += 1
            
            if similarity_score > 2:
                other_case_copy = other_case.copy()
                other_case_copy['similarity_score'] = similarity_score
                similar_cases.append(other_case_copy)
        
        similar_cases.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar_cases[:5]

    def _generate_case_suggestions(self, case: Dict, similar_cases: List[Dict]) -> List[str]:
        """Generate suggestions for a new case based on similar cases"""
        suggestions = []
        
        if similar_cases:
            suggestions.append(f"Found {len(similar_cases)} similar cases that might be relevant")
            
            # Suggest common resolution patterns
            resolution_patterns = {}
            for sim_case in similar_cases:
                for step in sim_case.get('resolution_steps', []):
                    resolution_patterns[step] = resolution_patterns.get(step, 0) + 1
            
            common_resolutions = sorted(resolution_patterns.items(), key=lambda x: x[1], reverse=True)
            if common_resolutions:
                suggestions.append(f"Common resolution: {common_resolutions[0][0]}")
        
        # Service-specific suggestions
        for service in case.get('affected_services', []):
            if service == 'topology-merge':
                suggestions.append("Check topology-merge service logs and timeout configurations")
            elif service == 'kafka':
                suggestions.append("Verify Kafka cluster health and consumer lag")
        
        return suggestions

    async def _generate_search_suggestions(self, query: str, search_results: Dict) -> List[str]:
        """Generate search suggestions based on results"""
        suggestions = []
        
        # Suggest related searches based on found services
        services_found = set()
        for case in search_results['case_results']:
            services_found.update(case.get('affected_services', []))
        
        for service in services_found:
            if service.lower() not in query.lower():
                suggestions.append(f"Also search: {service} related issues")
        
        # Suggest expanding search if few results
        if search_results['total_results'] < 3:
            suggestions.append("Try broader search terms or check spelling")
        
        return suggestions[:3]

    async def _calculate_diagnostic_confidence(self, query: str, search_results: Dict) -> float:
        """Calculate diagnostic confidence based on search results"""
        if search_results['total_results'] == 0:
            return 0.0
        
        confidence = 0.0
        
        # High confidence if exact service matches found
        for case in search_results['case_results'][:3]:
            if case.get('confidence', 0) > 0.8:
                confidence += 0.3
        
        # Medium confidence if multiple results
        if search_results['total_results'] > 5:
            confidence += 0.2
        
        # Add confidence for code and doc matches
        if search_results['code_results']:
            confidence += 0.1
        if search_results['doc_results']:
            confidence += 0.1
        
        return min(1.0, confidence)


class LearningEngine:
    """Engine for learning from user interactions and feedback"""
    
    async def process_feedback(self, feedback: Dict):
        """Process user feedback to improve recommendations"""
        # This would implement ML-based learning
        # For now, we'll use simple heuristics
        pass
    
    async def generate_insights(self, knowledge_store: Dict) -> Dict[str, Any]:
        """Generate learning insights from the knowledge store"""
        
        insights = {
            'most_effective_sources': [],
            'common_search_patterns': [],
            'average_resolution_time': 0.0,
            'success_rate_by_source': {},
            'knowledge_gaps': [],
            'trending_issues': []
        }
        
        # Analyze search patterns
        search_history = knowledge_store['search_history']
        if search_history:
            # Find common search terms
            search_terms = {}
            for search in search_history[-100:]:  # Last 100 searches
                query_words = search['query'].lower().split()
                for word in query_words:
                    if len(word) > 3:  # Ignore short words
                        search_terms[word] = search_terms.get(word, 0) + 1
            
            common_terms = sorted(search_terms.items(), key=lambda x: x[1], reverse=True)
            insights['common_search_patterns'] = [term for term, count in common_terms[:10]]
        
        # Analyze knowledge source effectiveness
        feedback_data = knowledge_store['feedback']
        if feedback_data:
            source_ratings = {}
            for fb in feedback_data:
                source = fb['item_type']
                rating = fb.get('rating', 3)
                if source not in source_ratings:
                    source_ratings[source] = []
                source_ratings[source].append(rating)
            
            for source, ratings in source_ratings.items():
                avg_rating = sum(ratings) / len(ratings)
                insights['success_rate_by_source'][source] = avg_rating
        
        # Identify trending issues
        recent_cases = [
            case for case in knowledge_store['cases']
            if datetime.fromisoformat(case['created_date']) > (datetime.now() - timedelta(days=7))
        ]
        
        if recent_cases:
            service_counts = {}
            for case in recent_cases:
                for service in case.get('affected_services', []):
                    service_counts[service] = service_counts.get(service, 0) + 1
            
            trending = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)
            insights['trending_issues'] = [f"{service} ({count} cases)" for service, count in trending[:5]]
        
        return insights
