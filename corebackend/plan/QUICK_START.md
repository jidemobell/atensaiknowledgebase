# Quick Start: Minimal Viable Implementation

This document provides a practical starting point to build the first phase of your AI-powered support system.

## Phase 1 Setup (Week 1-2)

### Prerequisites
```bash
# Python environment
python -m venv ai-support-env
source ai-support-env/bin/activate  # On macOS/Linux
pip install -r requirements.txt

# Docker for local development  
docker --version
docker-compose --version
```

### Required Dependencies

#### requirements.txt
```txt
fastapi==0.104.1
uvicorn==0.24.0
langchain==0.1.0
langgraph==0.0.20
weaviate-client==4.4.0
neo4j==5.15.0
redis==5.0.1
sentence-transformers==2.2.2
pandas==2.1.3
pydantic==2.5.0
python-multipart==0.0.6
httpx==0.25.2
python-dotenv==1.0.0

# For React frontend
# npm install axios react-query @tanstack/react-query
```

#### docker-compose.yml
```yaml
version: '3.8'
services:
  weaviate:
    image: semitechnologies/weaviate:1.22.4
    ports:
      - "8080:8080"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'none'
      CLUSTER_HOSTNAME: 'node1'
    volumes:
      - weaviate_data:/var/lib/weaviate

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  neo4j:
    image: neo4j:5.15-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/password
      NEO4J_PLUGINS: '["graph-data-science"]'
    volumes:
      - neo4j_data:/data

volumes:
  weaviate_data:
  redis_data:
  neo4j_data:
```

## Core Implementation

### 1. Data Models (models.py)

```python
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class ServiceType(str, Enum):
    TOPOLOGY_MERGE = "topology-merge"
    TOPOLOGY_INVENTORY = "topology-inventory" 
    TOPOLOGY_STATUS = "topology-status"
    KAFKA = "kafka"
    CASSANDRA = "cassandra"
    OTHER = "other"

class CaseStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Case(BaseModel):
    id: str
    title: str
    description: str
    status: CaseStatus
    created_at: datetime
    resolved_at: Optional[datetime] = None
    affected_services: List[ServiceType]
    symptoms: List[str]
    resolution_steps: List[str] = []
    tags: List[str] = []

class DiagnosticHypothesis(BaseModel):
    cause: str
    probability: float
    evidence: List[str]
    next_steps: List[str]

class SessionState(BaseModel):
    session_id: str
    current_case_context: Dict[str, Any]
    hypotheses: List[DiagnosticHypothesis]
    eliminated_causes: List[str]
    conversation_history: List[Dict[str, str]]
    last_updated: datetime
```

### 2. Knowledge Graph Setup (knowledge_graph.py)

