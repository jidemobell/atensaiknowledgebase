"""
Multi-Agent Knowledge Fusion Architecture
==========================================

This module implements a sophisticated multi-agent system that goes beyond traditional RAG
by providing specialized agents for query analysis, context management, and knowledge synthesis.

Key Differentiators from Basic RAG:
- Intent-aware query processing with semantic understanding
- Temporal reasoning and historical context awareness
- Cross-source validation and credibility scoring
- Dynamic agent collaboration and knowledge routing
- Contextual memory with conversation flow understanding
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class KnowledgeItem:
    """Structured representation of knowledge with metadata"""
    content: str
    source: str
    source_type: str  # 'github', 'web', 'api', 'document', 'conversation'
    timestamp: datetime
    confidence: float
    credibility_score: float
    tags: List[str]
    context: Dict[str, Any]
    version: str = "1.0"

@dataclass
class QueryIntent:
    """Analyzed query with extracted intent and context"""
    original_query: str
    intent_type: str
    entities: List[str]
    temporal_context: Optional[str]  # 'recent', 'historical', 'current'
    complexity_level: str  # 'simple', 'medium', 'complex'
    required_sources: List[str]
    confidence: float

@dataclass
class AgentResponse:
    """Response from an individual agent"""
    agent_name: str
    content: Any
    confidence: float
    reasoning: str
    metadata: Dict[str, Any]
    execution_time: float

class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system"""
    
    def __init__(self, name: str, capabilities: List[str]):
        self.name = name
        self.capabilities = capabilities
        self.memory = {}
        self.performance_metrics = {
            'queries_processed': 0,
            'average_confidence': 0.0,
            'average_execution_time': 0.0
        }
    
    @abstractmethod
    async def process(self, input_data: Any, context: Dict[str, Any]) -> AgentResponse:
        """Process input and return agent response"""
        pass
    
    def update_metrics(self, confidence: float, execution_time: float):
        """Update agent performance metrics"""
        self.performance_metrics['queries_processed'] += 1
        current_avg_conf = self.performance_metrics['average_confidence']
        current_avg_time = self.performance_metrics['average_execution_time']
        queries = self.performance_metrics['queries_processed']
        
        # Rolling average calculation
        self.performance_metrics['average_confidence'] = (
            (current_avg_conf * (queries - 1) + confidence) / queries
        )
        self.performance_metrics['average_execution_time'] = (
            (current_avg_time * (queries - 1) + execution_time) / queries
        )

