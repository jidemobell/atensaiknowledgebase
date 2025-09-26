#!/usr/bin/env python3
"""
Multi-Agent Knowledge System - Phase 2 Implementation
Foundation classes for specialized knowledge agents with coordination and validation
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import time
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentRole(Enum):
    """Define specialized agent roles"""
    TOPOLOGY_EXPERT = "topology_expert"
    CASE_ANALYST = "case_analyst"
    GITHUB_SPECIALIST = "github_specialist"
    VALIDATION_COORDINATOR = "validation_coordinator"
    QUERY_ORCHESTRATOR = "query_orchestrator"
    SYNTHESIS_ENGINE = "synthesis_engine"

class KnowledgeConfidence(Enum):
    """Knowledge confidence levels"""
    HIGH = 0.9
    MEDIUM = 0.7
    LOW = 0.5
    UNCERTAIN = 0.3

@dataclass
class KnowledgeFragment:
    """Individual piece of knowledge with metadata"""
    content: str
    source: str
    confidence: float
    agent_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    validation_status: str = "pending"
    related_fragments: List[str] = field(default_factory=list)

@dataclass
class AgentQuery:
    """Structured query between agents"""
    query_id: str
    content: str
    context: Dict[str, Any]
    requester_id: str
    priority: int = 1
    timeout: int = 30
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class AgentResponse:
    """Structured response from agents"""
    query_id: str
    agent_id: str
    knowledge_fragments: List[KnowledgeFragment]
    confidence: float
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseKnowledgeAgent(ABC):
    """Base class for all knowledge agents"""
    
    def __init__(self, agent_id: str, role: AgentRole, knowledge_domains: List[str]):
        self.agent_id = agent_id
        self.role = role
        self.knowledge_domains = knowledge_domains
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        self.active_queries: Dict[str, AgentQuery] = {}
        self.knowledge_cache: Dict[str, List[KnowledgeFragment]] = {}
        self.performance_metrics = {
            "queries_processed": 0,
            "avg_response_time": 0.0,
            "confidence_scores": [],
            "validation_success_rate": 0.0
        }
        
    @abstractmethod
    async def process_query(self, query: AgentQuery) -> AgentResponse:
        """Process a query and return knowledge fragments"""
        pass
    
    @abstractmethod
    async def validate_knowledge(self, fragment: KnowledgeFragment) -> bool:
        """Validate a knowledge fragment"""
        pass
    
    async def can_handle_query(self, query: AgentQuery) -> Tuple[bool, float]:
        """Determine if this agent can handle the query and with what confidence"""
        query_lower = query.content.lower()
        
        # Check if query relates to agent's knowledge domains
        relevance_score = 0.0
        for domain in self.knowledge_domains:
            if domain.lower() in query_lower:
                relevance_score += 0.3
        
        # Additional context-based scoring
        context_relevance = await self._assess_context_relevance(query.context)
        total_score = min(1.0, relevance_score + context_relevance)
        
        return total_score > 0.3, total_score
    
    async def _assess_context_relevance(self, context: Dict[str, Any]) -> float:
        """Assess relevance based on query context"""
        relevance = 0.0
        
        # Check for relevant context keys
        relevant_keys = {'services', 'symptoms', 'case_type', 'topology', 'github_repo'}
        for key in relevant_keys:
            if key in context:
                relevance += 0.1
        
        return min(0.4, relevance)
    
    def update_performance_metrics(self, response_time: float, confidence: float, validation_success: bool):
        """Update agent performance metrics"""
        self.performance_metrics["queries_processed"] += 1
        
        # Update average response time
        current_avg = self.performance_metrics["avg_response_time"]
        count = self.performance_metrics["queries_processed"]
        self.performance_metrics["avg_response_time"] = ((current_avg * (count - 1)) + response_time) / count
        
        # Track confidence scores
        self.performance_metrics["confidence_scores"].append(confidence)
        
        # Update validation success rate
        if hasattr(self, '_validation_attempts'):
            self._validation_attempts += 1
            if validation_success:
                self._validation_successes = getattr(self, '_validation_successes', 0) + 1
            self.performance_metrics["validation_success_rate"] = self._validation_successes / self._validation_attempts
        else:
            self._validation_attempts = 1
            self._validation_successes = 1 if validation_success else 0
            self.performance_metrics["validation_success_rate"] = self._validation_successes

class AgentCommunicationHub:
    """Central communication hub for agent coordination"""
    
    def __init__(self):
        self.agents: Dict[str, BaseKnowledgeAgent] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.query_routing_table: Dict[str, List[str]] = {}
        self.collaboration_history: List[Dict[str, Any]] = []
        
    def register_agent(self, agent: BaseKnowledgeAgent):
        """Register an agent with the communication hub"""
        self.agents[agent.agent_id] = agent
        logger.info(f"🤖 Registered agent: {agent.agent_id} ({agent.role.value})")
        
    async def route_query(self, query: AgentQuery) -> List[AgentResponse]:
        """Route a query to appropriate agents"""
        suitable_agents = []
        
        # Find agents that can handle the query
        for agent_id, agent in self.agents.items():
            can_handle, confidence = await agent.can_handle_query(query)
            if can_handle:
                suitable_agents.append((agent_id, confidence))
        
        # Sort by confidence
        suitable_agents.sort(key=lambda x: x[1], reverse=True)
        
        # Execute queries in parallel
        tasks = []
        for agent_id, confidence in suitable_agents[:3]:  # Limit to top 3 agents
            agent = self.agents[agent_id]
            tasks.append(agent.process_query(query))
        
        if not tasks:
            logger.warning(f"No suitable agents found for query: {query.content[:50]}...")
            return []
        
        # Wait for responses
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid responses
        valid_responses = [r for r in responses if isinstance(r, AgentResponse)]
        
        # Log collaboration
        self.collaboration_history.append({
            "query_id": query.query_id,
            "agents_involved": [r.agent_id for r in valid_responses],
            "timestamp": datetime.now(),
            "response_count": len(valid_responses)
        })
        
        return valid_responses

class KnowledgeValidator:
    """Cross-source validation system"""
    
    def __init__(self):
        self.validation_rules: Dict[str, callable] = {}
        self.consistency_cache: Dict[str, Dict[str, Any]] = {}
        
    async def validate_cross_source(self, fragments: List[KnowledgeFragment]) -> Dict[str, Any]:
        """Validate consistency across multiple knowledge fragments"""
        validation_result = {
            "overall_confidence": 0.0,
            "consistency_score": 0.0,
            "conflicts": [],
            "validated_fragments": [],
            "recommendations": []
        }
        
        if len(fragments) < 2:
            if fragments:
                validation_result["overall_confidence"] = fragments[0].confidence
                validation_result["consistency_score"] = 1.0
                validation_result["validated_fragments"] = fragments
            return validation_result
        
        # Check for content consistency
        content_similarity = await self._check_content_consistency(fragments)
        validation_result["consistency_score"] = content_similarity
        
        # Check for conflicts
        conflicts = await self._detect_conflicts(fragments)
        validation_result["conflicts"] = conflicts
        
        # Calculate overall confidence
        avg_confidence = sum(f.confidence for f in fragments) / len(fragments)
        consistency_penalty = max(0, 1 - len(conflicts) * 0.2)
        validation_result["overall_confidence"] = avg_confidence * consistency_penalty * content_similarity
        
        # Filter validated fragments
        confidence_threshold = 0.6
        validation_result["validated_fragments"] = [
            f for f in fragments if f.confidence >= confidence_threshold
        ]
        
        # Generate recommendations
        validation_result["recommendations"] = await self._generate_recommendations(
            fragments, conflicts, content_similarity
        )
        
        return validation_result
    
    async def _check_content_consistency(self, fragments: List[KnowledgeFragment]) -> float:
        """Check consistency between fragment contents"""
        if len(fragments) < 2:
            return 1.0
        
        # Simple keyword overlap analysis
        all_keywords = []
        fragment_keywords = []
        
        for fragment in fragments:
            keywords = set(fragment.content.lower().split())
            fragment_keywords.append(keywords)
            all_keywords.extend(keywords)
        
        if not all_keywords:
            return 0.5
        
        # Calculate pairwise similarity
        similarities = []
        for i in range(len(fragment_keywords)):
            for j in range(i + 1, len(fragment_keywords)):
                kw1, kw2 = fragment_keywords[i], fragment_keywords[j]
                if kw1 or kw2:
                    intersection = len(kw1 & kw2)
                    union = len(kw1 | kw2)
                    similarity = intersection / union if union > 0 else 0
                    similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 0.5
    
    async def _detect_conflicts(self, fragments: List[KnowledgeFragment]) -> List[Dict[str, Any]]:
        """Detect conflicts between knowledge fragments"""
        conflicts = []
        
        # Simple conflict detection based on contradictory keywords
        conflict_pairs = [
            ("enabled", "disabled"),
            ("working", "failing"),
            ("healthy", "unhealthy"),
            ("connected", "disconnected"),
            ("true", "false"),
            ("yes", "no")
        ]
        
        for i, frag1 in enumerate(fragments):
            for j, frag2 in enumerate(fragments[i+1:], i+1):
                content1 = frag1.content.lower()
                content2 = frag2.content.lower()
                
                for word1, word2 in conflict_pairs:
                    if word1 in content1 and word2 in content2:
                        conflicts.append({
                            "type": "contradictory_statements",
                            "fragment_ids": [i, j],
                            "conflict_terms": [word1, word2],
                            "confidence_impact": 0.3
                        })
        
        return conflicts
    
    async def _generate_recommendations(self, fragments: List[KnowledgeFragment], 
                                      conflicts: List[Dict[str, Any]], 
                                      consistency_score: float) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if consistency_score < 0.7:
            recommendations.append("Consider validating information from additional sources")
        
        if conflicts:
            recommendations.append(f"Detected {len(conflicts)} potential conflicts - review conflicting information")
        
        if len(fragments) == 1:
            recommendations.append("Single source information - consider cross-validation")
        
        # Confidence-based recommendations
        low_confidence_count = sum(1 for f in fragments if f.confidence < 0.6)
        if low_confidence_count > 0:
            recommendations.append(f"{low_confidence_count} fragments have low confidence - verify accuracy")
        
        return recommendations

# Export main classes
__all__ = [
    'BaseKnowledgeAgent', 
    'AgentCommunicationHub', 
    'KnowledgeValidator',
    'AgentRole', 
    'KnowledgeConfidence', 
    'KnowledgeFragment', 
    'AgentQuery', 
    'AgentResponse'
]