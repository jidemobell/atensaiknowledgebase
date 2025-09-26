#!/usr/bin/env python3
"""
Multi-Agent Orchestration System - Phase 2 Implementation
Agent coordination, dynamic source management, and cross-source validation
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import uuid

from multi_agent_foundation import (
    BaseKnowledgeAgent, AgentCommunicationHub, KnowledgeValidator,
    AgentQuery, AgentResponse, KnowledgeFragment, AgentRole
)
from specialized_knowledge_agents import (
    TopologyAgent, CaseAnalysisAgent, GitHubSourceAgent
)

logger = logging.getLogger(__name__)

@dataclass
class QueryContext:
    """Enhanced query context with temporal and relational information"""
    original_query: str
    user_context: Dict[str, Any]
    session_id: str
    query_history: List[str] = field(default_factory=list)
    temporal_context: Dict[str, Any] = field(default_factory=dict)
    related_queries: List[str] = field(default_factory=list)
    source_preferences: Dict[str, float] = field(default_factory=dict)

@dataclass
class SourcePerformance:
    """Track source performance metrics"""
    source_id: str
    total_queries: int = 0
    successful_responses: int = 0
    avg_response_time: float = 0.0
    avg_confidence: float = 0.0
    validation_success_rate: float = 0.0
    last_used: Optional[datetime] = None
    reliability_score: float = 0.5

class DynamicSourceManager:
    """Intelligent source selection and management"""
    
    def __init__(self):
        self.source_performance: Dict[str, SourcePerformance] = {}
        self.query_patterns: Dict[str, List[str]] = {}
        self.temporal_weights: Dict[str, float] = {
            "recency": 0.3,
            "frequency": 0.2,
            "success_rate": 0.3,
            "confidence": 0.2
        }
        
    def record_source_usage(self, source_id: str, response_time: float, 
                          confidence: float, validation_success: bool):
        """Record source usage metrics"""
        if source_id not in self.source_performance:
            self.source_performance[source_id] = SourcePerformance(source_id=source_id)
        
        perf = self.source_performance[source_id]
        perf.total_queries += 1
        perf.last_used = datetime.now()
        
        if confidence > 0.5:  # Consider successful if confidence > 0.5
            perf.successful_responses += 1
        
        # Update rolling averages
        alpha = 0.2  # Learning rate
        perf.avg_response_time = (1 - alpha) * perf.avg_response_time + alpha * response_time
        perf.avg_confidence = (1 - alpha) * perf.avg_confidence + alpha * confidence
        
        # Update validation success rate
        if hasattr(perf, '_validation_attempts'):
            perf._validation_attempts += 1
            if validation_success:
                perf._validation_successes = getattr(perf, '_validation_successes', 0) + 1
        else:
            perf._validation_attempts = 1
            perf._validation_successes = 1 if validation_success else 0
        
        perf.validation_success_rate = perf._validation_successes / perf._validation_attempts
        
        # Calculate overall reliability score
        success_rate = perf.successful_responses / perf.total_queries
        perf.reliability_score = (
            self.temporal_weights["success_rate"] * success_rate +
            self.temporal_weights["confidence"] * perf.avg_confidence +
            self.temporal_weights["recency"] * self._calculate_recency_score(perf.last_used)
        )
    
    def _calculate_recency_score(self, last_used: Optional[datetime]) -> float:
        """Calculate recency score based on last usage"""
        if not last_used:
            return 0.0
        
        time_diff = datetime.now() - last_used
        hours_ago = time_diff.total_seconds() / 3600
        
        # Exponential decay: score decreases as time increases
        return max(0.1, 1.0 * (0.9 ** hours_ago))
    
    async def select_optimal_sources(self, query_context: QueryContext, 
                                   available_agents: List[BaseKnowledgeAgent]) -> List[BaseKnowledgeAgent]:
        """Select optimal sources based on context and performance"""
        
        # Analyze query for source preferences
        query_keywords = self._extract_keywords(query_context.original_query)
        
        # Score each agent
        agent_scores = []
        for agent in available_agents:
            score = await self._calculate_agent_score(agent, query_context, query_keywords)
            agent_scores.append((agent, score))
        
        # Sort by score and select top agents
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Dynamic selection: take top performers or minimum 2 agents
        selected = []
        threshold = 0.6
        for agent, score in agent_scores:
            if score >= threshold or len(selected) < 2:
                selected.append(agent)
            if len(selected) >= 4:  # Maximum 4 agents to avoid overwhelming
                break
        
        logger.info(f"Selected {len(selected)} agents for query processing")
        return selected
    
    async def _calculate_agent_score(self, agent: BaseKnowledgeAgent, 
                                   context: QueryContext, keywords: List[str]) -> float:
        """Calculate agent suitability score"""
        score = 0.0
        
        # Base capability score
        can_handle, base_confidence = await agent.can_handle_query(
            AgentQuery(
                query_id=str(uuid.uuid4()),
                content=context.original_query,
                context=context.user_context,
                requester_id="orchestrator"
            )
        )
        
        if not can_handle:
            return 0.0
        
        score += base_confidence * 0.4
        
        # Performance history score
        if agent.agent_id in self.source_performance:
            perf = self.source_performance[agent.agent_id]
            score += perf.reliability_score * 0.3
        
        # Domain relevance score
        domain_relevance = self._calculate_domain_relevance(agent.knowledge_domains, keywords)
        score += domain_relevance * 0.3
        
        return min(1.0, score)
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract relevant keywords from query"""
        # Simple keyword extraction - could be enhanced with NLP
        import re
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Filter out common words
        stopwords = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        
        return keywords[:10]  # Limit to top 10 keywords
    
    def _calculate_domain_relevance(self, domains: List[str], keywords: List[str]) -> float:
        """Calculate how relevant an agent's domains are to the query keywords"""
        if not domains or not keywords:
            return 0.0
        
        relevance_score = 0.0
        for domain in domains:
            domain_words = domain.lower().split('-')
            for keyword in keywords:
                if keyword in domain_words or any(keyword in word for word in domain_words):
                    relevance_score += 1.0
        
        # Normalize by the number of domains
        return min(1.0, relevance_score / len(domains))