class QueryAgent(BaseAgent):
    """
    Specialized agent for query analysis and intent detection
    Goes beyond keyword matching to understand semantic intent
    """
    
    def __init__(self):
        super().__init__("QueryAgent", ["intent_detection", "entity_extraction", "query_classification"])
        self.intent_patterns = {
            'troubleshooting': [
                r'error|issue|problem|fail|broken|not working|debug',
                r'fix|solve|resolve|help|troubleshoot'
            ],
            'information_seeking': [
                r'what is|how to|explain|describe|tell me about',
                r'documentation|guide|manual|tutorial'
            ],
            'code_analysis': [
                r'code|function|class|method|implementation',
                r'review|analyze|optimize|refactor'
            ],
            'historical_inquiry': [
                r'previous|before|history|past|similar case',
                r'last time|when did|how often'
            ],
            'comparative_analysis': [
                r'compare|difference|better|versus|vs',
                r'alternative|option|choice'
            ],
            'prediction': [
                r'will|future|predict|expect|likely',
                r'trend|forecast|projection'
            ]
        }
        
        self.entity_extractors = {
            'technical_terms': r'\b[A-Z]{2,}(?:[_-][A-Z0-9]+)*\b',  # API names, tech terms
            'file_paths': r'(?:/[^/\s]+)+/?|\w+\.\w+',
            'error_codes': r'\b[A-Z]{1,3}[-_]?\d{3,4}\b',
            'versions': r'v?\d+\.\d+(?:\.\d+)?',
            'urls': r'https?://[^\s]+',
            'ips': r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        }
    
    async def process(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """Analyze query for intent, entities, and context"""
        start_time = datetime.now()
        
        # Intent detection
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score += matches
            intent_scores[intent] = score / len(patterns)
        
        # Primary intent selection
        primary_intent = max(intent_scores, key=intent_scores.get) if intent_scores else 'general'
        intent_confidence = intent_scores.get(primary_intent, 0.0)
        
        # Entity extraction
        entities = {}
        for entity_type, pattern in self.entity_extractors.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                entities[entity_type] = list(set(matches))  # Remove duplicates
        
        # Temporal context detection
        temporal_indicators = {
            'recent': r'recent|latest|current|now|today|this week',
            'historical': r'old|previous|past|before|history|archive',
            'future': r'future|will|going to|plan|upcoming'
        }
        
        temporal_context = None
        for temporal_type, pattern in temporal_indicators.items():
            if re.search(pattern, query, re.IGNORECASE):
                temporal_context = temporal_type
                break
        
        # Complexity assessment
        complexity_indicators = {
            'simple': ['what', 'who', 'when', 'where'],
            'medium': ['how', 'why', 'compare', 'explain'],
            'complex': ['analyze', 'optimize', 'design', 'architect', 'integrate']
        }
        
        complexity_level = 'simple'
        query_lower = query.lower()
        for level, indicators in complexity_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                complexity_level = level
        
        # Source requirement analysis
        required_sources = self._determine_required_sources(primary_intent, entities, temporal_context)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        query_intent = QueryIntent(
            original_query=query,
            intent_type=primary_intent,
            entities=list(entities.keys()),
            temporal_context=temporal_context,
            complexity_level=complexity_level,
            required_sources=required_sources,
            confidence=intent_confidence
        )
        
        response = AgentResponse(
            agent_name=self.name,
            content=query_intent,
            confidence=intent_confidence,
            reasoning=f"Detected intent: {primary_intent} with entities: {list(entities.keys())}",
            metadata={
                'intent_scores': intent_scores,
                'extracted_entities': entities,
                'temporal_context': temporal_context,
                'complexity_level': complexity_level
            },
            execution_time=execution_time
        )
        
        self.update_metrics(intent_confidence, execution_time)
        return response
    
    def _determine_required_sources(self, intent: str, entities: Dict, temporal_context: str) -> List[str]:
        """Determine which knowledge sources are needed based on analysis"""
        source_mapping = {
            'troubleshooting': ['cases', 'github_code', 'documentation', 'conversations'],
            'information_seeking': ['documentation', 'web_content', 'conversations'],
            'code_analysis': ['github_code', 'documentation', 'api_data'],
            'historical_inquiry': ['cases', 'conversations', 'database_logs'],
            'comparative_analysis': ['documentation', 'web_content', 'api_data'],
            'prediction': ['cases', 'database_logs', 'api_data']
        }
        
        base_sources = source_mapping.get(intent, ['documentation'])
        
        # Add sources based on entities
        if 'technical_terms' in entities:
            base_sources.extend(['api_data', 'github_code'])
        if 'file_paths' in entities:
            base_sources.append('github_code')
        if 'error_codes' in entities:
            base_sources.extend(['cases', 'documentation'])
        
        # Temporal context adjustments
        if temporal_context == 'historical':
            base_sources.extend(['cases', 'database_logs'])
        elif temporal_context == 'recent':
            base_sources.extend(['conversations', 'api_data'])
        
        return list(set(base_sources))  # Remove duplicates

class ContextAgent(BaseAgent):
    """
    Manages conversational context and memory
    Provides temporal reasoning and relevance scoring
    """
    
    def __init__(self):
        super().__init__("ContextAgent", ["memory_management", "relevance_scoring", "temporal_reasoning"])
        self.conversation_memory = {}
        self.knowledge_graph = {}  # Connections between concepts
        self.temporal_index = {}   # Time-based knowledge organization
    
    async def process(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AgentResponse:
        """Build and maintain conversational context"""
        start_time = datetime.now()
        
        conversation_id = context.get('conversation_id', 'default')
        query_intent = input_data.get('query_intent')
        
        # Initialize conversation memory if needed
        if conversation_id not in self.conversation_memory:
            self.conversation_memory[conversation_id] = {
                'messages': [],
                'context_stack': [],
                'active_topics': [],
                'user_preferences': {},
                'session_start': datetime.now()
            }
        
        conv_memory = self.conversation_memory[conversation_id]
        
        # Analyze conversation flow
        context_analysis = self._analyze_conversation_context(conv_memory, query_intent)
        
        # Build temporal context
        temporal_context = self._build_temporal_context(query_intent, conv_memory)
        
        # Calculate relevance scores for historical knowledge
        relevance_scores = self._calculate_relevance_scores(query_intent, temporal_context)
        
        # Update knowledge graph
        self._update_knowledge_graph(query_intent, context_analysis)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        context_data = {
            'conversation_flow': context_analysis,
            'temporal_context': temporal_context,
            'relevance_scores': relevance_scores,
            'active_topics': conv_memory['active_topics'],
            'session_duration': (datetime.now() - conv_memory['session_start']).total_seconds()
        }
        
        confidence = self._calculate_context_confidence(context_analysis, temporal_context)
        
        response = AgentResponse(
            agent_name=self.name,
            content=context_data,
            confidence=confidence,
            reasoning=f"Built context with {len(context_analysis['related_topics'])} related topics",
            metadata={
                'conversation_length': len(conv_memory['messages']),
                'active_topics_count': len(conv_memory['active_topics']),
                'knowledge_graph_size': len(self.knowledge_graph)
            },
            execution_time=execution_time
        )
        
        self.update_metrics(confidence, execution_time)
        return response
    
    def _analyze_conversation_context(self, conv_memory: Dict, query_intent: QueryIntent) -> Dict[str, Any]:
        """Analyze conversation flow and topic evolution"""
        recent_messages = conv_memory['messages'][-5:]  # Last 5 messages
        
        # Topic continuity analysis
        current_topics = self._extract_topics(query_intent.original_query)
        related_topics = []
        
        for msg in recent_messages:
            msg_topics = self._extract_topics(msg.get('content', ''))
            related_topics.extend(msg_topics)
        
        # Topic shift detection
        topic_shift = len(set(current_topics) - set(related_topics)) > 0
        
        return {
            'current_topics': current_topics,
            'related_topics': list(set(related_topics)),
            'topic_shift_detected': topic_shift,
            'conversation_depth': len(conv_memory['messages']),
            'context_continuity': 1.0 - (0.2 if topic_shift else 0.0)
        }
    
    def _build_temporal_context(self, query_intent: QueryIntent, conv_memory: Dict) -> Dict[str, Any]:
        """Build temporal context for knowledge retrieval"""
        now = datetime.now()
        
        # Time-based knowledge filtering
        if query_intent.temporal_context == 'recent':
            time_filter = now - timedelta(days=7)
        elif query_intent.temporal_context == 'historical':
            time_filter = now - timedelta(days=365)
        else:
            time_filter = now - timedelta(days=30)  # Default
        
        return {
            'temporal_filter': time_filter,
            'temporal_context_type': query_intent.temporal_context,
            'session_context': conv_memory.get('session_start'),
            'time_sensitivity': 0.8 if query_intent.temporal_context else 0.3
        }
    
    def _calculate_relevance_scores(self, query_intent: QueryIntent, temporal_context: Dict) -> Dict[str, float]:
        """Calculate relevance scores for different knowledge sources"""
        base_scores = {
            'recent_conversations': 0.8 if temporal_context['temporal_context_type'] == 'recent' else 0.4,
            'documentation': 0.9 if query_intent.intent_type == 'information_seeking' else 0.6,
            'code_repositories': 0.9 if query_intent.intent_type == 'code_analysis' else 0.5,
            'historical_cases': 0.9 if temporal_context['temporal_context_type'] == 'historical' else 0.6,
            'api_data': 0.7 if 'technical_terms' in query_intent.entities else 0.4
        }
        
        # Adjust scores based on query complexity
        complexity_multiplier = {
            'simple': 1.0,
            'medium': 1.1,
            'complex': 1.2
        }
        
        multiplier = complexity_multiplier.get(query_intent.complexity_level, 1.0)
        
        return {source: score * multiplier for source, score in base_scores.items()}
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text using simple NLP"""
        # Simple topic extraction - in production, use proper NLP
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        return [word for word in words if word not in common_words and len(word) > 3]
    
    def _update_knowledge_graph(self, query_intent: QueryIntent, context_analysis: Dict):
        """Update knowledge graph with new connections"""
        current_topics = context_analysis['current_topics']
        related_topics = context_analysis['related_topics']
        
        for topic in current_topics:
            if topic not in self.knowledge_graph:
                self.knowledge_graph[topic] = {'connections': set(), 'frequency': 0}
            
            self.knowledge_graph[topic]['frequency'] += 1
            self.knowledge_graph[topic]['connections'].update(related_topics)
    
    def _calculate_context_confidence(self, context_analysis: Dict, temporal_context: Dict) -> float:
        """Calculate confidence in context understanding"""
        base_confidence = 0.7
        
        # Boost confidence based on conversation continuity
        continuity_boost = context_analysis['context_continuity'] * 0.2
        
        # Boost confidence based on temporal context clarity
        temporal_boost = temporal_context['time_sensitivity'] * 0.1
        
        return min(1.0, base_confidence + continuity_boost + temporal_boost)

class SynthesisAgent(BaseAgent):
    """
    Knowledge synthesis and response generation agent
    Combines insights from multiple sources with cross-validation
    """
    
    def __init__(self):
        super().__init__("SynthesisAgent", ["knowledge_fusion", "response_generation", "source_validation"])
        self.synthesis_strategies = {
            'simple': self._simple_synthesis,
            'medium': self._contextual_synthesis,
            'complex': self._advanced_synthesis
        }
        self.credibility_weights = {
            'documentation': 0.9,
            'github_code': 0.8,
            'cases': 0.85,
            'conversations': 0.6,
            'web_content': 0.7,
            'api_data': 0.75
        }
    
    async def process(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AgentResponse:
        """Synthesize knowledge from multiple sources"""
        start_time = datetime.now()
        
        query_intent = input_data.get('query_intent')
        context_data = input_data.get('context_data')
        knowledge_items = input_data.get('knowledge_items', [])
        
        # Select synthesis strategy based on complexity
        strategy = self.synthesis_strategies.get(
            query_intent.complexity_level, 
            self._simple_synthesis
        )
        
        # Perform cross-source validation
        validated_knowledge = self._validate_cross_sources(knowledge_items)
        
        # Synthesize response using selected strategy
        synthesis_result = await strategy(query_intent, context_data, validated_knowledge)
        
        # Generate confidence score
        confidence = self._calculate_synthesis_confidence(validated_knowledge, synthesis_result)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        response = AgentResponse(
            agent_name=self.name,
            content=synthesis_result,
            confidence=confidence,
            reasoning=f"Synthesized from {len(validated_knowledge)} sources using {query_intent.complexity_level} strategy",
            metadata={
                'sources_used': [item.source for item in validated_knowledge],
                'validation_score': sum(item.credibility_score for item in validated_knowledge) / len(validated_knowledge) if validated_knowledge else 0,
                'synthesis_strategy': query_intent.complexity_level
            },
            execution_time=execution_time
        )
        
        self.update_metrics(confidence, execution_time)
        return response
    
    async def _simple_synthesis(self, query_intent: QueryIntent, context_data: Dict, knowledge_items: List[KnowledgeItem]) -> Dict[str, Any]:
        """Simple synthesis for straightforward queries"""
        if not knowledge_items:
            return {
                'response': "I don't have sufficient information to answer your query.",
                'synthesis_type': 'simple',
                'sources_consulted': 0
            }
        
        # Take the highest confidence item
        best_item = max(knowledge_items, key=lambda x: x.confidence * x.credibility_score)
        
        return {
            'response': best_item.content,
            'synthesis_type': 'simple',
            'primary_source': best_item.source,
            'sources_consulted': 1,
            'confidence_score': best_item.confidence
        }
    
    async def _contextual_synthesis(self, query_intent: QueryIntent, context_data: Dict, knowledge_items: List[KnowledgeItem]) -> Dict[str, Any]:
        """Contextual synthesis considering conversation flow"""
        if not knowledge_items:
            return {
                'response': "I need more information to provide a comprehensive answer.",
                'synthesis_type': 'contextual',
                'sources_consulted': 0
            }
        
        # Group by source type and weight by credibility
        source_groups = {}
        for item in knowledge_items:
            source_type = item.source_type
            if source_type not in source_groups:
                source_groups[source_type] = []
            source_groups[source_type].append(item)
        
        # Create weighted response
        response_parts = []
        for source_type, items in source_groups.items():
            if items:
                best_item = max(items, key=lambda x: x.confidence)
                weight = self.credibility_weights.get(source_type, 0.5)
                response_parts.append((best_item.content, weight, source_type))
        
        # Combine responses with weights
        if response_parts:
            # Sort by weight and combine
            response_parts.sort(key=lambda x: x[1], reverse=True)
            primary_response = response_parts[0][0]
            
            supporting_info = []
            for content, weight, source_type in response_parts[1:3]:  # Top 3 sources
                if weight > 0.6:  # Only high-credibility supporting info
                    supporting_info.append(f"Additionally, {source_type} indicates: {content[:100]}...")
            
            full_response = primary_response
            if supporting_info:
                full_response += "\n\n" + "\n".join(supporting_info)
            
            return {
                'response': full_response,
                'synthesis_type': 'contextual',
                'primary_source': response_parts[0][2],
                'supporting_sources': [item[2] for item in response_parts[1:3]],
                'sources_consulted': len(response_parts),
                'weighted_confidence': sum(item[1] for item in response_parts) / len(response_parts)
            }
        
        return await self._simple_synthesis(query_intent, context_data, knowledge_items)
    
    async def _advanced_synthesis(self, query_intent: QueryIntent, context_data: Dict, knowledge_items: List[KnowledgeItem]) -> Dict[str, Any]:
        """Advanced synthesis with conflict resolution and reasoning"""
        if not knowledge_items:
            return {
                'response': "This appears to be a complex query that requires information I don't currently have access to.",
                'synthesis_type': 'advanced',
                'sources_consulted': 0
            }
        
        # Detect conflicting information
        conflicts = self._detect_conflicts(knowledge_items)
        
        # Perform evidence-based synthesis
        synthesis_result = self._evidence_based_synthesis(knowledge_items, conflicts)
        
        # Generate reasoning chain
        reasoning_chain = self._generate_reasoning_chain(knowledge_items, synthesis_result)
        
        return {
            'response': synthesis_result['response'],
            'synthesis_type': 'advanced',
            'conflicts_detected': len(conflicts),
            'conflict_resolution': synthesis_result.get('conflict_resolution', []),
            'reasoning_chain': reasoning_chain,
            'sources_consulted': len(knowledge_items),
            'evidence_strength': synthesis_result.get('evidence_strength', 0.0)
        }
    
    def _validate_cross_sources(self, knowledge_items: List[KnowledgeItem]) -> List[KnowledgeItem]:
        """Validate knowledge across multiple sources"""
        if len(knowledge_items) <= 1:
            return knowledge_items
        
        validated_items = []
        
        for item in knowledge_items:
            # Basic validation checks
            if len(item.content.strip()) < 10:  # Too short
                continue
            
            if item.confidence < 0.3:  # Too low confidence
                continue
            
            # Cross-reference validation
            supporting_count = 0
            for other_item in knowledge_items:
                if other_item != item and self._items_support_each_other(item, other_item):
                    supporting_count += 1
            
            # Boost credibility if supported by other sources
            if supporting_count > 0:
                item.credibility_score = min(1.0, item.credibility_score + (supporting_count * 0.1))
            
            validated_items.append(item)
        
        return validated_items
    
    def _items_support_each_other(self, item1: KnowledgeItem, item2: KnowledgeItem) -> bool:
        """Check if two knowledge items support each other"""
        # Simple support detection using common keywords
        words1 = set(re.findall(r'\b\w+\b', item1.content.lower()))
        words2 = set(re.findall(r'\b\w+\b', item2.content.lower()))
        
        # Calculate overlap
        overlap = len(words1 & words2)
        total_unique = len(words1 | words2)
        
        return (overlap / total_unique) > 0.3 if total_unique > 0 else False
    
    def _detect_conflicts(self, knowledge_items: List[KnowledgeItem]) -> List[Dict[str, Any]]:
        """Detect conflicting information between sources"""
        conflicts = []
        
        for i, item1 in enumerate(knowledge_items):
            for j, item2 in enumerate(knowledge_items[i+1:], i+1):
                # Simple conflict detection based on contradiction keywords
                conflict_indicators = [
                    ('not', 'is'), ('false', 'true'), ('incorrect', 'correct'),
                    ('wrong', 'right'), ('no', 'yes'), ('never', 'always')
                ]
                
                content1_lower = item1.content.lower()
                content2_lower = item2.content.lower()
                
                for neg, pos in conflict_indicators:
                    if ((neg in content1_lower and pos in content2_lower) or 
                        (pos in content1_lower and neg in content2_lower)):
                        conflicts.append({
                            'item1_index': i,
                            'item2_index': j,
                            'conflict_type': f"{neg}_vs_{pos}",
                            'severity': 'medium'
                        })
        
        return conflicts
    
    def _evidence_based_synthesis(self, knowledge_items: List[KnowledgeItem], conflicts: List[Dict]) -> Dict[str, Any]:
        """Synthesize based on evidence strength"""
        if not knowledge_items:
            return {'response': 'No evidence available', 'evidence_strength': 0.0}
        
        # Weight items by credibility and confidence
        weighted_items = []
        for item in knowledge_items:
            evidence_score = (item.confidence * item.credibility_score * 
                            self.credibility_weights.get(item.source_type, 0.5))
            weighted_items.append((item, evidence_score))
        
        # Sort by evidence strength
        weighted_items.sort(key=lambda x: x[1], reverse=True)
        
        # Build response prioritizing strong evidence
        primary_item = weighted_items[0][0]
        response = primary_item.content
        
        # Add supporting evidence
        supporting_evidence = []
        for item, score in weighted_items[1:3]:  # Top 2 supporting items
            if score > 0.6:  # High evidence threshold
                supporting_evidence.append(f"This is supported by {item.source_type}: {item.content[:100]}...")
        
        if supporting_evidence:
            response += "\n\nSupporting evidence:\n" + "\n".join(supporting_evidence)
        
        # Handle conflicts if present
        conflict_resolution = []
        if conflicts:
            conflict_resolution.append("Note: Some conflicting information was found and resolved based on source credibility.")
        
        return {
            'response': response,
            'evidence_strength': weighted_items[0][1],
            'conflict_resolution': conflict_resolution
        }
    
    def _generate_reasoning_chain(self, knowledge_items: List[KnowledgeItem], synthesis_result: Dict) -> List[str]:
        """Generate reasoning chain for transparency"""
        reasoning = []
        
        reasoning.append(f"Analyzed {len(knowledge_items)} knowledge sources")
        
        source_types = list(set(item.source_type for item in knowledge_items))
        reasoning.append(f"Sources included: {', '.join(source_types)}")
        
        if synthesis_result.get('conflicts_detected', 0) > 0:
            reasoning.append(f"Resolved {synthesis_result['conflicts_detected']} conflicts based on source credibility")
        
        evidence_strength = synthesis_result.get('evidence_strength', 0.0)
        if evidence_strength > 0.8:
            reasoning.append("High confidence response based on strong evidence")
        elif evidence_strength > 0.6:
            reasoning.append("Moderate confidence response with good supporting evidence")
        else:
            reasoning.append("Lower confidence response - limited evidence available")
        
        return reasoning
    
    def _calculate_synthesis_confidence(self, knowledge_items: List[KnowledgeItem], synthesis_result: Dict) -> float:
        """Calculate overall confidence in synthesis"""
        if not knowledge_items:
            return 0.0
        
        # Base confidence from evidence strength
        evidence_confidence = synthesis_result.get('evidence_strength', 0.0)
        
        # Boost for multiple sources
        source_diversity = len(set(item.source_type for item in knowledge_items))
        diversity_boost = min(0.2, source_diversity * 0.05)
        
        # Penalty for conflicts
        conflicts = synthesis_result.get('conflicts_detected', 0)
        conflict_penalty = min(0.3, conflicts * 0.1)
        
        final_confidence = evidence_confidence + diversity_boost - conflict_penalty
        return max(0.0, min(1.0, final_confidence))

class MultiAgentOrchestrator:
    """
    Orchestrates the multi-agent system for knowledge fusion
    """
    
    def __init__(self):
        self.query_agent = QueryAgent()
        self.context_agent = ContextAgent()
        self.synthesis_agent = SynthesisAgent()
        
        self.knowledge_store = {}  # Simulated knowledge store
        self.orchestration_metrics = {
            'total_queries': 0,
            'average_response_time': 0.0,
            'agent_collaboration_success': 0.0
        }
    
    async def process_query(self, query: str, conversation_id: str = 'default', 
                          user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main entry point for multi-agent query processing"""
        start_time = datetime.now()
        
        try:
            # Phase 1: Query Analysis
            logger.info(f"Phase 1: Analyzing query with QueryAgent")
            query_response = await self.query_agent.process(query, {'conversation_id': conversation_id})
            query_intent = query_response.content
            
            # Phase 2: Context Building
            logger.info(f"Phase 2: Building context with ContextAgent")
            context_input = {
                'query_intent': query_intent,
                'user_context': user_context or {}
            }
            context_response = await self.context_agent.process(context_input, {'conversation_id': conversation_id})
            context_data = context_response.content
            
            # Phase 3: Knowledge Retrieval (simulated)
            logger.info(f"Phase 3: Retrieving knowledge from sources")
            knowledge_items = await self._retrieve_knowledge(query_intent, context_data)
            
            # Phase 4: Knowledge Synthesis
            logger.info(f"Phase 4: Synthesizing response with SynthesisAgent")
            synthesis_input = {
                'query_intent': query_intent,
                'context_data': context_data,
                'knowledge_items': knowledge_items
            }
            synthesis_response = await self.synthesis_agent.process(synthesis_input, {'conversation_id': conversation_id})
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Compile final response
            final_response = {
                'response': synthesis_response.content.get('response', 'Unable to generate response'),
                'confidence': synthesis_response.confidence,
                'sources_used': [item.source for item in knowledge_items],
                'reasoning_chain': synthesis_response.content.get('reasoning_chain', []),
                'intent_detected': query_intent.intent_type,
                'complexity_level': query_intent.complexity_level,
                'execution_time': execution_time,
                'agent_metrics': {
                    'query_agent': {
                        'confidence': query_response.confidence,
                        'execution_time': query_response.execution_time
                    },
                    'context_agent': {
                        'confidence': context_response.confidence,
                        'execution_time': context_response.execution_time
                    },
                    'synthesis_agent': {
                        'confidence': synthesis_response.confidence,
                        'execution_time': synthesis_response.execution_time
                    }
                }
            }
            
            self._update_orchestration_metrics(execution_time, True)
            return final_response
            
        except Exception as e:
            logger.error(f"Error in multi-agent processing: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_orchestration_metrics(execution_time, False)
            
            return {
                'response': f"I apologize, but I encountered an error while processing your query: {str(e)}",
                'confidence': 0.0,
                'sources_used': [],
                'reasoning_chain': ['Error occurred during processing'],
                'intent_detected': 'error',
                'complexity_level': 'unknown',
                'execution_time': execution_time,
                'error': str(e)
            }
    
    async def _retrieve_knowledge(self, query_intent: QueryIntent, context_data: Dict) -> List[KnowledgeItem]:
        """Retrieve relevant knowledge items (simulated for now)"""
        # In production, this would query actual knowledge sources
        # For now, return simulated knowledge items
        
        simulated_items = []
        
        # Simulate different sources based on required sources
        for source in query_intent.required_sources[:3]:  # Limit to 3 sources
            item = KnowledgeItem(
                content=f"Simulated knowledge from {source} for query about {query_intent.intent_type}. This would contain actual relevant information from the {source} source.",
                source=source,
                source_type=source,
                timestamp=datetime.now(),
                confidence=0.8,
                credibility_score=self.synthesis_agent.credibility_weights.get(source, 0.7),
                tags=[query_intent.intent_type],
                context={'source_query': query_intent.original_query},
                version="1.0"
            )
            simulated_items.append(item)
        
        return simulated_items
    
    def _update_orchestration_metrics(self, execution_time: float, success: bool):
        """Update orchestration performance metrics"""
        self.orchestration_metrics['total_queries'] += 1
        
        # Update average response time
        current_avg = self.orchestration_metrics['average_response_time']
        total_queries = self.orchestration_metrics['total_queries']
        self.orchestration_metrics['average_response_time'] = (
            (current_avg * (total_queries - 1) + execution_time) / total_queries
        )
        
        # Update success rate
        current_success = self.orchestration_metrics['agent_collaboration_success']
        success_value = 1.0 if success else 0.0
        self.orchestration_metrics['agent_collaboration_success'] = (
            (current_success * (total_queries - 1) + success_value) / total_queries
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'orchestrator_metrics': self.orchestration_metrics,
            'agent_status': {
                'query_agent': {
                    'name': self.query_agent.name,
                    'capabilities': self.query_agent.capabilities,
                    'performance_metrics': self.query_agent.performance_metrics
                },
                'context_agent': {
                    'name': self.context_agent.name,
                    'capabilities': self.context_agent.capabilities,
                    'performance_metrics': self.context_agent.performance_metrics
                },
                'synthesis_agent': {
                    'name': self.synthesis_agent.name,
                    'capabilities': self.synthesis_agent.capabilities,
                    'performance_metrics': self.synthesis_agent.performance_metrics
                }
            },
            'system_health': 'healthy' if all([
                self.orchestration_metrics['agent_collaboration_success'] > 0.8,
                self.orchestration_metrics['average_response_time'] < 5.0
            ]) else 'degraded'
        }

# Example usage and testing
if __name__ == "__main__":
    async def test_multi_agent_system():
        """Test the multi-agent system"""
        orchestrator = MultiAgentOrchestrator()
        
        test_queries = [
            "How do I fix topology merge issues in our system?",
            "What are the best practices for code review in our GitHub repositories?",
            "Can you compare the performance of different API endpoints?",
            "Show me historical cases similar to the current network connectivity problem"
        ]
        
        for query in test_queries:
            print(f"\n{'='*50}")
            print(f"Query: {query}")
            print('='*50)
            
            result = await orchestrator.process_query(query)
            
            print(f"Intent: {result['intent_detected']}")
            print(f"Complexity: {result['complexity_level']}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Execution Time: {result['execution_time']:.2f}s")
            print(f"Sources Used: {', '.join(result['sources_used'])}")
            print(f"\nResponse: {result['response']}")
            
            if result.get('reasoning_chain'):
                print(f"\nReasoning:")
                for step in result['reasoning_chain']:
                    print(f"  - {step}")
        
        # System status
        status = orchestrator.get_system_status()
        print(f"\n{'='*50}")
        print("System Status")
        print('='*50)
        print(json.dumps(status, indent=2, default=str))
    
    # Run the test
    asyncio.run(test_multi_agent_system())