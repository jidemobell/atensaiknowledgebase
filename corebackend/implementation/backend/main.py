"""
Enhanced FastAPI Backend for IBM AIOps Knowledge System
Combines intelligent diagnostics with document processing and semantic search
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
import json
from datetime import datetime

from enhanced_agent import EnhancedDiagnosticAgent

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced AI-Powered Support System", 
    version="2.0.0",
    description="Intelligent diagnostic system with document processing and semantic search"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the enhanced agent
agent = EnhancedDiagnosticAgent()

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    session_id: str
    hypotheses: List[Dict[str, Any]]
    similar_cases: List[Dict[str, Any]]
    similar_documents: List[Dict[str, Any]]
    confidence: float
    analysis: str
    data_sources: Dict[str, bool]
    reasoning_trace: Optional[Dict[str, Any]] = None

class CaseData(BaseModel):
    id: str
    title: str
    description: str
    affected_services: List[str]
    symptoms: List[str]
    resolution_steps: List[str]
    confidence: Optional[float] = 0.8

class DocumentUploadResponse(BaseModel):
    filename: str
    status: str
    chunks_processed: Optional[int] = None
    error: Optional[str] = None

# Main diagnostic endpoint
@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query and return enhanced diagnostic insights"""
    
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        result = agent.diagnose_issue(request.query, session_id)
        
        return QueryResponse(
            response=result.get("response", ""),
            session_id=session_id,
            hypotheses=result.get("hypotheses", []),
            similar_cases=result.get("similar_cases", []),
            similar_documents=result.get("similar_documents", []),
            confidence=result.get("confidence", 0.0),
            analysis=result.get("analysis", ""),
            data_sources=result.get("data_sources", {}),
            reasoning_trace=result.get("reasoning_trace")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Document ingestion endpoint
@app.post("/documents/ingest", response_model=List[DocumentUploadResponse])
async def ingest_documents(files: List[UploadFile] = File(...)):
    """Ingest new documents into the knowledge base"""
    results = []
    
    for file in files:
        try:
            # Read file content
            content = await file.read()
            text_content = content.decode('utf-8')
            
            # Process document
            processed_doc = agent.document_processor.process_salesforce_case(
                text_content, 
                file.filename or "unknown_file"
            )
            
            # Add to vector store
            success = agent.vector_store.add_documents([processed_doc])
            
            if success:
                results.append(DocumentUploadResponse(
                    filename=file.filename or "unknown_file",
                    status="success",
                    chunks_processed=len(processed_doc['chunks'])
                ))
            else:
                results.append(DocumentUploadResponse(
                    filename=file.filename or "unknown_file",
                    status="warning",
                    chunks_processed=len(processed_doc['chunks']),
                    error="Document processed but not added to vector store"
                ))
            
        except Exception as e:
            results.append(DocumentUploadResponse(
                filename=file.filename or "unknown_file",
                status="error",
                error=str(e)
            ))
    
    return results

# Semantic search endpoint
@app.get("/documents/search")
async def search_documents(
    query: str,
    services: List[str] = Query(None),
    chunk_types: List[str] = Query(None),
    limit: int = 5
):
    """Semantic search across documents"""
    if not agent.embedder:
        raise HTTPException(status_code=503, detail="Semantic search not available - embeddings not loaded")
    
    try:
        # Generate query embedding
        query_embedding = agent.embedder.encode(query).tolist()
        
        # Search
        results = agent.vector_store.semantic_search(
            query_embedding=query_embedding,
            services=services,
            chunk_types=chunk_types,
            limit=limit
        )
        
        return {"query": query, "results": results, "count": len(results)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

# Case management endpoints
@app.post("/cases/add")
async def add_case(case: CaseData):
    """Add a new case to the knowledge base"""
    try:
        case_dict = case.model_dump()
        case_dict['created_at'] = datetime.now().isoformat()
        
        success = agent.add_case_to_knowledge_base(case_dict)
        
        if success:
            return {"status": "success", "message": f"Case {case.id} added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add case")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding case: {str(e)}")

@app.get("/cases/list")
async def list_cases():
    """List all cases in the knowledge base"""
    try:
        cases = agent.knowledge_base.get('cases', [])
        return {
            "cases": cases,
            "count": len(cases),
            "last_updated": agent.knowledge_base.get('created_at', 'unknown')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing cases: {str(e)}")

@app.get("/cases/{case_id}")
async def get_case(case_id: str):
    """Get a specific case by ID"""
    try:
        cases = agent.knowledge_base.get('cases', [])
        case = next((c for c in cases if c.get('id') == case_id), None)
        
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Also get associated documents from vector store
        documents = agent.vector_store.search_by_case_id(case_id)
        
        return {
            "case": case,
            "documents": documents,
            "document_count": len(documents)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving case: {str(e)}")

# Session management
@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session state for debugging"""
    session = agent.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.to_dict()

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id in agent.sessions:
        del agent.sessions[session_id]
        return {"status": "success", "message": "Session deleted"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

# System status and management
@app.get("/status")
async def get_system_status():
    """Get system status and component health"""
    try:
        status = agent.get_collection_status()
        
        # Add additional system info
        status.update({
            "api_version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "features": {
                "pattern_matching": True,
                "semantic_search": status['embeddings_available'],
                "document_processing": status['processor_available'],
                "session_management": True
            }
        })
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

# Load sample data endpoint
@app.post("/cases/load_samples")
async def load_sample_cases():
    """Load sample cases for testing"""
    try:
        sample_cases = [
            {
                "id": "case_001",
                "title": "Topology Merge Service Timeout",
                "description": "Service experiencing timeout errors after 30 seconds, high Kafka consumer lag detected",
                "affected_services": ["topology-merge", "kafka"],
                "symptoms": ["timeout", "30 seconds", "slow response", "kafka lag"],
                "resolution_steps": [
                    "Check Kafka consumer lag metrics",
                    "Monitor partition assignments", 
                    "Scale consumer instances",
                    "Verify network connectivity"
                ],
                "confidence": 0.95
            },
            {
                "id": "case_002", 
                "title": "Cassandra Connection Issues",
                "description": "Database connection timeouts causing service failures, high read latency observed",
                "affected_services": ["topology-inventory", "cassandra"],
                "symptoms": ["database timeout", "connection failed", "cassandra", "high latency"],
                "resolution_steps": [
                    "Check Cassandra cluster health",
                    "Monitor node performance",
                    "Review connection pool settings",
                    "Restart problematic nodes"
                ],
                "confidence": 0.9
            },
            {
                "id": "case_003",
                "title": "Redis Cache Performance",
                "description": "Cache misses and connection timeouts affecting status updates",
                "affected_services": ["topology-status", "redis"],
                "symptoms": ["cache miss", "redis", "stale data", "connection timeout"],
                "resolution_steps": [
                    "Monitor Redis memory usage",
                    "Check cache hit ratios", 
                    "Scale Redis cluster",
                    "Review eviction policies"
                ],
                "confidence": 0.85
            },
            {
                "id": "case_004",
                "title": "Observer Resource Consumption",
                "description": "High CPU and memory usage in observer services causing performance degradation",
                "affected_services": ["kubernetes-observer", "servicenow-observer"],
                "symptoms": ["high cpu", "memory leak", "slow processing", "observer"],
                "resolution_steps": [
                    "Monitor resource metrics",
                    "Check for memory leaks",
                    "Optimize data collection intervals",
                    "Scale observer instances"
                ],
                "confidence": 0.8
            }
        ]
        
        added_count = 0
        for case_data in sample_cases:
            case_data['created_at'] = datetime.now().isoformat()
            success = agent.add_case_to_knowledge_base(case_data)
            if success:
                added_count += 1
        
        return {
            "status": "success",
            "message": f"Loaded {added_count} sample cases",
            "total_cases": len(agent.knowledge_base.get('cases', []))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading sample cases: {str(e)}")

# Advanced search endpoint
@app.post("/search/advanced")
async def advanced_search(
    query: str,
    include_pattern_matching: bool = True,
    include_semantic_search: bool = True,
    services_filter: List[str] = None,
    confidence_threshold: float = 0.5
):
    """Advanced search combining multiple methods"""
    try:
        results = {}
        
        if include_pattern_matching:
            # Use agent's pattern matching
            pattern_results = agent._find_similar_cases_keyword(query)
            results['pattern_matches'] = pattern_results
        
        if include_semantic_search and agent.embedder:
            # Use semantic search
            query_embedding = agent.embedder.encode(query).tolist()
            semantic_results = agent.vector_store.semantic_search(
                query_embedding=query_embedding,
                services=services_filter,
                limit=10
            )
            
            # Filter by confidence threshold
            filtered_results = [
                r for r in semantic_results 
                if r.get('confidence', 0) >= confidence_threshold
            ]
            results['semantic_matches'] = filtered_results
        
        results['query'] = query
        results['filters'] = {
            'services': services_filter,
            'confidence_threshold': confidence_threshold
        }
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advanced search error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