```python
import weaviate
from typing import List, Dict, Any
import json

class KnowledgeGraph:
    def __init__(self, weaviate_url: str = "http://localhost:8080"):
        self.client = weaviate.Client(weaviate_url)
        self.setup_schema()
    
    def setup_schema(self):
        """Create Weaviate schema for our knowledge graph"""
        
        case_schema = {
            "class": "Case",
            "description": "A support case from Salesforce",
            "properties": [
                {"name": "caseId", "dataType": ["text"]},
                {"name": "title", "dataType": ["text"]},
                {"name": "description", "dataType": ["text"]},
                {"name": "status", "dataType": ["text"]},
                {"name": "affectedServices", "dataType": ["text[]"]},
                {"name": "symptoms", "dataType": ["text[]"]},
                {"name": "resolutionSteps", "dataType": ["text[]"]},
                {"name": "createdAt", "dataType": ["date"]},
            ],
            "vectorizer": "none"  # We'll add embeddings manually
        }
        
        service_schema = {
            "class": "Service", 
            "description": "A service in the IBM AIOPs topology",
            "properties": [
                {"name": "serviceName", "dataType": ["text"]},
                {"name": "serviceType", "dataType": ["text"]},
                {"name": "dependencies", "dataType": ["text[]"]},
                {"name": "commonIssues", "dataType": ["text[]"]},
            ],
            "vectorizer": "none"
        }
        
        fix_schema = {
            "class": "Fix",
            "description": "A resolution or fix for a case",
            "properties": [
                {"name": "description", "dataType": ["text"]},
                {"name": "commands", "dataType": ["text[]"]},
                {"name": "successRate", "dataType": ["number"]},
                {"name": "applicableServices", "dataType": ["text[]"]},
            ],
            "vectorizer": "none"
        }
        
        # Create schemas if they don't exist
        for schema in [case_schema, service_schema, fix_schema]:
            try:
                self.client.schema.create_class(schema)
                print(f"Created schema: {schema['class']}")
            except Exception as e:
                print(f"Schema {schema['class']} might already exist: {e}")
    
    def add_case(self, case: Case, embedding: List[float]):
        """Add a case to the knowledge graph"""
        case_obj = {
            "caseId": case.id,
            "title": case.title,
            "description": case.description,
            "status": case.status.value,
            "affectedServices": [s.value for s in case.affected_services],
            "symptoms": case.symptoms,
            "resolutionSteps": case.resolution_steps,
            "createdAt": case.created_at.isoformat(),
        }
        
        self.client.data_object.create(
            data_object=case_obj,
            class_name="Case",
            vector=embedding
        )
    
    def find_similar_cases(self, query_embedding: List[float], limit: int = 5) -> List[Dict]:
        """Find similar cases using vector similarity"""
        result = (
            self.client.query
            .get("Case", ["caseId", "title", "description", "affectedServices", "resolutionSteps"])
            .with_near_vector({"vector": query_embedding})
            .with_limit(limit)
            .with_additional(["certainty", "distance"])
            .do()
        )
        
        return result.get("data", {}).get("Get", {}).get("Case", [])
```

### 3. Stateful Agent (agent.py)

