"""
Enhanced Multi-Source Knowledge Platform - Backend API
Supports cases, code, documentation, and learning capabilities
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
import json
from datetime import datetime

# Try to import our enhanced manager, fallback to basic if dependencies missing
try:
    from multi_source_manager import MultiSourceKnowledgeManager
    ENHANCED_MODE = True
except ImportError:
    ENHANCED_MODE = False
    print("Enhanced mode unavailable - using basic mode")

# Initialize FastAPI app
app = FastAPI(
    title="IBM AIOps Multi-Source Knowledge Platform", 
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

# Initialize knowledge manager
if ENHANCED_MODE:
    knowledge_manager = MultiSourceKnowledgeManager()
else:
    # Fallback to simple in-memory storage
    knowledge_store = {
        'cases': [],
        'code': [],
        'documentation': [],
        'search_history': [],
        'diagnostic_sessions': []
    }

# Request/Response Models
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
    search_mode: str = "all"  # all, cases, code, docs, history
    filters: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class FeedbackRequest(BaseModel):
    session_id: str
    item_id: str
    item_type: str
    feedback_type: str
    rating: Optional[int] = None
    comments: Optional[str] = None

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "enhanced_mode": ENHANCED_MODE
    }

# Case Management Endpoints
@app.post("/api/cases/add-manual")
async def add_manual_case(request: CaseEntryRequest):
    """Add a manually entered case with smart extraction"""
    
    if ENHANCED_MODE:
        try:
            user_metadata = {}
            if request.title:
                user_metadata['title'] = request.title
            if request.severity:
                user_metadata['severity'] = request.severity
            if request.affected_services:
                user_metadata['affected_services'] = request.affected_services
            if request.tags:
                user_metadata['tags'] = request.tags
            
            result = await knowledge_manager.add_manual_case(
                request.raw_content, 
                user_metadata
            )
            return {
                "status": "success",
                "case": result['case'],
                "similar_cases": result['similar_cases'],
                "suggestions": result['suggestions']
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing case: {str(e)}")
    else:
        # Fallback mode - basic case creation
        case = {
            'id': str(uuid.uuid4()),
            'title': request.title or "Manual Case Entry",
            'description': request.raw_content[:500],
            'raw_content': request.raw_content,
            'affected_services': request.affected_services or [],
            'severity': request.severity or "Medium",
            'tags': request.tags or [],
            'created_date': datetime.now().isoformat(),
            'manual_entry': True,
            'confidence': 0.7
        }
        knowledge_store['cases'].append(case)
        
        return {
            "status": "success",
            "case": case,
            "similar_cases": [],
            "suggestions": ["Case added successfully in basic mode"]
        }

@app.get("/api/cases")
async def get_all_cases():
    """Get all cases"""
    if ENHANCED_MODE:
        return knowledge_manager.knowledge_store['cases']
    else:
        return knowledge_store['cases']

@app.get("/api/cases/{case_id}")
async def get_case(case_id: str):
    """Get specific case by ID"""
    if ENHANCED_MODE:
        cases = knowledge_manager.knowledge_store['cases']
    else:
        cases = knowledge_store['cases']
    
    case = next((c for c in cases if c['id'] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return case

# Code Knowledge Endpoints
@app.post("/api/code/add")
async def add_code_knowledge(request: CodeEntryRequest):
    """Add code knowledge from GitHub or other sources"""
    
    if ENHANCED_MODE:
        try:
            commit_info = {}
            if request.commit_hash:
                commit_info['hash'] = request.commit_hash
            if request.commit_message:
                commit_info['message'] = request.commit_message
            
            result = await knowledge_manager.add_code_knowledge(
                request.repository,
                request.file_path,
                request.code_content,
                commit_info
            )
            return {"status": "success", "code_entry": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing code: {str(e)}")
    else:
        # Fallback mode
        code_entry = {
            'id': str(uuid.uuid4()),
            'repository': request.repository,
            'file_path': request.file_path,
            'code_content': request.code_content,
            'created_date': datetime.now().isoformat()
        }
        knowledge_store['code'].append(code_entry)
        return {"status": "success", "code_entry": code_entry}

@app.get("/api/code")
async def get_code_knowledge():
    """Get all code knowledge entries"""
    if ENHANCED_MODE:
        return knowledge_manager.knowledge_store['code']
    else:
        return knowledge_store['code']

# Documentation Endpoints
@app.post("/api/docs/add")
async def add_documentation(request: DocumentationEntryRequest):
    """Add documentation knowledge"""
    
    if ENHANCED_MODE:
        try:
            result = await knowledge_manager.add_documentation(
                request.title,
                request.content,
                request.source_url,
                request.doc_type
            )
            return {"status": "success", "doc_entry": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing documentation: {str(e)}")
    else:
        # Fallback mode
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
    """Get all documentation entries"""
    if ENHANCED_MODE:
        return knowledge_manager.knowledge_store['documentation']
    else:
        return knowledge_store['documentation']

# Unified Search
@app.post("/api/search")
async def unified_search(request: UnifiedSearchRequest):
    """Search across all knowledge sources"""
    
    if ENHANCED_MODE:
        try:
            results = await knowledge_manager.unified_search(
                request.query,
                request.search_mode,
                request.session_id,
                request.filters
            )
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
    else:
        # Fallback simple search
        query_lower = request.query.lower()
        results = {
            'query': request.query,
            'total_results': 0,
            'case_results': [],
            'code_results': [],
            'doc_results': [],
            'suggestions': []
        }
        
        # Simple case search
        if request.search_mode in ['all', 'cases']:
            case_results = [
                case for case in knowledge_store['cases']
                if query_lower in case.get('title', '').lower() or 
                   query_lower in case.get('description', '').lower()
            ]
            results['case_results'] = case_results
            results['total_results'] += len(case_results)
        
        return results

# Diagnostic Sessions
@app.post("/api/sessions/start")
async def start_diagnostic_session(query: str, user_id: Optional[str] = None):
    """Start a new diagnostic session"""
    
    if ENHANCED_MODE:
        session_id = await knowledge_manager.start_diagnostic_session(query, user_id)
    else:
        session_id = str(uuid.uuid4())
        session = {
            'id': session_id,
            'initial_query': query,
            'user_id': user_id,
            'created_date': datetime.now().isoformat(),
            'status': 'active'
        }
        knowledge_store['diagnostic_sessions'].append(session)
    
    return {"session_id": session_id, "status": "started"}

@app.post("/api/sessions/{session_id}/interaction")
async def track_interaction(session_id: str, interaction_type: str, 
                          content: Dict, effectiveness: Optional[int] = None):
    """Track user interaction during diagnostic session"""
    
    if ENHANCED_MODE:
        await knowledge_manager.track_interaction(
            session_id, interaction_type, content, effectiveness
        )
    
    return {"status": "tracked"}

@app.post("/api/feedback")
async def record_feedback(request: FeedbackRequest):
    """Record user feedback on knowledge items"""
    
    if ENHANCED_MODE:
        await knowledge_manager.record_feedback(
            request.session_id,
            request.item_id,
            request.item_type,
            request.feedback_type,
            request.rating,
            request.comments
        )
    
    return {"status": "feedback_recorded"}

# Learning and Analytics
@app.get("/api/insights")
async def get_learning_insights():
    """Get insights from the learning engine"""
    
    if ENHANCED_MODE:
        try:
            insights = await knowledge_manager.get_learning_insights()
            return insights
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")
    else:
        # Basic insights
        return {
            'most_effective_sources': [],
            'common_search_patterns': [],
            'total_cases': len(knowledge_store['cases']),
            'total_code_entries': len(knowledge_store['code']),
            'total_docs': len(knowledge_store['documentation'])
        }

# Legacy compatibility endpoint
@app.post("/query")
async def legacy_query(request: Dict[str, str]):
    """Legacy query endpoint for backward compatibility"""
    
    query = request.get('query', '')
    
    if ENHANCED_MODE:
        results = await knowledge_manager.unified_search(query, "all")
        
        # Format as legacy response
        if results['case_results']:
            top_case = results['case_results'][0]
            return {
                "hypothesis": f"Based on similar cases, this appears to be related to {', '.join(top_case.get('affected_services', ['unknown service']))}",
                "confidence": results['diagnostic_confidence'],
                "similar_cases": len(results['case_results']),
                "suggested_actions": results['suggestions'],
                "next_steps": ["Review similar cases", "Check service health", "Verify configurations"]
            }
    
    # Fallback response
    return {
        "hypothesis": "Pattern matching suggests this may be a service connectivity issue",
        "confidence": 0.75,
        "similar_cases": 0,
        "suggested_actions": ["Check service logs", "Verify network connectivity"],
        "next_steps": ["Investigate further", "Contact service owner"]
    }

@app.post("/load-sample-data")
async def load_sample_data():
    """Load sample data for testing"""
    
    sample_cases = [
        {
            'id': str(uuid.uuid4()),
            'title': 'Topology-merge service timeout issues',
            'description': 'Service experiencing 30-second timeouts during peak hours',
            'affected_services': ['topology-merge'],
            'symptoms': ['timeout', 'slow response'],
            'severity': 'High',
            'resolution_status': 'Resolved',
            'tags': ['performance', 'timeout'],
            'confidence': 0.9,
            'created_date': datetime.now().isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Kafka consumer lag increasing',
            'description': 'Consumer lag increasing rapidly on topic user-events',
            'affected_services': ['kafka'],
            'symptoms': ['high latency', 'consumer lag'],
            'severity': 'Medium',
            'resolution_status': 'Open',
            'tags': ['kafka', 'performance'],
            'confidence': 0.85,
            'created_date': datetime.now().isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Cassandra connection pool exhausted',
            'description': 'Database connection pool exhausted during data migration',
            'affected_services': ['cassandra'],
            'symptoms': ['connection refused', 'pool exhausted'],
            'severity': 'Critical',
            'resolution_status': 'In Progress',
            'tags': ['database', 'connections'],
            'confidence': 0.95,
            'created_date': datetime.now().isoformat()
        }
    ]
    
    if ENHANCED_MODE:
        knowledge_manager.knowledge_store['cases'].extend(sample_cases)
    else:
        knowledge_store['cases'].extend(sample_cases)
    
    return {
        "status": "success",
        "message": f"Loaded {len(sample_cases)} sample cases",
        "total_cases": len(knowledge_store['cases'] if not ENHANCED_MODE else knowledge_manager.knowledge_store['cases'])
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting IBM AIOps Multi-Source Knowledge Platform...")
    print(f"Enhanced mode: {ENHANCED_MODE}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
