"""
Lightweight Core Backend for IBM AIOps Knowledge System  
Works without heavy ML dependencies for testing and development
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
import json
from datetime import datetime
import os

# Initialize FastAPI app
app = FastAPI(
    title="Core Backend - Lightweight Mode", 
    version="2.0.0-lite",
    description="Core API functionality without ML dependencies"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class DiagnosticRequest(BaseModel):
    issue_description: str
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class DiagnosticResponse(BaseModel):
    session_id: str
    analysis: Dict[str, Any]
    suggestions: List[str]
    confidence_score: float
    follow_up_questions: List[str]

class KnowledgeEntry(BaseModel):
    title: str
    content: str
    category: str
    tags: List[str] = []
    metadata: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    limit: int = 10

# In-memory storage for development
knowledge_base = []
sessions = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Core Backend - Lightweight Mode",
        "version": "2.0.0-lite",
        "status": "running",
        "mode": "development",
        "ml_dependencies": "disabled",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "core-backend-lite",
        "timestamp": datetime.now().isoformat(),
        "dependencies": {
            "fastapi": "available",
            "ml_components": "disabled"
        }
    }

@app.post("/diagnose", response_model=DiagnosticResponse)
async def diagnose_issue(request: DiagnosticRequest):
    """
    Lightweight diagnostic endpoint
    Returns mock analysis for testing purposes
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    # Mock diagnostic analysis
    analysis = {
        "issue_type": "general_inquiry",
        "severity": "medium",
        "category": "system_analysis",
        "context_analysis": request.context or {},
        "processed_at": datetime.now().isoformat(),
        "processing_mode": "lightweight"
    }
    
    suggestions = [
        "Check system logs for recent errors",
        "Verify network connectivity",
        "Review recent configuration changes",
        "Monitor system resources (CPU, memory, disk)"
    ]
    
    follow_up_questions = [
        "When did you first notice this issue?",
        "Have there been any recent system changes?",
        "What is the frequency of this problem?",
        "Are there any error messages in the logs?"
    ]
    
    # Store session
    sessions[session_id] = {
        "created_at": datetime.now().isoformat(),
        "issue_description": request.issue_description,
        "analysis": analysis
    }
    
    return DiagnosticResponse(
        session_id=session_id,
        analysis=analysis,
        suggestions=suggestions,
        confidence_score=0.75,
        follow_up_questions=follow_up_questions
    )

@app.post("/knowledge/add")
async def add_knowledge(entry: KnowledgeEntry):
    """Add knowledge entry to the base"""
    entry_id = str(uuid.uuid4())
    knowledge_entry = {
        "id": entry_id,
        "title": entry.title,
        "content": entry.content,
        "category": entry.category,
        "tags": entry.tags,
        "metadata": entry.metadata or {},
        "created_at": datetime.now().isoformat()
    }
    
    knowledge_base.append(knowledge_entry)
    
    return {
        "status": "success",
        "entry_id": entry_id,
        "message": "Knowledge entry added successfully"
    }

@app.post("/knowledge/search")
async def search_knowledge(request: SearchRequest):
    """
    Lightweight knowledge search
    Uses simple text matching instead of semantic search
    """
    query_lower = request.query.lower()
    results = []
    
    for entry in knowledge_base:
        # Simple text matching
        if (query_lower in entry["title"].lower() or 
            query_lower in entry["content"].lower() or
            any(query_lower in tag.lower() for tag in entry["tags"])):
            
            if not request.category or entry["category"] == request.category:
                results.append({
                    "id": entry["id"],
                    "title": entry["title"],
                    "content": entry["content"][:200] + "...",  # Truncate content
                    "category": entry["category"],
                    "tags": entry["tags"],
                    "relevance_score": 0.8  # Mock score
                })
    
    # Limit results
    results = results[:request.limit]
    
    return {
        "query": request.query,
        "results": results,
        "total_found": len(results),
        "search_method": "text_matching"
    }

@app.get("/knowledge/categories")
async def get_categories():
    """Get all available knowledge categories"""
    categories = list(set(entry["category"] for entry in knowledge_base))
    return {
        "categories": categories,
        "total": len(categories)
    }

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return sessions[session_id]

@app.get("/sessions")
async def list_sessions():
    """List all sessions"""
    return {
        "sessions": list(sessions.keys()),
        "total": len(sessions)
    }

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    return {"status": "success", "message": f"Session {session_id} deleted"}

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "knowledge_entries": len(knowledge_base),
        "active_sessions": len(sessions),
        "uptime_check": datetime.now().isoformat(),
        "mode": "lightweight",
        "ml_status": "disabled"
    }

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Mock document upload endpoint
    In production, this would process documents and extract knowledge
    """
    return {
        "status": "success",
        "filename": file.filename,
        "message": "Document upload simulated (lightweight mode)",
        "processing_mode": "mock"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)