```python
import redis
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from models import SessionState, DiagnosticHypothesis, Case

class StatefulDiagnosticAgent:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.knowledge_graph = KnowledgeGraph()
        
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Retrieve session state from Redis"""
        session_data = self.redis_client.get(f"session:{session_id}")
        if session_data:
            return SessionState.model_validate(json.loads(session_data))
        return None
    
    def save_session(self, session: SessionState):
        """Save session state to Redis with expiration"""
        session_key = f"session:{session.session_id}"
        session_data = session.model_dump_json()
        self.redis_client.setex(session_key, timedelta(hours=24), session_data)
    
    def process_query(self, query: str, session_id: str) -> Dict:
        """Process a query with stateful reasoning"""
        
        # Get or create session
        session = self.get_session(session_id)
        if not session:
            session = SessionState(
                session_id=session_id,
                current_case_context={},
                hypotheses=[],
                eliminated_causes=[],
                conversation_history=[],
                last_updated=datetime.now()
            )
        
        # Add query to conversation history
        session.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "user_query",
            "content": query
        })
        
        # Generate embedding for semantic search
        query_embedding = self.embedder.encode(query).tolist()
        
        # Find similar cases
        similar_cases = self.knowledge_graph.find_similar_cases(
            query_embedding, limit=3
        )
        
        # Update hypotheses based on similar cases
        new_hypotheses = self.generate_hypotheses(query, similar_cases)
        session.hypotheses = self.merge_hypotheses(session.hypotheses, new_hypotheses)
        
        # Generate response
        response = self.generate_response(query, session, similar_cases)
        
        # Add response to conversation history
        session.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "agent_response", 
            "content": response["response"]
        })
        
        session.last_updated = datetime.now()
        self.save_session(session)
        
        return response
    
    def generate_hypotheses(self, query: str, similar_cases: List[Dict]) -> List[DiagnosticHypothesis]:
        """Generate diagnostic hypotheses from similar cases"""
        hypotheses = []
        
        for case in similar_cases:
            # Extract common patterns
            services = case.get("affectedServices", [])
            resolution_steps = case.get("resolutionSteps", [])
            
            if services and resolution_steps:
                # Simple heuristic for hypothesis generation
                cause = self.extract_likely_cause(resolution_steps)
                if cause:
                    hypothesis = DiagnosticHypothesis(
                        cause=cause,
                        probability=float(case.get("_additional", {}).get("certainty", 0.5)),
                        evidence=[f"Similar case: {case.get('title', '')[:100]}"],
                        next_steps=resolution_steps[:3]  # Top 3 steps
                    )
                    hypotheses.append(hypothesis)
        
        return hypotheses
    
    def extract_likely_cause(self, resolution_steps: List[str]) -> Optional[str]:
        """Extract likely root cause from resolution steps"""
        # Simple pattern matching - enhance this with NLP
        keywords_to_causes = {
            "kafka": "Kafka connectivity/lag issue",
            "cassandra": "Cassandra performance issue", 
            "timeout": "Service timeout issue",
            "memory": "Memory/resource issue",
            "disk": "Disk space issue"
        }
        
        for step in resolution_steps:
            step_lower = step.lower()
            for keyword, cause in keywords_to_causes.items():
                if keyword in step_lower:
                    return cause
        
        return None
    
    def merge_hypotheses(self, current: List[DiagnosticHypothesis], 
                        new: List[DiagnosticHypothesis]) -> List[DiagnosticHypothesis]:
        """Merge and deduplicate hypotheses"""
        # Simple deduplication by cause
        merged = {}
        
        for hypothesis in current + new:
            if hypothesis.cause in merged:
                # Update probability with simple averaging
                existing = merged[hypothesis.cause]
                existing.probability = (existing.probability + hypothesis.probability) / 2
                existing.evidence.extend(hypothesis.evidence)
                existing.next_steps.extend(hypothesis.next_steps)
            else:
                merged[hypothesis.cause] = hypothesis
        
        # Sort by probability
        return sorted(merged.values(), key=lambda h: h.probability, reverse=True)
    
    def generate_response(self, query: str, session: SessionState, 
                         similar_cases: List[Dict]) -> Dict:
        """Generate response based on current session state"""
        
        response = {
            "response": "",
            "hypotheses": [h.model_dump() for h in session.hypotheses[:3]],
            "similar_cases": similar_cases,
            "next_steps": [],
            "confidence": 0.0
        }
        
        if session.hypotheses:
            top_hypothesis = session.hypotheses[0]
            response["response"] = f"""Based on similar cases, the most likely cause is: **{top_hypothesis.cause}**

**Confidence**: {top_hypothesis.probability:.2%}

**Suggested next steps**:
{chr(10).join(f"• {step}" for step in top_hypothesis.next_steps)}

**Evidence**:
{chr(10).join(f"• {evidence}" for evidence in top_hypothesis.evidence)}
"""
            response["next_steps"] = top_hypothesis.next_steps
            response["confidence"] = top_hypothesis.probability
        else:
            response["response"] = "I need more information to diagnose this issue. Can you provide more details about the symptoms or error messages?"
        
        return response
```

### 4. FastAPI Backend (main.py)

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
from agent import StatefulDiagnosticAgent

