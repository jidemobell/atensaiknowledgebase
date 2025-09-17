"""
Enhanced Backend for OpenWebUI Integration
Extends your existing backend with conversational AI capabilities
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
import json
from datetime import datetime
from pathlib import Path

app = FastAPI(
    title="IBM Knowledge Fusion Platform - Enhanced for OpenWebUI", 
    version="3.0.0",
    description="Conversational AI with multi-source knowledge fusion"
)

# Enable CORS for OpenWebUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced data models for chat integration
class ChatMessage(BaseModel):
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    sources_used: List[str] = []
    confidence: float = 0.0
    metadata: Dict[str, Any] = {}

class ConversationContext(BaseModel):
    conversation_id: str
    user_id: str
    messages: List[ChatMessage]
    active_knowledge_areas: List[str] = []
    session_metadata: Dict[str, Any] = {}

class KnowledgeFusionQuery(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    preferred_sources: List[str] = []
    context_window: int = 5  # Number of previous messages to consider

class KnowledgeFusionResponse(BaseModel):
    response: str
    sources_used: List[str]
    confidence: float
    reasoning: str
    suggested_follow_ups: List[str]
    conversation_id: str
    knowledge_areas_detected: List[str]

# Enhanced storage with conversation support
enhanced_store = {
    'conversations': {},  # conversation_id -> ConversationContext
    'knowledge_areas': {
        'cases': [],
        'github_code': [],
        'documentation': [],
        'chat_history': [],
        'external_apis': []
    },
    'user_profiles': {},  # user preferences and history
    'fusion_analytics': []  # Track what sources work best
}

class KnowledgeRouter:
    """
    Intelligent routing system that determines which knowledge sources
    to query based on the conversation context and query analysis
    """
    
    def analyze_query_intent(self, query: str, context: List[ChatMessage]) -> Dict[str, Any]:
        """Analyze what the user is asking and determine relevant knowledge areas"""
        import re
        
        # Intent detection patterns
        intents = {
            'topology_issue': r'topology|merge|network|connectivity|infrastructure',
            'code_question': r'code|function|class|method|implementation|bug|error',
            'documentation': r'how to|guide|documentation|manual|setup|configure',
            'historical_case': r'similar|previous|before|history|past|case',
            'troubleshooting': r'error|problem|issue|fail|timeout|crash|debug'
        }
        
        detected_intents = []
        for intent_name, pattern in intents.items():
            if re.search(pattern, query, re.IGNORECASE):
                detected_intents.append(intent_name)
        
        # Analyze conversation context for additional clues
        context_keywords = []
        if context:
            recent_messages = context[-3:]  # Last 3 messages
            for msg in recent_messages:
                context_keywords.extend(msg.content.lower().split())
        
        return {
            'detected_intents': detected_intents,
            'context_keywords': context_keywords,
            'recommended_sources': self._get_sources_for_intents(detected_intents),
            'confidence': len(detected_intents) / len(intents)
        }
    
    def _get_sources_for_intents(self, intents: List[str]) -> List[str]:
        """Map intents to knowledge sources"""
        source_mapping = {
            'topology_issue': ['cases', 'documentation', 'github_code'],
            'code_question': ['github_code', 'documentation', 'chat_history'],
            'documentation': ['documentation', 'cases'],
            'historical_case': ['cases', 'chat_history'],
            'troubleshooting': ['cases', 'github_code', 'documentation']
        }
        
        sources = set()
        for intent in intents:
            sources.update(source_mapping.get(intent, []))
        
        return list(sources)

class ConversationManager:
    """Manages chat history and conversation context"""
    
    def get_or_create_conversation(self, conversation_id: str, user_id: str) -> ConversationContext:
        """Get existing conversation or create new one"""
        if conversation_id not in enhanced_store['conversations']:
            enhanced_store['conversations'][conversation_id] = ConversationContext(
                conversation_id=conversation_id,
                user_id=user_id,
                messages=[],
                active_knowledge_areas=[],
                session_metadata={}
            )
        return enhanced_store['conversations'][conversation_id]
    
    def add_message(self, conversation_id: str, message: ChatMessage):
        """Add message to conversation history"""
        if conversation_id in enhanced_store['conversations']:
            enhanced_store['conversations'][conversation_id].messages.append(message)
    
    def get_conversation_context(self, conversation_id: str, window_size: int = 5) -> List[ChatMessage]:
        """Get recent conversation context"""
        if conversation_id not in enhanced_store['conversations']:
            return []
        
        messages = enhanced_store['conversations'][conversation_id].messages
        return messages[-window_size:] if messages else []

class SourceFusion:
    """Combines information from multiple knowledge sources"""
    
    def __init__(self):
        self.knowledge_router = KnowledgeRouter()
        self.conversation_manager = ConversationManager()
    
    def fuse_knowledge(self, query: str, conversation_id: str, user_id: str) -> KnowledgeFusionResponse:
        """Main knowledge fusion logic"""
        
        # Get conversation context
        context = self.conversation_manager.get_conversation_context(conversation_id)
        
        # Analyze query intent and determine sources
        analysis = self.knowledge_router.analyze_query_intent(query, context)
        
        # Query relevant knowledge sources
        knowledge_results = self._query_knowledge_sources(
            query, 
            analysis['recommended_sources'],
            context
        )
        
        # Synthesize response
        response = self._synthesize_response(query, knowledge_results, analysis)
        
        # Create and store user message
        user_msg = ChatMessage(
            id=str(uuid.uuid4()),
            role="user",
            content=query,
            timestamp=datetime.now(),
            sources_used=[],
            metadata={"analysis": analysis}
        )
        
        # Create assistant response message
        assistant_msg = ChatMessage(
            id=str(uuid.uuid4()),
            role="assistant",
            content=response['response'],
            timestamp=datetime.now(),
            sources_used=response['sources_used'],
            confidence=response['confidence'],
            metadata={"reasoning": response['reasoning']}
        )
        
        # Store messages
        conversation = self.conversation_manager.get_or_create_conversation(conversation_id, user_id)
        self.conversation_manager.add_message(conversation_id, user_msg)
        self.conversation_manager.add_message(conversation_id, assistant_msg)
        
        return KnowledgeFusionResponse(
            response=response['response'],
            sources_used=response['sources_used'],
            confidence=response['confidence'],
            reasoning=response['reasoning'],
            suggested_follow_ups=response['suggested_follow_ups'],
            conversation_id=conversation_id,
            knowledge_areas_detected=analysis['detected_intents']
        )
    
    def _query_knowledge_sources(self, query: str, sources: List[str], context: List[ChatMessage]) -> Dict[str, Any]:
        """Query the specified knowledge sources"""
        results = {}
        
        for source in sources:
            if source == 'cases':
                results['cases'] = self._query_historical_cases(query)
            elif source == 'github_code':
                results['github_code'] = self._query_github_code(query)
            elif source == 'documentation':
                results['documentation'] = self._query_documentation(query)
            elif source == 'chat_history':
                results['chat_history'] = self._query_chat_history(query, context)
        
        return results
    
    def _query_historical_cases(self, query: str) -> List[Dict]:
        """Query your existing case knowledge base"""
        # This will integrate with your existing backend functionality
        # For now, return mock data
        return [
            {
                "case_id": "CASE-001",
                "title": "Topology merge service timeout",
                "description": "Service experiencing timeouts after 30 seconds",
                "resolution": "Increased timeout configuration and optimized query",
                "relevance": 0.9
            }
        ]
    
    def _query_github_code(self, query: str) -> List[Dict]:
        """Query GitHub repositories for relevant code"""
        return [
            {
                "repo": "topology-service",
                "file": "src/merge.py",
                "snippet": "def merge_topology(timeout=30):",
                "relevance": 0.8
            }
        ]
    
    def _query_documentation(self, query: str) -> List[Dict]:
        """Query documentation sources"""
        return [
            {
                "doc_type": "API_GUIDE",
                "title": "Topology Service Configuration",
                "content": "Configure timeout settings in config.yaml",
                "relevance": 0.85
            }
        ]
    
    def _query_chat_history(self, query: str, context: List[ChatMessage]) -> List[Dict]:
        """Search previous conversations for relevant information"""
        relevant_messages = []
        query_lower = query.lower()
        
        for msg in context:
            if any(word in msg.content.lower() for word in query_lower.split()):
                relevant_messages.append({
                    "message": msg.content,
                    "role": msg.role,
                    "timestamp": msg.timestamp,
                    "relevance": 0.7
                })
        
        return relevant_messages
    
    def _synthesize_response(self, query: str, knowledge_results: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Combine knowledge from multiple sources into coherent response"""
        
        # For now, create a structured response based on available knowledge
        response_parts = []
        sources_used = []
        total_confidence = 0
        source_count = 0
        
        # Process each knowledge source
        for source_type, results in knowledge_results.items():
            if results:
                sources_used.append(source_type)
                source_count += 1
                
                if source_type == 'cases':
                    response_parts.append(f"Based on historical cases, I found: {results[0]['description']}")
                    response_parts.append(f"Previous resolution: {results[0]['resolution']}")
                    total_confidence += results[0]['relevance']
                
                elif source_type == 'github_code':
                    response_parts.append(f"From code analysis: {results[0]['snippet']}")
                    total_confidence += results[0]['relevance']
                
                elif source_type == 'documentation':
                    response_parts.append(f"Documentation suggests: {results[0]['content']}")
                    total_confidence += results[0]['relevance']
                
                elif source_type == 'chat_history':
                    if results:
                        response_parts.append("From our previous conversation, this relates to earlier discussions.")
                        total_confidence += 0.6
        
        # Calculate overall confidence
        confidence = total_confidence / source_count if source_count > 0 else 0.5
        
        # Combine response parts
        if response_parts:
            response = " ".join(response_parts)
        else:
            response = f"I understand you're asking about: {query}. Let me help you with that based on available knowledge."
        
        # Generate follow-up suggestions
        follow_ups = [
            "Would you like me to look deeper into this specific area?",
            "Are there related issues you'd like to explore?",
            "Do you need more technical details about the solution?"
        ]
        
        return {
            'response': response,
            'sources_used': sources_used,
            'confidence': confidence,
            'reasoning': f"I analyzed your query and found {len(sources_used)} relevant knowledge sources with {analysis['detected_intents']} detected intents.",
            'suggested_follow_ups': follow_ups[:2]  # Return first 2
        }

