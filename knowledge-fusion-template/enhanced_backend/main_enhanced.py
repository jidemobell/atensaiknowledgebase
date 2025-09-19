"""
Enhanced Backend for OpenWebUI Integration
Multi-Agent Knowledge Fusion System - Beyond Traditional RAG
Features: Intent-aware processing, temporal reasoning, cross-source validation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
import json
import asyncio
from datetime import datetime
from pathlib import Path
import sys

# Add the multi-agent architecture module
sys.path.append(str(Path(__file__).parent.parent))
from multi_agent_architecture import MultiAgentOrchestrator, KnowledgeItem

app = FastAPI(
    title="IBM Knowledge Fusion Platform - Multi-Agent Architecture", 
    version="4.0.0",
    description="Advanced multi-agent knowledge fusion system beyond traditional RAG"
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

class AdvancedKnowledgeFusionQuery(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    preferred_sources: List[str] = []
    context_window: int = 5  # Number of previous messages to consider
    enable_temporal_reasoning: bool = True
    enable_cross_validation: bool = True
    complexity_threshold: str = "auto"  # auto, simple, medium, complex

class AdvancedKnowledgeFusionResponse(BaseModel):
    response: str
    sources_used: List[str]
    confidence: float
    reasoning_chain: List[str]
    intent_detected: str
    complexity_level: str
    suggested_follow_ups: List[str]
    conversation_id: str
    knowledge_areas_detected: List[str]
    execution_time: float
    agent_metrics: Dict[str, Any]
    cross_validation_score: Optional[float] = None

class KnowledgeFusionResponse(BaseModel):
    response: str
    sources_used: List[str]
    confidence: float
    reasoning: str
    suggested_follow_ups: List[str]
    conversation_id: str
    knowledge_areas_detected: List[str]

# Enhanced storage with multi-agent conversation support
enhanced_store = {
    'conversations': {},  # conversation_id -> ConversationContext
    'knowledge_areas': {
        'cases': [],
        'github_code': [],
        'documentation': [],
        'chat_history': [],
        'external_apis': [],
        'web_content': [],
        'databases': []
    },
    'user_profiles': {},  # user preferences and history
    'fusion_analytics': [],  # Track what sources work best
    'agent_performance': {}  # Track agent collaboration metrics
}

# Initialize Multi-Agent Orchestrator
multi_agent_orchestrator = MultiAgentOrchestrator()

class AdvancedSourceFusion:
    """
    Advanced knowledge fusion using multi-agent architecture
    Goes beyond traditional RAG with intent analysis, temporal reasoning, and cross-validation
    """
    
    def __init__(self):
        self.conversation_manager = ConversationManager()
        self.orchestrator = multi_agent_orchestrator
    
    async def fuse_knowledge_with_agents(self, query: str, conversation_id: str, user_id: str, 
                                       enable_temporal: bool = True, enable_validation: bool = True) -> Dict[str, Any]:
        """Main knowledge fusion using multi-agent system"""
        
        # Get conversation context for temporal reasoning
        context = self.conversation_manager.get_conversation_context(conversation_id)
        user_context = {
            'conversation_history': [{'role': msg.role, 'content': msg.content} for msg in context],
            'user_preferences': enhanced_store['user_profiles'].get(user_id, {}),
            'enable_temporal_reasoning': enable_temporal,
            'enable_cross_validation': enable_validation
        }
        
        # Process through multi-agent system
        agent_result = await self.orchestrator.process_query(
            query=query,
            conversation_id=conversation_id,
            user_context=user_context
        )
        
        # Create and store conversation messages
        user_msg = ChatMessage(
            id=str(uuid.uuid4()),
            role="user",
            content=query,
            timestamp=datetime.now(),
            sources_used=[],
            metadata={"intent": agent_result.get('intent_detected')}
        )
        
        assistant_msg = ChatMessage(
            id=str(uuid.uuid4()),
            role="assistant",
            content=agent_result['response'],
            timestamp=datetime.now(),
            sources_used=agent_result['sources_used'],
            confidence=agent_result['confidence'],
            metadata={
                "reasoning_chain": agent_result.get('reasoning_chain', []),
                "complexity_level": agent_result.get('complexity_level'),
                "agent_metrics": agent_result.get('agent_metrics', {})
            }
        )
        
        # Store messages
        conversation = self.conversation_manager.get_or_create_conversation(conversation_id, user_id)
        self.conversation_manager.add_message(conversation_id, user_msg)
        self.conversation_manager.add_message(conversation_id, assistant_msg)
        
        # Generate follow-up suggestions based on intent and complexity
        follow_ups = self._generate_intelligent_followups(agent_result)
        
        return {
            'response': agent_result['response'],
            'sources_used': agent_result['sources_used'],
            'confidence': agent_result['confidence'],
            'reasoning_chain': agent_result.get('reasoning_chain', []),
            'intent_detected': agent_result.get('intent_detected', 'general'),
            'complexity_level': agent_result.get('complexity_level', 'medium'),
            'suggested_follow_ups': follow_ups,
            'conversation_id': conversation_id,
            'knowledge_areas_detected': [agent_result.get('intent_detected', 'general')],
            'execution_time': agent_result.get('execution_time', 0.0),
            'agent_metrics': agent_result.get('agent_metrics', {}),
            'cross_validation_score': self._calculate_cross_validation_score(agent_result)
        }
    
    def _generate_intelligent_followups(self, agent_result: Dict[str, Any]) -> List[str]:
        """Generate context-aware follow-up suggestions"""
        intent = agent_result.get('intent_detected', 'general')
        complexity = agent_result.get('complexity_level', 'medium')
        
        followup_templates = {
            'troubleshooting': [
                "Would you like me to analyze similar past incidents?",
                "Should I check for related configuration issues?",
                "Do you need step-by-step debugging guidance?"
            ],
            'information_seeking': [
                "Would you like more detailed documentation on this topic?",
                "Should I find related examples or use cases?",
                "Do you need implementation guidance?"
            ],
            'code_analysis': [
                "Would you like me to review the code quality?",
                "Should I look for optimization opportunities?",
                "Do you need security analysis for this code?"
            ],
            'historical_inquiry': [
                "Would you like to see trends over time for this issue?",
                "Should I compare with more recent similar cases?",
                "Do you need a timeline of related events?"
            ]
        }
        
        base_followups = followup_templates.get(intent, [
            "Would you like me to explore this topic further?",
            "Should I look into related areas?",
            "Do you need more specific information?"
        ])
        
        # Adjust based on complexity
        if complexity == 'complex':
            base_followups.append("Would you like me to break this down into simpler components?")
        elif complexity == 'simple':
            base_followups.append("Would you like to explore more advanced aspects of this topic?")
        
        return base_followups[:3]  # Return top 3
    
    def _calculate_cross_validation_score(self, agent_result: Dict[str, Any]) -> Optional[float]:
        """Calculate cross-validation score based on source agreement"""
        sources_used = agent_result.get('sources_used', [])
        
        if len(sources_used) < 2:
            return None
        
        # Simple cross-validation score based on source diversity and confidence
        source_diversity = len(set(sources_used)) / max(len(sources_used), 1)
        base_confidence = agent_result.get('confidence', 0.5)
        
        # Cross-validation boost for multiple agreeing sources
        validation_score = (source_diversity * 0.3) + (base_confidence * 0.7)
        
        return min(1.0, validation_score)

# Initialize the advanced fusion system
advanced_source_fusion = AdvancedSourceFusion()

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
        "version": "4.0.0",
        "service": "Knowledge Fusion Platform - Multi-Agent Architecture",
        "agents_status": multi_agent_orchestrator.get_system_status()
    }

@app.post("/knowledge-fusion/query")
async def advanced_knowledge_fusion_query(request: AdvancedKnowledgeFusionQuery) -> AdvancedKnowledgeFusionResponse:
    """
    Advanced multi-agent knowledge fusion endpoint
    Features: Intent analysis, temporal reasoning, cross-source validation
    """
    try:
        # Generate conversation ID if not provided
        if not request.conversation_id:
            request.conversation_id = str(uuid.uuid4())
        
        # Generate user ID if not provided
        if not request.user_id:
            request.user_id = "default_user"
        
        # Process the query through advanced multi-agent fusion
        response_data = await advanced_source_fusion.fuse_knowledge_with_agents(
            query=request.query,
            conversation_id=request.conversation_id,
            user_id=request.user_id,
            enable_temporal=request.enable_temporal_reasoning,
            enable_validation=request.enable_cross_validation
        )
        
        return AdvancedKnowledgeFusionResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-agent knowledge fusion error: {str(e)}")

@app.post("/knowledge-fusion/simple-query")
async def simple_knowledge_fusion_query(request: Dict[str, Any]):
    """
    Simplified endpoint for basic queries (backward compatibility)
    """
    try:
        advanced_request = AdvancedKnowledgeFusionQuery(
            query=request.get('query', ''),
            conversation_id=request.get('conversation_id'),
            user_id=request.get('user_id', 'default_user')
        )
        
        response = await advanced_knowledge_fusion_query(advanced_request)
        
        return {
            "response": response.response,
            "confidence": response.confidence,
            "sources_used": response.sources_used,
            "reasoning": response.reasoning_chain[-1] if response.reasoning_chain else "Multi-agent processing completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simple fusion error: {str(e)}")

@app.get("/system/agent-status")
async def get_agent_system_status():
    """Get detailed multi-agent system status"""
    return multi_agent_orchestrator.get_system_status()

@app.get("/system/metrics")
async def get_system_metrics():
    """Get comprehensive system performance metrics"""
    agent_status = multi_agent_orchestrator.get_system_status()
    
    return {
        "system_health": agent_status.get('system_health', 'unknown'),
        "orchestrator_metrics": agent_status.get('orchestrator_metrics', {}),
        "agent_performance": {
            agent_name: agent_data.get('performance_metrics', {})
            for agent_name, agent_data in agent_status.get('agent_status', {}).items()
        },
        "knowledge_store_size": {
            area: len(data) for area, data in enhanced_store['knowledge_areas'].items()
        },
        "active_conversations": len(enhanced_store['conversations'])
    }

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
    try:
        advanced_request = AdvancedKnowledgeFusionQuery(
            query=request.get('query', ''),
            conversation_id=request.get('conversation_id'),
            user_id=request.get('user_id', 'default_user')
        )
        
        response = await advanced_knowledge_fusion_query(advanced_request)
        return {
            "response": response.response, 
            "confidence": response.confidence,
            "sources": response.sources_used
        }
    except Exception as e:
        return {"response": f"Error processing query: {str(e)}", "confidence": 0.0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