class MultiAgentOrchestrator:
    """Main orchestrator for multi-agent knowledge system"""
    
    def __init__(self):
        self.communication_hub = AgentCommunicationHub()
        self.knowledge_validator = KnowledgeValidator()
        self.source_manager = DynamicSourceManager()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize agents
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize and register all specialized agents"""
        agents = [
            TopologyAgent(),
            CaseAnalysisAgent(),
            GitHubSourceAgent()
        ]
        
        for agent in agents:
            self.communication_hub.register_agent(agent)
        
        logger.info(f"Initialized {len(agents)} specialized agents")
    
    async def process_query(self, query: str, context: Dict[str, Any], 
                          session_id: str = None) -> Dict[str, Any]:
        """Process a query through the multi-agent system"""
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Create enhanced query context
        query_context = QueryContext(
            original_query=query,
            user_context=context,
            session_id=session_id,
            query_history=self._get_session_history(session_id),
            temporal_context=self._build_temporal_context(query, context)
        )
        
        # Select optimal agents
        available_agents = list(self.communication_hub.agents.values())
        selected_agents = await self.source_manager.select_optimal_sources(query_context, available_agents)
        
        if not selected_agents:
            return {
                "response": "No suitable knowledge agents available for this query.",
                "confidence": 0.0,
                "sources": [],
                "processing_time": 0.0
            }
        
        # Create agent query
        agent_query = AgentQuery(
            query_id=str(uuid.uuid4()),
            content=query,
            context=context,
            requester_id="orchestrator"
        )
        
        # Execute parallel processing
        start_time = datetime.now()
        responses = await self._execute_parallel_processing(selected_agents, agent_query)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Validate and synthesize responses
        synthesis_result = await self._synthesize_responses(responses, query_context)
        
        # Update source performance metrics
        for response in responses:
            self.source_manager.record_source_usage(
                response.agent_id,
                response.processing_time,
                response.confidence,
                synthesis_result.get("validation_success", False)
            )
        
        # Update session history
        self._update_session_history(session_id, query, synthesis_result)
        
        # Format final response
        return {
            "response": synthesis_result["synthesized_content"],
            "confidence": synthesis_result["overall_confidence"],
            "sources": synthesis_result["source_breakdown"],
            "processing_time": processing_time,
            "agents_consulted": len(responses),
            "validation_results": synthesis_result.get("validation_results", {}),
            "recommendations": synthesis_result.get("recommendations", [])
        }
    
    async def _execute_parallel_processing(self, agents: List[BaseKnowledgeAgent], 
                                         query: AgentQuery) -> List[AgentResponse]:
        """Execute parallel processing across selected agents"""
        
        tasks = []
        for agent in agents:
            tasks.append(agent.process_query(query))
        
        # Execute with timeout
        try:
            responses = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            logger.warning("Some agents timed out during processing")
            responses = [r for r in responses if isinstance(r, AgentResponse)]
        
        # Filter valid responses
        valid_responses = [r for r in responses if isinstance(r, AgentResponse)]
        
        logger.info(f"Received {len(valid_responses)} valid responses from {len(agents)} agents")
        return valid_responses
    
    async def _synthesize_responses(self, responses: List[AgentResponse], 
                                  context: QueryContext) -> Dict[str, Any]:
        """Synthesize responses from multiple agents"""
        
        if not responses:
            return {
                "synthesized_content": "No valid responses received from knowledge agents.",
                "overall_confidence": 0.0,
                "source_breakdown": [],
                "validation_results": {}
            }
        
        # Collect all knowledge fragments
        all_fragments = []
        for response in responses:
            all_fragments.extend(response.knowledge_fragments)
        
        # Cross-source validation
        validation_results = await self.knowledge_validator.validate_cross_source(all_fragments)
        
        # Group fragments by topic/theme
        grouped_fragments = self._group_fragments_by_theme(all_fragments)
        
        # Generate synthesized content
        synthesized_content = await self._generate_synthesized_content(
            grouped_fragments, validation_results, context
        )
        
        # Create source breakdown
        source_breakdown = self._create_source_breakdown(responses)
        
        return {
            "synthesized_content": synthesized_content,
            "overall_confidence": validation_results["overall_confidence"],
            "source_breakdown": source_breakdown,
            "validation_results": validation_results,
            "validation_success": validation_results["consistency_score"] > 0.7,
            "recommendations": validation_results.get("recommendations", [])
        }
    
    def _group_fragments_by_theme(self, fragments: List[KnowledgeFragment]) -> Dict[str, List[KnowledgeFragment]]:
        """Group knowledge fragments by common themes"""
        themes = {}
        
        for fragment in fragments:
            # Simple theme detection based on tags
            primary_theme = "general"
            if fragment.tags:
                primary_theme = fragment.tags[0]  # Use first tag as primary theme
            
            if primary_theme not in themes:
                themes[primary_theme] = []
            themes[primary_theme].append(fragment)
        
        return themes
    
    async def _generate_synthesized_content(self, grouped_fragments: Dict[str, List[KnowledgeFragment]], 
                                          validation_results: Dict[str, Any], 
                                          context: QueryContext) -> str:
        """Generate synthesized content from grouped fragments"""
        
        content_parts = []
        
        # Add validation notice if there are concerns
        if validation_results["consistency_score"] < 0.7:
            content_parts.append("⚠️ **Note**: Multiple sources provided varying information. Results have been cross-validated.\n")
        
        # Process each theme
        for theme, fragments in grouped_fragments.items():
            if not fragments:
                continue
            
            # Sort fragments by confidence
            fragments.sort(key=lambda f: f.confidence, reverse=True)
            
            # Add theme header
            theme_title = theme.replace("-", " ").replace("_", " ").title()
            content_parts.append(f"## {theme_title}\n")
            
            # Add highest confidence content from this theme
            primary_fragment = fragments[0]
            content_parts.append(primary_fragment.content)
            
            # Add supporting information from other fragments
            if len(fragments) > 1:
                supporting_info = []
                for fragment in fragments[1:3]:  # Limit to 2 additional fragments
                    if fragment.confidence > 0.6:  # Only include high-confidence supporting info
                        # Extract key points (first 2 bullet points or sentences)
                        lines = fragment.content.split('\n')
                        key_lines = [line for line in lines[:5] if line.strip() and ('•' in line or '**' in line)][:2]
                        if key_lines:
                            supporting_info.extend(key_lines)
                
                if supporting_info:
                    content_parts.append("\n**Additional Insights:**")
                    content_parts.extend(supporting_info)
            
            content_parts.append("\n")
        
        # Add recommendations if available
        if validation_results.get("recommendations"):
            content_parts.append("## Recommendations\n")
            for rec in validation_results["recommendations"][:3]:  # Limit to 3 recommendations
                content_parts.append(f"• {rec}")
            content_parts.append("\n")
        
        return "\n".join(content_parts)
    
    def _create_source_breakdown(self, responses: List[AgentResponse]) -> List[Dict[str, Any]]:
        """Create breakdown of sources consulted"""
        breakdown = []
        
        for response in responses:
            breakdown.append({
                "agent_id": response.agent_id,
                "confidence": response.confidence,
                "processing_time": response.processing_time,
                "fragments_provided": len(response.knowledge_fragments),
                "metadata": response.metadata
            })
        
        return breakdown
    
    def _get_session_history(self, session_id: str) -> List[str]:
        """Get query history for session"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id].get("query_history", [])
        return []
    
    def _build_temporal_context(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build temporal context for the query"""
        return {
            "timestamp": datetime.now().isoformat(),
            "hour_of_day": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
            "context_age": 0  # Could track how old the context information is
        }
    
    def _update_session_history(self, session_id: str, query: str, result: Dict[str, Any]):
        """Update session history with query and result"""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "query_history": [],
                "created_at": datetime.now(),
                "last_activity": datetime.now()
            }
        
        session = self.active_sessions[session_id]
        session["query_history"].append(query)
        session["last_activity"] = datetime.now()
        
        # Keep only last 10 queries to prevent memory bloat
        if len(session["query_history"]) > 10:
            session["query_history"] = session["query_history"][-10:]

# Factory function for easy instantiation
def create_multi_agent_system() -> MultiAgentOrchestrator:
    """Create and initialize the multi-agent system"""
    return MultiAgentOrchestrator()

# Export main classes
__all__ = ['MultiAgentOrchestrator', 'DynamicSourceManager', 'QueryContext', 'create_multi_agent_system']