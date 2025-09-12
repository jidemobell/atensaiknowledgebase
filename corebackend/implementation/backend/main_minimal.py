"""
Minimal FastAPI Backend for testing - without AI dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
import json
from datetime import datetime
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="IBM AIOps Multi-Source Knowledge Platform (Minimal)", 
    version="2.0.0",
    description="Enhanced knowledge platform supporting cases, code, docs, and learning"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for testing
knowledge_store = {
    'cases': [],
    'code': [],
    'documentation': [],
    'search_history': [],
    'diagnostic_sessions': [],
    'feedback': []
}

# Simple knowledge extraction for manual cases
def extract_case_metadata(raw_content):
    """Basic metadata extraction from raw content"""
    import re
    
    # Detect services
    service_patterns = {
        'topology-merge': r'topology[-_]?merge|topology merge',
        'kafka': r'\bkafka\b',
        'cassandra': r'\bcassandra\b',
        'elasticsearch': r'elasticsearch|elastic search',
        'redis': r'\bredis\b'
    }
    
    detected_services = []
    content_lower = raw_content.lower()
    for service, pattern in service_patterns.items():
        if re.search(pattern, content_lower, re.IGNORECASE):
            detected_services.append(service)
    
    # Extract title (first meaningful line)
    lines = raw_content.split('\n')
    title = "Manual Case Entry"
    for line in lines[:5]:
        if len(line.strip()) > 10 and not line.strip().startswith(('From:', 'To:', 'Date:')):
            title = line.strip()[:80]
            break
    
    # Detect severity
    severity = "Medium"
    if any(word in content_lower for word in ['critical', 'urgent', 'sev 1', 'priority 1']):
        severity = "Critical"
    elif any(word in content_lower for word in ['high', 'sev 2', 'priority 2']):
        severity = "High"
    
    # Extract symptoms
    symptoms = []
    if 'timeout' in content_lower:
        symptoms.append('timeout')
    if 'slow' in content_lower or 'performance' in content_lower:
        symptoms.append('performance issue')
    if 'error' in content_lower or 'exception' in content_lower:
        symptoms.append('error')
    
    return {
        'title': title,
        'severity': severity,
        'affected_services': detected_services,
        'symptoms': symptoms,
        'confidence': 0.7 if detected_services else 0.5
    }
knowledge_base = {"cases": [], "sessions": {}}

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    session_id: str
    hypotheses: List[Dict[str, Any]]
    similar_cases: List[Dict[str, Any]]
    confidence: float
    analysis: str

class CaseData(BaseModel):
    id: str
    title: str
    description: str
    affected_services: List[str]
    symptoms: List[str]
    resolution_steps: List[str]
    confidence: Optional[float] = 0.8

# Load knowledge base from file if exists
def load_knowledge_base():
    kb_path = Path("../knowledge_base.json")
    if kb_path.exists():
        try:
            with open(kb_path, 'r') as f:
                data = json.load(f)
                knowledge_base.update(data)
                print(f"Loaded {len(knowledge_base.get('cases', []))} cases from knowledge base")
        except Exception as e:
            print(f"Error loading knowledge base: {e}")

# Simple pattern matching function
def find_similar_cases(query: str) -> List[Dict[str, Any]]:
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    scored_cases = []
    
    for case in knowledge_base.get('cases', []):
        # Create searchable text
        searchable_text = ' '.join([
            case.get('title', ''),
            case.get('description', ''),
            ' '.join(case.get('symptoms', [])),
            ' '.join(case.get('affected_services', []))
        ]).lower()
        
        # Calculate simple similarity score
        case_words = set(searchable_text.split())
        common_words = query_words.intersection(case_words)
        
        if common_words:
            similarity = len(common_words) / len(query_words.union(case_words))
            if similarity > 0.1:  # Minimum threshold
                scored_cases.append((similarity, case))
    
    # Sort by similarity and return top 3
    scored_cases.sort(key=lambda x: x[0], reverse=True)
    return [case for score, case in scored_cases[:3]]

# Simple service detection
def detect_services(text: str) -> List[str]:
    text_lower = text.lower()
    services = []
    
    service_patterns = {
        'topology-merge': ['topology-merge', 'topology merge', 'merge service'],
        'topology-inventory': ['topology-inventory', 'inventory service'],
        'topology-status': ['topology-status', 'status service'],
        'kafka': ['kafka', 'message queue', 'consumer lag'],
        'cassandra': ['cassandra', 'database', 'cql'],
        'redis': ['redis', 'cache'],
        'observer': ['observer', 'kubernetes-observer', 'servicenow-observer']
    }
    
    for service, patterns in service_patterns.items():
        if any(pattern in text_lower for pattern in patterns):
            services.append(service)
    
    return list(set(services))

# Generate simple hypotheses
def generate_hypotheses(query: str, services: List[str], similar_cases: List[Dict]) -> List[Dict[str, Any]]:
    hypotheses = []
    
    # Service-based hypotheses
    if 'kafka' in services:
        hypotheses.append({
            'category': 'messaging',
            'description': 'Potential Kafka messaging issue',
            'confidence': 0.8,
            'next_steps': ['Check Kafka consumer lag', 'Verify broker connectivity']
        })
    
    if 'cassandra' in services:
        hypotheses.append({
            'category': 'database', 
            'description': 'Potential Cassandra database issue',
            'confidence': 0.8,
            'next_steps': ['Check cluster health', 'Monitor query performance']
        })
    
    if any(svc.startswith('topology') for svc in services):
        hypotheses.append({
            'category': 'topology',
            'description': 'Topology service issue',
            'confidence': 0.85,
            'next_steps': ['Check service logs', 'Verify data sources']
        })
    
    # Symptom-based hypotheses
    if any(word in query.lower() for word in ['timeout', 'slow', 'lag']):
        hypotheses.append({
            'category': 'performance',
            'description': 'Performance degradation',
            'confidence': 0.75,
            'next_steps': ['Check resource usage', 'Monitor network latency']
        })
    
    return hypotheses

# Main diagnostic endpoint
@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query and return diagnostic insights"""
    
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Detect services
        services = detect_services(request.query)
        
        # Find similar cases
        similar_cases = find_similar_cases(request.query)
        
        # Generate hypotheses
        hypotheses = generate_hypotheses(request.query, services, similar_cases)
        
        # Calculate confidence
        base_confidence = 0.4
        if services:
            base_confidence += 0.2
        if similar_cases:
            base_confidence += 0.2
        if hypotheses:
            base_confidence += 0.1
        
        confidence = min(0.95, base_confidence)
        
        # Generate response
        if hypotheses:
            top_hypothesis = max(hypotheses, key=lambda h: h.get('confidence', 0))
            response_text = f"Based on the symptoms described, I have {confidence:.0%} confidence this is related to: {top_hypothesis['description']}\n\n"
            
            if top_hypothesis.get('next_steps'):
                response_text += "**Suggested next steps:**\n"
                for i, step in enumerate(top_hypothesis['next_steps'][:3], 1):
                    response_text += f"{i}. {step}\n"
            
            if similar_cases:
                response_text += f"\n**Similar cases found:** {len(similar_cases)} historical cases match this pattern"
        else:
            response_text = "I need more information to diagnose this issue. Can you provide more details about the symptoms or error messages?"
        
        # Store session info
        knowledge_base['sessions'][session_id] = {
            'last_query': request.query,
            'timestamp': datetime.now().isoformat()
        }
        
        return QueryResponse(
            response=response_text,
            session_id=session_id,
            hypotheses=hypotheses,
            similar_cases=similar_cases,
            confidence=confidence,
            analysis=f"Detected {len(services)} services, found {len(similar_cases)} similar cases"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Health check
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# System status
@app.get("/status")
async def get_system_status():
    """Get system status"""
    return {
        "api_version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "knowledge_base_cases": len(knowledge_base.get('cases', [])),
        "active_sessions": len(knowledge_base.get('sessions', {})),
        "features": {
            "pattern_matching": True,
            "semantic_search": False,  # Disabled for minimal version
            "document_processing": False,  # Disabled for minimal version
            "session_management": True
        }
    }

# Load sample data
@app.post("/load-sample-data")
async def load_sample_data():
    """Load sample data for testing"""
    
    sample_cases = [
        {
            'id': str(uuid.uuid4()),
            'title': 'Topology-merge service timeout issues',
            'description': 'Service experiencing 30-second timeouts during peak hours affecting user experience',
            'affected_services': ['topology-merge'],
            'symptoms': ['timeout', 'slow response'],
            'severity': 'High',
            'resolution_status': 'Resolved',
            'tags': ['performance', 'timeout'],
            'confidence': 0.9,
            'created_date': datetime.now().isoformat(),
            'manual_entry': True
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Kafka consumer lag increasing rapidly',
            'description': 'Consumer lag increasing rapidly on topic user-events, causing data processing delays',
            'affected_services': ['kafka'],
            'symptoms': ['high latency', 'consumer lag'],
            'severity': 'Medium',
            'resolution_status': 'Open',
            'tags': ['kafka', 'performance'],
            'confidence': 0.85,
            'created_date': datetime.now().isoformat(),
            'manual_entry': True
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Cassandra connection pool exhausted',
            'description': 'Database connection pool exhausted during data migration causing application errors',
            'affected_services': ['cassandra'],
            'symptoms': ['connection refused', 'pool exhausted'],
            'severity': 'Critical',
            'resolution_status': 'In Progress',
            'tags': ['database', 'connections'],
            'confidence': 0.95,
            'created_date': datetime.now().isoformat(),
            'manual_entry': True
        }
    ]
    
    knowledge_store['cases'].extend(sample_cases)
    
    return {
        "status": "success",
        "message": f"Loaded {len(sample_cases)} sample cases",
        "total_cases": len(knowledge_store['cases'])
    }

# Enhanced Multi-Source Endpoints

class CaseEntryRequest(BaseModel):
    raw_content: str
    title: Optional[str] = None
    severity: Optional[str] = None
    affected_services: Optional[List[str]] = None
    tags: Optional[List[str]] = None

class CodeEntryRequest(BaseModel):
    repository: str
    file_path: str
    code_content: str
    commit_hash: Optional[str] = None
    commit_message: Optional[str] = None

class DocumentationEntryRequest(BaseModel):
    title: str
    content: str
    source_url: Optional[str] = None
    doc_type: Optional[str] = None

class UnifiedSearchRequest(BaseModel):
    query: str
    search_mode: str = "all"
    filters: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

@app.post("/api/cases/add-manual")
async def add_manual_case(request: CaseEntryRequest):
    """Add a manually entered case with smart extraction"""
    
    # Extract metadata from raw content
    extracted = extract_case_metadata(request.raw_content)
    
    # Apply user overrides
    if request.title:
        extracted['title'] = request.title
    if request.severity:
        extracted['severity'] = request.severity
    if request.affected_services:
        extracted['affected_services'] = request.affected_services
    if request.tags:
        extracted['tags'] = request.tags
    
    # Create case
    case = {
        'id': str(uuid.uuid4()),
        'title': extracted['title'],
        'description': request.raw_content[:500] + '...' if len(request.raw_content) > 500 else request.raw_content,
        'raw_content': request.raw_content,
        'affected_services': extracted['affected_services'],
        'symptoms': extracted['symptoms'],
        'severity': extracted['severity'],
        'tags': extracted.get('tags', []),
        'confidence': extracted['confidence'],
        'manual_entry': True,
        'created_date': datetime.now().isoformat(),
        'resolution_status': 'Open'
    }
    
    knowledge_store['cases'].append(case)
    
    # Find similar cases
    similar_cases = []
    for other_case in knowledge_store['cases']:
        if other_case['id'] == case['id']:
            continue
        
        # Simple similarity based on services
        common_services = set(case['affected_services']) & set(other_case.get('affected_services', []))
        if common_services:
            similar_cases.append({
                **other_case,
                'similarity_score': len(common_services) * 2
            })
    
    similar_cases.sort(key=lambda x: x['similarity_score'], reverse=True)
    similar_cases = similar_cases[:3]  # Top 3
    
    # Generate suggestions
    suggestions = []
    if similar_cases:
        suggestions.append(f"Found {len(similar_cases)} similar cases")
    
    for service in case['affected_services']:
        if service == 'topology-merge':
            suggestions.append("Check topology-merge service logs and timeout configurations")
        elif service == 'kafka':
            suggestions.append("Verify Kafka cluster health and consumer lag")
    
    return {
        "status": "success",
        "case": case,
        "similar_cases": similar_cases,
        "suggestions": suggestions
    }

@app.post("/api/code/add")
async def add_code_knowledge(request: CodeEntryRequest):
    """Add code knowledge"""
    
    code_entry = {
        'id': str(uuid.uuid4()),
        'repository': request.repository,
        'file_path': request.file_path,
        'code_content': request.code_content,
        'commit_hash': request.commit_hash,
        'commit_message': request.commit_message,
        'created_date': datetime.now().isoformat(),
        'tags': [f"repo:{request.repository}"]
    }
    
    knowledge_store['code'].append(code_entry)
    return {"status": "success", "code_entry": code_entry}

@app.get("/api/code")
async def get_code_knowledge():
    """Get all code knowledge"""
    return knowledge_store['code']

@app.post("/api/docs/add")
async def add_documentation(request: DocumentationEntryRequest):
    """Add documentation"""
    
    doc_entry = {
        'id': str(uuid.uuid4()),
        'title': request.title,
        'content': request.content,
        'source_url': request.source_url,
        'doc_type': request.doc_type or 'documentation',
        'created_date': datetime.now().isoformat()
    }
    
    knowledge_store['documentation'].append(doc_entry)
    return {"status": "success", "doc_entry": doc_entry}

@app.get("/api/docs")
async def get_documentation():
    """Get all documentation"""
    return knowledge_store['documentation']

@app.post("/api/search")
async def unified_search(request: UnifiedSearchRequest):
    """Unified search across all knowledge sources"""
    
    query_lower = request.query.lower()
    results = {
        'query': request.query,
        'session_id': request.session_id or str(uuid.uuid4()),
        'total_results': 0,
        'case_results': [],
        'code_results': [],
        'doc_results': [],
        'historical_searches': [],
        'suggestions': [],
        'diagnostic_confidence': 0.0
    }
    
    # Search cases
    if request.search_mode in ['all', 'cases']:
        for case in knowledge_store['cases']:
            score = 0
            if query_lower in case.get('title', '').lower():
                score += 3
            if query_lower in case.get('description', '').lower():
                score += 2
            for service in case.get('affected_services', []):
                if query_lower in service.lower():
                    score += 4
            
            if score > 0:
                case_result = case.copy()
                case_result['search_score'] = score
                results['case_results'].append(case_result)
        
        results['case_results'].sort(key=lambda x: x['search_score'], reverse=True)
        results['total_results'] += len(results['case_results'])
    
    # Search code
    if request.search_mode in ['all', 'code']:
        for code in knowledge_store['code']:
            score = 0
            if query_lower in code.get('file_path', '').lower():
                score += 2
            if query_lower in code.get('code_content', '').lower():
                score += 1
            
            if score > 0:
                code_result = code.copy()
                code_result['search_score'] = score
                results['code_results'].append(code_result)
        
        results['code_results'].sort(key=lambda x: x['search_score'], reverse=True)
        results['total_results'] += len(results['code_results'])
    
    # Search documentation
    if request.search_mode in ['all', 'docs']:
        for doc in knowledge_store['documentation']:
            score = 0
            if query_lower in doc.get('title', '').lower():
                score += 3
            if query_lower in doc.get('content', '').lower():
                score += 1
            
            if score > 0:
                doc_result = doc.copy()
                doc_result['search_score'] = score
                results['doc_results'].append(doc_result)
        
        results['doc_results'].sort(key=lambda x: x['search_score'], reverse=True)
        results['total_results'] += len(results['doc_results'])
    
    # Calculate diagnostic confidence
    if results['total_results'] > 0:
        if results['case_results'] and any(c.get('confidence', 0) > 0.8 for c in results['case_results'][:3]):
            results['diagnostic_confidence'] = 0.8
        elif results['total_results'] > 3:
            results['diagnostic_confidence'] = 0.6
        else:
            results['diagnostic_confidence'] = 0.4
    
    # Generate suggestions
    if results['case_results']:
        results['suggestions'].append("Found relevant cases - review similar issues")
    if results['code_results']:
        results['suggestions'].append("Check related code for implementation details")
    if results['total_results'] == 0:
        results['suggestions'].append("Try broader search terms or check spelling")
    
    # Record search
    search_record = {
        'query': request.query,
        'timestamp': datetime.now().isoformat(),
        'results_count': results['total_results'],
        'session_id': results['session_id']
    }
    knowledge_store['search_history'].append(search_record)
    
    return results

@app.post("/api/sessions/start")
async def start_diagnostic_session(query: str = "", user_id: Optional[str] = None):
    """Start diagnostic session"""
    
    session_id = str(uuid.uuid4())
    session = {
        'id': session_id,
        'initial_query': query,
        'user_id': user_id,
        'created_date': datetime.now().isoformat(),
        'interactions': []
    }
    knowledge_store['diagnostic_sessions'].append(session)
    
    return {"session_id": session_id, "status": "started"}

@app.post("/api/sessions/{session_id}/interaction")
async def track_interaction(session_id: str, interaction_type: str, content: Dict, effectiveness: Optional[int] = None):
    """Track interaction"""
    
    interaction = {
        'timestamp': datetime.now().isoformat(),
        'type': interaction_type,
        'content': content,
        'effectiveness': effectiveness
    }
    
    # Find and update session
    for session in knowledge_store['diagnostic_sessions']:
        if session['id'] == session_id:
            session['interactions'].append(interaction)
            break
    
    return {"status": "tracked"}

@app.post("/api/feedback")
async def record_feedback(session_id: str, item_id: str, item_type: str, feedback_type: str, rating: Optional[int] = None, comments: Optional[str] = None):
    """Record feedback"""
    
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
    
    knowledge_store['feedback'].append(feedback)
    return {"status": "feedback_recorded"}

@app.get("/api/insights")
async def get_learning_insights():
    """Get learning insights"""
    
    total_cases = len(knowledge_store['cases'])
    total_searches = len(knowledge_store['search_history'])
    recent_searches = [s for s in knowledge_store['search_history'][-20:]]
    
    # Common search terms
    search_terms = {}
    for search in recent_searches:
        words = search['query'].lower().split()
        for word in words:
            if len(word) > 3:
                search_terms[word] = search_terms.get(word, 0) + 1
    
    common_patterns = sorted(search_terms.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        'most_effective_sources': [
            {'source': 'cases', 'count': total_cases},
            {'source': 'code', 'count': len(knowledge_store['code'])},
            {'source': 'docs', 'count': len(knowledge_store['documentation'])}
        ],
        'common_search_patterns': [term for term, count in common_patterns],
        'total_searches': total_searches,
        'total_cases': total_cases,
        'trending_issues': ['topology-merge timeouts', 'kafka lag', 'connection issues']
    }

# List cases
@app.get("/cases/list")
async def list_cases():
    """List all cases in the knowledge base"""
    try:
        cases = knowledge_base.get('cases', [])
        return {
            "cases": cases,
            "count": len(cases)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing cases: {str(e)}")

# API endpoint for cases (what the frontend expects)
@app.get("/api/cases")
async def api_get_cases():
    """API endpoint to get all cases for frontend"""
    try:
        cases = knowledge_store.get('cases', [])
        return cases
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cases: {str(e)}")

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    """Load knowledge base on startup"""
    load_knowledge_base()
    print("🚀 Minimal AI-Powered Support System started")
    print("📍 API available at: http://localhost:8000")
    print("📖 Interactive docs at: http://localhost:8000/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
