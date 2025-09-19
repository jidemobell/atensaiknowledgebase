#!/bin/bash

# =============================================================================
# MINIMAL CORE BACKEND RUNNER
# =============================================================================
# Run a minimal Core Backend without ML dependencies for API testing
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/corebackend/implementation/backend"
VENV_PATH="$PROJECT_ROOT/openwebui_venv"
TEMP_MAIN="$BACKEND_DIR/main_minimal.py"

echo -e "${BLUE}🚀 Starting Minimal Core Backend${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check prerequisites
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found: $VENV_PATH${NC}"
    exit 1
fi

if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found backend directory${NC}"

# Kill any existing processes on port 8001
echo -e "${YELLOW}🔄 Cleaning up existing processes on port 8001...${NC}"
pkill -f "uvicorn.*main.*8001" 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
sleep 2

# Create minimal main.py
echo -e "${BLUE}📝 Creating minimal Core Backend...${NC}"
cat > "$TEMP_MAIN" << 'EOF'
"""
Minimal FastAPI Backend for Testing API Structure
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
import json
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced AI-Powered Support System", 
    version="2.0.0",
    description="Intelligent diagnostic system with document processing and semantic search"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    session_id: str
    hypotheses: List[Dict[str, Any]] = []
    similar_cases: List[Dict[str, Any]] = []
    similar_documents: List[Dict[str, Any]] = []
    confidence: float = 0.0
    analysis: str = ""
    data_sources: Dict[str, bool] = {}

class CaseData(BaseModel):
    id: str
    title: str
    description: str
    affected_services: List[str]
    symptoms: List[str]
    resolution_steps: List[str]
    confidence: Optional[float] = 0.8

# Mock data storage
mock_cases = [
    {
        "id": "case-001",
        "title": "Sample Network Issue",
        "description": "Mock network connectivity problem",
        "affected_services": ["networking", "dns"],
        "symptoms": ["timeout", "connection refused"],
        "resolution_steps": ["Check network config", "Restart network service"],
        "confidence": 0.9
    }
]

# Routes
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

@app.get("/status")
async def get_system_status():
    return {
        "status": "operational",
        "components": {
            "api": "healthy",
            "database": "mocked",
            "embeddings": "disabled",
            "document_processor": "disabled"
        },
        "timestamp": datetime.now().isoformat(),
        "mode": "minimal"
    }

@app.post("/query")
async def process_query(request: QueryRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    # Mock response
    return QueryResponse(
        response=f"Mock response for query: {request.query}",
        session_id=session_id,
        hypotheses=[{"type": "mock", "description": "Sample hypothesis"}],
        similar_cases=[mock_cases[0]] if mock_cases else [],
        similar_documents=[],
        confidence=0.8,
        analysis="This is a mock analysis for testing purposes.",
        data_sources={"cases": True, "documents": False, "patterns": False}
    )

@app.get("/cases/list")
async def list_cases():
    return {"cases": mock_cases, "total": len(mock_cases)}

@app.get("/cases/{case_id}")
async def get_case(case_id: str):
    case = next((c for c in mock_cases if c["id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@app.post("/cases/add")
async def add_case(case: CaseData):
    new_case = case.dict()
    mock_cases.append(new_case)
    return {"status": "added", "case_id": case.id}

@app.post("/cases/load_samples")
async def load_sample_cases():
    return {"status": "loaded", "count": len(mock_cases)}

@app.get("/documents/search")
async def search_documents(query: str, limit: int = 5):
    return {
        "query": query,
        "results": [],
        "total": 0,
        "message": "Document search disabled in minimal mode"
    }

@app.post("/documents/ingest")
async def ingest_documents():
    return [{"filename": "mock", "status": "disabled", "message": "Document ingestion disabled in minimal mode"}]

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    return {
        "session_id": session_id,
        "created": datetime.now().isoformat(),
        "queries": [],
        "status": "active"
    }

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    return {"status": "deleted", "session_id": session_id}

@app.post("/search/advanced")
async def advanced_search(query: str):
    return {
        "query": query,
        "results": [],
        "confidence": 0.0,
        "message": "Advanced search disabled in minimal mode"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
EOF

echo -e "${GREEN}✅ Created minimal backend${NC}"

# Change to backend directory and activate venv
cd "$BACKEND_DIR"
source "$VENV_PATH/bin/activate"

echo -e "${BLUE}🚀 Starting minimal Core Backend on port 8001...${NC}"
echo -e "${BLUE}   Access at: http://localhost:8001${NC}"
echo -e "${BLUE}   API docs: http://localhost:8001/docs${NC}"
echo -e "${BLUE}   OpenAPI:  http://localhost:8001/openapi.json${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Start the minimal backend
exec python main_minimal.py