app = FastAPI(title="AI-Powered Support System", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = StatefulDiagnosticAgent()

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    session_id: str
    hypotheses: List[Dict]
    similar_cases: List[Dict]
    next_steps: List[str]
    confidence: float

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query and return diagnostic insights"""
    
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        result = agent.process_query(request.query, session_id)
        
        return QueryResponse(
            response=result["response"],
            session_id=session_id,
            hypotheses=result["hypotheses"],
            similar_cases=result["similar_cases"],
            next_steps=result["next_steps"],
            confidence=result["confidence"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session state for debugging"""
    session = agent.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.model_dump()

@app.post("/cases/load")
async def load_sample_cases():
    """Load sample cases for testing"""
    # This would normally load from Salesforce
    # For now, create some sample data
    sample_cases = [
        {
            "id": "case_001",
            "title": "topology-merge service timeout",
            "description": "Customer reports topology-merge timing out after 30 seconds",
            "affected_services": ["topology-merge", "kafka"],
            "resolution_steps": [
                "Checked Kafka consumer lag",
                "Found lag of 50K messages", 
                "Increased consumer instances from 2 to 4",
                "Issue resolved"
            ]
        },
        # Add more sample cases...
    ]
    
    # Process and add to knowledge graph
    for case_data in sample_cases:
        # Generate embedding
        embedding = agent.embedder.encode(case_data["description"]).tolist()
        
        # Create case object and add to knowledge graph
        # (Implementation details here...)
    
    return {"status": "Sample cases loaded"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-support-system"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 5. React Frontend Setup

#### package.json
```json
{
  "name": "ai-support-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.16.5",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^13.5.0",
    "axios": "^1.6.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-query": "^3.39.0",
    "react-scripts": "5.0.1",
    "web-vitals": "^2.1.4"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

#### App.js (Basic Chat Interface)
```jsx
import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    
    try {
      const result = await axios.post(`${API_BASE}/query`, {
        query: query,
        session_id: sessionId
      });

      const newResponse = result.data;
      setResponse(newResponse);
      setSessionId(newResponse.session_id);
      
      // Add to conversation history
      setConversationHistory(prev => [
        ...prev,
        { type: 'user', content: query },
        { type: 'assistant', content: newResponse.response }
      ]);
      
      setQuery('');
    } catch (error) {
      console.error('Error:', error);
      alert('Error processing query');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI-Powered Support System</h1>
        {sessionId && <p>Session: {sessionId.slice(0, 8)}...</p>}
      </header>

      <div className="conversation">
        {conversationHistory.map((msg, idx) => (
          <div key={idx} className={`message ${msg.type}`}>
            <strong>{msg.type === 'user' ? 'You' : 'AI'}:</strong>
            <div dangerouslySetInnerHTML={{ __html: msg.content.replace(/\n/g, '<br/>') }} />
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="query-form">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe the issue you're facing..."
          rows={3}
          cols={50}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Ask AI'}
        </button>
      </form>

      {response && (
        <div className="response-details">
          <h3>Diagnostic Details</h3>
          <p><strong>Confidence:</strong> {(response.confidence * 100).toFixed(1)}%</p>
          
          {response.hypotheses.length > 0 && (
            <div>
              <h4>Top Hypotheses:</h4>
              <ul>
                {response.hypotheses.map((hyp, idx) => (
                  <li key={idx}>
                    {hyp.cause} ({(hyp.probability * 100).toFixed(1)}%)
                  </li>
                ))}
              </ul>
            </div>
          )}

          {response.next_steps.length > 0 && (
            <div>
              <h4>Next Steps:</h4>
              <ol>
                {response.next_steps.map((step, idx) => (
                  <li key={idx}>{step}</li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
```

## Getting Started Commands

```bash
# Terminal 1: Start infrastructure
docker-compose up -d

# Terminal 2: Start backend
cd backend
pip install -r requirements.txt
python main.py

# Terminal 3: Start frontend  
cd frontend
npm install
npm start

# Terminal 4: Load sample data
curl -X POST http://localhost:8000/cases/load
```

## Next Steps

1. **Test the basic system** with sample cases
2. **Add real Salesforce case data** (manual copy-paste for now)
3. **Enhance the knowledge graph** with service dependencies
4. **Implement tool integration** (Phase 3)
5. **Add more sophisticated reasoning** (Phase 4)

This gives you a solid foundation that's already beyond basic RAG with stateful sessions and hypothesis tracking!
