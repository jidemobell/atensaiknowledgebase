"""
Enhanced Diagnostic Agent for IBM AIOps Knowledge System
Combines pattern matching with semantic search and document intelligence
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

# Try to import optional dependencies
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

from document_processor import DocumentProcessor
from vector_store import create_vector_store


class SessionState:
    """Represents session state for multi-turn conversations"""
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_case_context = {}
        self.hypotheses = []
        self.eliminated_causes = []
        self.conversation_history = []
        self.last_updated = datetime.now()
        self.confidence_threshold = 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'current_case_context': self.current_case_context,
            'hypotheses': self.hypotheses,
            'eliminated_causes': self.eliminated_causes,
            'conversation_history': self.conversation_history,
            'last_updated': self.last_updated.isoformat(),
            'confidence_threshold': self.confidence_threshold
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionState':
        session = cls(data['session_id'])
        session.current_case_context = data.get('current_case_context', {})
        session.hypotheses = data.get('hypotheses', [])
        session.eliminated_causes = data.get('eliminated_causes', [])
        session.conversation_history = data.get('conversation_history', [])
        session.confidence_threshold = data.get('confidence_threshold', 0.7)
        if 'last_updated' in data:
            session.last_updated = datetime.fromisoformat(data['last_updated'])
        return session


class EnhancedDiagnosticAgent:
    def __init__(self, knowledge_base_path: str = "knowledge_base.json"):
        """Initialize the enhanced diagnostic agent"""
        
        # Initialize embeddings if available
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                print("Loaded sentence transformer model")
            except Exception as e:
                print(f"Warning: Could not load embeddings: {e}")
                self.embedder = None
        else:
            self.embedder = None
            print("Warning: sentence-transformers not available")
        
        # Initialize components
        self.document_processor = DocumentProcessor()
        self.vector_store = create_vector_store()
        
        # Session management
        self.sessions = {}
        self.session_timeout = timedelta(hours=24)
        
        # Knowledge base
        self.knowledge_base_path = Path(knowledge_base_path)
        self.knowledge_base = self._load_knowledge_base()
        
        # Initialize vector store with existing cases
        self._initialize_vector_store()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load existing knowledge base"""
        try:
            if self.knowledge_base_path.exists():
                with open(self.knowledge_base_path, 'r') as f:
                    kb = json.load(f)
                print(f"Loaded knowledge base with {len(kb.get('cases', []))} cases")
                return kb
            else:
                print("No existing knowledge base found, creating new one")
                return {"cases": [], "version": "1.0", "created_at": datetime.now().isoformat()}
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return {"cases": [], "version": "1.0", "created_at": datetime.now().isoformat()}
    
    def _initialize_vector_store(self):
        """Initialize vector store with existing cases"""
        if not self.embedder:
            print("Skipping vector store initialization - no embeddings available")
            return
        
        try:
            # Process existing cases for vector store
            processed_docs = []
            for case in self.knowledge_base.get('cases', []):
                # Create a text representation of the case
                case_text = f"Title: {case.get('title', '')}\n"
                case_text += f"Description: {case.get('description', '')}\n"
                case_text += f"Services: {', '.join(case.get('affected_services', []))}\n"
                case_text += f"Resolution: {' '.join(case.get('resolution_steps', []))}"
                
                # Process the case
                processed_doc = self.document_processor.process_salesforce_case(
                    case_text, case.get('id', 'unknown')
                )
                processed_docs.append(processed_doc)
            
            if processed_docs:
                success = self.vector_store.add_documents(processed_docs)
                if success:
                    print(f"Initialized vector store with {len(processed_docs)} cases")
        except Exception as e:
            print(f"Error initializing vector store: {e}")
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get session state"""
        session = self.sessions.get(session_id)
        if session and (datetime.now() - session.last_updated) < self.session_timeout:
            return session
        elif session:
            # Session expired
            del self.sessions[session_id]
        return None
    
    def save_session(self, session: SessionState):
        """Save session state"""
        session.last_updated = datetime.now()
        self.sessions[session.session_id] = session
    
    def diagnose_issue(self, symptom: str, session_id: str) -> Dict[str, Any]:
        """Enhanced diagnosis using multiple intelligence sources"""
        
        # Get or create session
        session = self.get_session(session_id)
        if not session:
            session = SessionState(session_id)
        
        # Add to conversation history
        session.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "user_symptom",
            "content": symptom
        })
        
        # 1. Pattern-based analysis (your existing logic)
        pattern_analysis = self._pattern_based_analysis(symptom)
        
        # 2. Semantic search analysis
        semantic_analysis = self._semantic_analysis(symptom, pattern_analysis)
        
        # 3. Fuse results
        fused_result = self._fuse_analyses(pattern_analysis, semantic_analysis, symptom)
        
        # 4. Update session state
        session.current_case_context.update({
            'latest_symptom': symptom,
            'pattern_confidence': pattern_analysis.get('confidence', 0.0),
            'semantic_confidence': semantic_analysis.get('confidence', 0.0),
            'fused_confidence': fused_result.get('confidence', 0.0)
        })
        
        # Add response to conversation history
        session.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "agent_response",
            "content": fused_result.get('response', '')
        })
        
        # Save session
        self.save_session(session)
        
        return fused_result
    
    def _pattern_based_analysis(self, symptom: str) -> Dict[str, Any]:
        """Pattern-based diagnostic analysis (your existing logic)"""
        
        # Extract service indicators
        services = self._detect_services_from_symptom(symptom)
        
        # Find similar cases using keyword matching
        similar_cases = self._find_similar_cases_keyword(symptom)
        
        # Generate hypotheses based on patterns
        hypotheses = self._generate_pattern_hypotheses(symptom, services, similar_cases)
        
        # Calculate confidence
        confidence = self._calculate_pattern_confidence(symptom, hypotheses, similar_cases)
        
        # Generate response
        response = self._generate_pattern_response(symptom, hypotheses, similar_cases, confidence)
        
        return {
            'method': 'pattern_matching',
            'services': services,
            'similar_cases': similar_cases,
            'hypotheses': hypotheses,
            'confidence': confidence,
            'response': response,
            'analysis': f"Pattern analysis identified {len(services)} services and {len(similar_cases)} similar cases"
        }
    
    def _semantic_analysis(self, symptom: str, pattern_result: Dict) -> Dict[str, Any]:
        """Semantic search analysis"""
        if not self.embedder:
            return {
                'method': 'semantic_search',
                'similar_documents': [],
                'confidence': 0.0,
                'insights': 'Semantic search not available'
            }
        
        try:
            # Generate embedding for symptom
            symptom_embedding = self.embedder.encode(symptom).tolist()
            
            # Extract services from pattern analysis for filtering
            detected_services = pattern_result.get('services', [])
            
            # Search for similar documents
            similar_docs = self.vector_store.semantic_search(
                query_embedding=symptom_embedding,
                services=detected_services if detected_services else None,
                chunk_types=['resolution', 'error_description', 'general'],
                limit=5
            )
            
            # Extract insights
            insights = self._extract_semantic_insights(similar_docs)
            
            # Calculate semantic confidence
            confidence = self._calculate_semantic_confidence(similar_docs)
            
            return {
                'method': 'semantic_search',
                'similar_documents': similar_docs,
                'confidence': confidence,
                'insights': insights,
                'semantic_services': detected_services
            }
            
        except Exception as e:
            print(f"Error in semantic analysis: {e}")
            return {
                'method': 'semantic_search',
                'similar_documents': [],
                'confidence': 0.0,
                'insights': f'Semantic search error: {str(e)}'
            }
    
    def _fuse_analyses(self, pattern_result: Dict, semantic_result: Dict, original_symptom: str) -> Dict[str, Any]:
        """Intelligently fuse pattern matching and semantic search results"""
        # Use the original_symptom parameter
        _ = original_symptom
        
        # Start with pattern analysis as base
        fused_result = pattern_result.copy()
        
        # Enhance confidence if semantic search agrees
        semantic_confidence = semantic_result.get('confidence', 0.0)
        if semantic_confidence > 0.5:
            # Boost confidence when semantic search agrees
            boost = min(0.15, semantic_confidence * 0.2)
            fused_result['confidence'] = min(0.95, fused_result['confidence'] + boost)
        
        # Enhance analysis with semantic insights
        if semantic_result.get('similar_documents'):
            current_analysis = fused_result.get('analysis', '')
            semantic_insights = semantic_result.get('insights', '')
            enhanced_analysis = f"{current_analysis}\n\nDocument Analysis: {semantic_insights}"
            fused_result['analysis'] = enhanced_analysis
        
        # Add semantic documents to results
        fused_result['similar_documents'] = semantic_result.get('similar_documents', [])
        
        # Update response with semantic information
        if semantic_result.get('similar_documents'):
            current_response = fused_result.get('response', '')
            doc_count = len(semantic_result['similar_documents'])
            semantic_addition = f"\n\nI found {doc_count} relevant historical documents that may help with this issue."
            fused_result['response'] = current_response + semantic_addition
        
        # Add data source attribution
        fused_result['data_sources'] = {
            'pattern_matching': True,
            'semantic_search': len(semantic_result.get('similar_documents', [])) > 0,
            'knowledge_graph': len(fused_result.get('similar_cases', [])) > 0
        }
        
        # Add reasoning trace
        fused_result['reasoning_trace'] = {
            'pattern_confidence': pattern_result.get('confidence', 0.0),
            'semantic_confidence': semantic_confidence,
            'fusion_method': 'weighted_combination',
            'final_confidence': fused_result['confidence']
        }
        
        return fused_result
    
    def _detect_services_from_symptom(self, symptom: str) -> List[str]:
        """Detect affected services from symptom description"""
        return self.document_processor._detect_services(symptom)
    
    def _find_similar_cases_keyword(self, symptom: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Find similar cases using keyword matching"""
        symptom_lower = symptom.lower()
        symptom_words = set(symptom_lower.split())
        
        scored_cases = []
        
        for case in self.knowledge_base.get('cases', []):
            # Create searchable text
            searchable_text = ' '.join([
                case.get('title', ''),
                case.get('description', ''),
                ' '.join(case.get('symptoms', [])),
                ' '.join(case.get('affected_services', []))
            ]).lower()
            
            # Calculate simple similarity score
            case_words = set(searchable_text.split())
            common_words = symptom_words.intersection(case_words)
            
            if common_words:
                similarity = len(common_words) / len(symptom_words.union(case_words))
                scored_cases.append((similarity, case))
        
        # Sort by similarity and return top cases
        scored_cases.sort(key=lambda x: x[0], reverse=True)
        return [case for score, case in scored_cases[:limit] if score > 0.1]
    
    def _generate_pattern_hypotheses(self, symptom: str, services: List[str], similar_cases: List[Dict]) -> List[Dict[str, Any]]:
        """Generate diagnostic hypotheses based on patterns"""
        hypotheses = []
        
        # Service-based hypotheses
        if 'kafka' in services:
            hypotheses.append({
                'category': 'messaging',
                'description': 'Potential Kafka messaging issue',
                'confidence': 0.8,
                'evidence': ['kafka service mentioned'],
                'next_steps': ['Check Kafka consumer lag', 'Verify broker connectivity']
            })
        
        if 'cassandra' in services:
            hypotheses.append({
                'category': 'database',
                'description': 'Potential Cassandra database issue',
                'confidence': 0.8,
                'evidence': ['cassandra service mentioned'],
                'next_steps': ['Check cluster health', 'Monitor query performance']
            })
        
        if any(svc.startswith('topology') for svc in services):
            hypotheses.append({
                'category': 'topology',
                'description': 'Topology service issue',
                'confidence': 0.85,
                'evidence': ['topology service mentioned'],
                'next_steps': ['Check service logs', 'Verify data sources']
            })
        
        # Symptom-based hypotheses
        if any(word in symptom.lower() for word in ['timeout', 'slow', 'lag']):
            hypotheses.append({
                'category': 'performance',
                'description': 'Performance degradation',
                'confidence': 0.75,
                'evidence': ['performance keywords detected'],
                'next_steps': ['Check resource usage', 'Monitor network latency']
            })
        
        # Case-based hypotheses
        if similar_cases:
            for case in similar_cases[:2]:  # Top 2 similar cases
                hypotheses.append({
                    'category': 'historical',
                    'description': f"Similar to case: {case.get('title', 'Unknown')}",
                    'confidence': case.get('confidence', 0.5),
                    'evidence': [f"Matches case {case.get('id', 'unknown')}"],
                    'next_steps': case.get('resolution_steps', [])[:3]  # First 3 steps
                })
        
        return hypotheses
    
    def _calculate_pattern_confidence(self, symptom: str, hypotheses: List[Dict], similar_cases: List[Dict]) -> float:
        """Calculate confidence based on pattern analysis"""
        base_confidence = 0.4
        
        # Boost for multiple hypotheses
        if len(hypotheses) > 1:
            base_confidence += 0.2
        
        # Boost for similar cases
        if similar_cases:
            avg_case_confidence = sum(case.get('confidence', 0.5) for case in similar_cases) / len(similar_cases)
            base_confidence += avg_case_confidence * 0.3
        
        # Boost for specific keywords
        high_confidence_keywords = ['timeout', 'kafka', 'cassandra', 'topology-merge']
        keyword_matches = sum(1 for keyword in high_confidence_keywords if keyword in symptom.lower())
        base_confidence += keyword_matches * 0.1
        
        return min(0.95, base_confidence)
    
    def _generate_pattern_response(self, original_symptom: str, hypotheses: List[Dict], similar_cases: List[Dict], confidence: float) -> str:
        """Generate response based on pattern analysis"""
        # Use the original_symptom parameter
        _ = original_symptom
        
        if not hypotheses:
            return "I need more information to diagnose this issue. Can you provide more details about the symptoms or error messages?"
        
        # Get top hypothesis
        top_hypothesis = max(hypotheses, key=lambda h: h.get('confidence', 0))
        
        response = f"Based on the symptoms described, I have {confidence:.0%} confidence this is related to: {top_hypothesis['description']}\n\n"
        
        if top_hypothesis.get('next_steps'):
            response += "**Suggested next steps:**\n"
            for i, step in enumerate(top_hypothesis['next_steps'][:3], 1):
                response += f"{i}. {step}\n"
        
        if similar_cases:
            response += f"\n**Similar cases found:** {len(similar_cases)} historical cases match this pattern"
        
        return response
    
    def _extract_semantic_insights(self, similar_docs: List[Dict]) -> str:
        """Extract insights from semantically similar documents"""
        if not similar_docs:
            return "No similar historical documents found."
        
        # Group by case_id
        cases_mentioned = set()
        resolution_chunks = []
        error_chunks = []
        
        for doc in similar_docs:
            cases_mentioned.add(doc['case_id'])
            if doc['chunk_type'] == 'resolution':
                resolution_chunks.append(doc)
            elif doc['chunk_type'] == 'error_description':
                error_chunks.append(doc)
        
        insight = f"Found {len(cases_mentioned)} similar historical cases"
        
        if resolution_chunks:
            insight += f" with {len(resolution_chunks)} documented resolutions"
        
        if error_chunks:
            insight += f" and {len(error_chunks)} similar error patterns"
        
        # Add confidence information
        avg_score = sum(doc['score'] for doc in similar_docs) / len(similar_docs)
        insight += f". Average relevance: {avg_score:.2f}"
        
        return insight
    
    def _calculate_semantic_confidence(self, similar_docs: List[Dict]) -> float:
        """Calculate confidence based on semantic search results"""
        if not similar_docs:
            return 0.0
        
        # Consider both semantic similarity and document confidence
        total_score = 0
        total_confidence = 0
        
        for doc in similar_docs:
            total_score += doc['score']
            total_confidence += doc.get('confidence', 0.5)
        
        avg_score = total_score / len(similar_docs)
        avg_confidence = total_confidence / len(similar_docs)
        
        # Combine semantic similarity with document confidence
        return min(0.95, (avg_score * 0.6) + (avg_confidence * 0.4))
    
    def add_case_to_knowledge_base(self, case_data: Dict[str, Any]) -> bool:
        """Add a new case to the knowledge base"""
        try:
            # Add timestamp if not present
            if 'created_at' not in case_data:
                case_data['created_at'] = datetime.now().isoformat()
            
            # Add to knowledge base
            self.knowledge_base['cases'].append(case_data)
            
            # Save to file
            with open(self.knowledge_base_path, 'w') as f:
                json.dump(self.knowledge_base, f, indent=2)
            
            # Add to vector store if embeddings available
            if self.embedder:
                case_text = f"Title: {case_data.get('title', '')}\n"
                case_text += f"Description: {case_data.get('description', '')}\n"
                case_text += f"Services: {', '.join(case_data.get('affected_services', []))}\n"
                case_text += f"Resolution: {' '.join(case_data.get('resolution_steps', []))}"
                
                processed_doc = self.document_processor.process_salesforce_case(
                    case_text, case_data.get('id', 'unknown')
                )
                self.vector_store.add_documents([processed_doc])
            
            print(f"Added case {case_data.get('id', 'unknown')} to knowledge base")
            return True
            
        except Exception as e:
            print(f"Error adding case to knowledge base: {e}")
            return False
    
    def get_collection_status(self) -> Dict[str, Any]:
        """Get status of all components"""
        return {
            'embeddings_available': self.embedder is not None,
            'vector_store_status': self.vector_store.get_collection_info(),
            'knowledge_base_cases': len(self.knowledge_base.get('cases', [])),
            'active_sessions': len(self.sessions),
            'processor_available': self.document_processor is not None
        }