# Initialize the fusion system
source_fusion = SourceFusion()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "service": "Knowledge Fusion Platform"
    }

@app.post("/knowledge-fusion/query")
async def knowledge_fusion_query(request: KnowledgeFusionQuery) -> KnowledgeFusionResponse:
    """
    Main endpoint for OpenWebUI integration
    Handles conversational queries with multi-source knowledge fusion
    """
    try:
        # Generate conversation ID if not provided
        if not request.conversation_id:
            request.conversation_id = str(uuid.uuid4())
        
        # Generate user ID if not provided
        if not request.user_id:
            request.user_id = "default_user"
        
        # Process the query through knowledge fusion
        response = source_fusion.fuse_knowledge(
            query=request.query,
            conversation_id=request.conversation_id,
            user_id=request.user_id
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge fusion error: {str(e)}")

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    if conversation_id not in enhanced_store['conversations']:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return enhanced_store['conversations'][conversation_id]

@app.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str, limit: int = 50):
    """Get messages from a conversation"""
    if conversation_id not in enhanced_store['conversations']:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = enhanced_store['conversations'][conversation_id].messages
    return messages[-limit:] if messages else []

@app.post("/knowledge/upload-cases")
async def upload_knowledge_cases(cases: List[Dict[str, Any]]):
    """Upload historical cases to knowledge base"""
    enhanced_store['knowledge_areas']['cases'].extend(cases)
    return {"status": "success", "uploaded": len(cases)}

# Legacy endpoints for compatibility with your existing system
@app.post("/query")
async def legacy_query(request: Dict[str, Any]):
    """Legacy endpoint for backward compatibility"""
    fusion_request = KnowledgeFusionQuery(
        query=request.get('query', ''),
        conversation_id=request.get('conversation_id'),
        user_id=request.get('user_id')
    )
    
    response = await knowledge_fusion_query(fusion_request)
    return {"response": response.response, "confidence": response.confidence}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
