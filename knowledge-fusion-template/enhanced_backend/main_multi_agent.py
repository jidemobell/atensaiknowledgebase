"""
Enhanced IBM Knowledge Fusion Platform - Beyond RAG
Merges ideas from IBM Granite Retrieval Agent with novel multi-source synthesis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Callable, Awaitable
import uuid
import json
import asyncio
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IBM Knowledge Fusion Platform - Enhanced Multi-Agent", 
    version="4.0.0",
    description="Beyond RAG: Multi-agent conversational AI with dynamic knowledge fusion"
)

# Enable CORS for OpenWebUI and other frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:3001", "http://localhost:8082"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced data models inspired by Granite template
class KnowledgeAgent(BaseModel):
    """Represents a specialized knowledge agent"""
    name: str
    role: str
    capabilities: List[str]
    confidence_threshold: float = 0.7

class ExecutionStep(BaseModel):
    """Individual step in knowledge fusion plan"""
    step_id: str
    instruction: str
    agent_assigned: str
    tools_required: List[str]
    expected_output: str
    status: str = "pending"  # pending, executing, completed, failed
    result: Optional[Dict[str, Any]] = None
    confidence: float = 0.0

class KnowledgeFusionPlan(BaseModel):
    """Dynamic execution plan for knowledge synthesis"""
    plan_id: str
    original_query: str
    goal: str
    steps: List[ExecutionStep]
    current_step: int = 0
    context_accumulated: List[Dict[str, Any]] = []
    status: str = "active"  # active, completed, failed

class EnhancedQuery(BaseModel):
    """Enhanced query model supporting multi-modal input"""
    query: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}
    execution_mode: str = "adaptive"  # simple, planned, adaptive
    confidence_threshold: float = 0.8
    max_iterations: int = 6

class AgentResponse(BaseModel):
    """Response from individual knowledge agent"""
    agent_name: str
    response_content: str
    sources_used: List[str]
    confidence: float
    metadata: Dict[str, Any] = {}
    tool_calls: List[Dict[str, Any]] = []

class KnowledgeFusionResponse(BaseModel):
    """Enhanced response with execution details"""
    response: str
    execution_plan: Optional[KnowledgeFusionPlan] = None
    agents_used: List[str] = []
    sources_synthesized: List[str] = []
    confidence: float
    reasoning: str
    suggested_follow_ups: List[str] = []
    conversation_id: str
    knowledge_areas_detected: List[str] = []
    execution_metadata: Dict[str, Any] = {}

# Agent definitions inspired by Granite pattern
KNOWLEDGE_AGENTS = {
    "planner": KnowledgeAgent(
        name="Strategic Planner",
        role="Creates dynamic execution plans for complex knowledge queries",
        capabilities=["query_analysis", "step_planning", "resource_allocation"]
    ),
    "researcher": KnowledgeAgent(
        name="Knowledge Researcher", 
        role="Executes research steps across multiple knowledge sources",
        capabilities=["document_search", "code_analysis", "case_retrieval", "web_search"]
    ),
    "synthesizer": KnowledgeAgent(
        name="Knowledge Synthesizer",
        role="Combines insights from multiple sources into coherent responses", 
        capabilities=["multi_source_fusion", "confidence_scoring", "response_generation"]
    ),
    "critic": KnowledgeAgent(
        name="Quality Critic",
        role="Validates step completion and response quality",
        capabilities=["step_validation", "quality_assessment", "gap_identification"]
    ),
    "reflector": KnowledgeAgent(
        name="Adaptive Reflector",
        role="Adapts plans based on intermediate results and context",
        capabilities=["plan_adaptation", "context_analysis", "next_step_recommendation"]
    )
}

# Enhanced storage with execution tracking
enhanced_store = {
    'conversations': {},
    'execution_plans': {},
    'agent_interactions': [],
    'knowledge_cache': {},
    'performance_metrics': {}
}

class MultiAgentKnowledgeFusion:
    """
    Multi-agent system for dynamic knowledge fusion
    Goes beyond traditional RAG with adaptive planning and execution
    """
    
    def __init__(self):
        self.agents = KNOWLEDGE_AGENTS
        self.active_plans = {}
        
    async def process_query(self, query: EnhancedQuery) -> KnowledgeFusionResponse:
        """Main entry point for multi-agent knowledge fusion"""
        
        logger.info(f"Processing query with {query.execution_mode} mode: {query.query[:50]}...")
        
        if query.execution_mode == "simple":
            return await self._simple_fusion(query)
        elif query.execution_mode == "planned":
            return await self._planned_fusion(query)
        else:  # adaptive
            return await self._adaptive_fusion(query)
    
    async def _adaptive_fusion(self, query: EnhancedQuery) -> KnowledgeFusionResponse:
        """
        Adaptive multi-agent fusion inspired by Granite template
        Dynamically creates and executes plans based on query complexity
        """
        
        # Step 1: Strategic Planning
        plan = await self._create_execution_plan(query)
        
        # Step 2: Iterative Execution with Adaptation
        execution_result = await self._execute_adaptive_plan(plan, query)
        
        # Step 3: Final Synthesis
        response = await self._synthesize_final_response(execution_result, query)
        
        return response
    
    async def _create_execution_plan(self, query: EnhancedQuery) -> KnowledgeFusionPlan:
        """Create dynamic execution plan using planner agent"""
        
        plan_id = str(uuid.uuid4())
        
        # Analyze query complexity and determine required steps
        analysis = await self._analyze_query_complexity(query.query)
        
        steps = []
        
        # Dynamic step generation based on query analysis
        if analysis['requires_historical_data']:
            steps.append(ExecutionStep(
                step_id=f"step_{len(steps)+1}",
                instruction=f"Search historical cases related to: {query.query}",
                agent_assigned="researcher",
                tools_required=["case_search"],
                expected_output="Relevant historical cases with solutions"
            ))
        
        if analysis['requires_code_analysis']:
            steps.append(ExecutionStep(
                step_id=f"step_{len(steps)+1}",
                instruction=f"Analyze code repositories for: {query.query}",
                agent_assigned="researcher", 
                tools_required=["code_search"],
                expected_output="Code patterns and implementation details"
            ))
        
        if analysis['requires_documentation']:
            steps.append(ExecutionStep(
                step_id=f"step_{len(steps)+1}",
                instruction=f"Search documentation for: {query.query}",
                agent_assigned="researcher",
                tools_required=["doc_search"],
                expected_output="Documentation guidelines and procedures"
            ))
        
        if analysis['requires_external_knowledge']:
            steps.append(ExecutionStep(
                step_id=f"step_{len(steps)+1}",
                instruction=f"Search external sources for: {query.query}",
                agent_assigned="researcher",
                tools_required=["web_search"],
                expected_output="External knowledge and best practices"
            ))
        
        # Always add synthesis step
        steps.append(ExecutionStep(
            step_id=f"step_{len(steps)+1}",
            instruction="Synthesize findings from all sources into coherent response",
            agent_assigned="synthesizer",
            tools_required=["fusion_engine"],
            expected_output="Comprehensive synthesized response"
        ))
        
        plan = KnowledgeFusionPlan(
            plan_id=plan_id,
            original_query=query.query,
            goal=f"Provide comprehensive answer to: {query.query}",
            steps=steps
        )
        
        # Store plan
        enhanced_store['execution_plans'][plan_id] = plan
        self.active_plans[plan_id] = plan
        
        return plan
    
    async def _execute_adaptive_plan(self, plan: KnowledgeFusionPlan, query: EnhancedQuery) -> Dict[str, Any]:
        """Execute plan with adaptive refinement"""
        
        execution_result = {
            'plan_id': plan.plan_id,
            'steps_completed': [],
            'accumulated_knowledge': [],
            'adaptations_made': [],
            'final_status': 'in_progress'
        }
        
        for i, step in enumerate(plan.steps):
            logger.info(f"Executing step {i+1}/{len(plan.steps)}: {step.instruction[:50]}...")
            
            # Execute individual step
            step_result = await self._execute_step(step, plan.context_accumulated)
            
            # Validate step completion
            is_step_valid = await self._validate_step(step, step_result)
            
            if is_step_valid:
                # Step successful - accumulate knowledge
                step.status = "completed"
                step.result = step_result
                plan.context_accumulated.append(step_result)
                execution_result['steps_completed'].append(step)
                execution_result['accumulated_knowledge'].extend(step_result.get('knowledge_items', []))
            else:
                # Step failed - adapt plan
                logger.warning(f"Step failed validation: {step.step_id}")
                adaptation = await self._adapt_plan(plan, step, step_result)
                execution_result['adaptations_made'].append(adaptation)
                
                if adaptation['action'] == 'retry_modified':
                    # Retry with modified instruction
                    step.instruction = adaptation['modified_instruction']
                    step_result = await self._execute_step(step, plan.context_accumulated)
                    step.result = step_result
                    plan.context_accumulated.append(step_result)
                elif adaptation['action'] == 'skip':
                    # Skip this step and continue
                    step.status = "skipped"
                    continue
                elif adaptation['action'] == 'abort':
                    # Critical failure - abort execution
                    execution_result['final_status'] = 'failed'
                    break
            
            # Check if goal is achieved early
            goal_achieved = await self._check_goal_achievement(plan, execution_result)
            if goal_achieved:
                logger.info("Goal achieved early - ending execution")
                break
        
        execution_result['final_status'] = 'completed'
        return execution_result
    
    async def _execute_step(self, step: ExecutionStep, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute individual step using appropriate agent and tools"""
        
        step.status = "executing"
        
        # Select appropriate execution method based on tools required
        if "case_search" in step.tools_required:
            return await self._execute_case_search(step.instruction, context)
        elif "code_search" in step.tools_required:
            return await self._execute_code_search(step.instruction, context)
        elif "doc_search" in step.tools_required:
            return await self._execute_doc_search(step.instruction, context)
        elif "web_search" in step.tools_required:
            return await self._execute_web_search(step.instruction, context)
        elif "fusion_engine" in step.tools_required:
            return await self._execute_knowledge_fusion(step.instruction, context)
        else:
            return await self._execute_generic_step(step.instruction, context)
    
    async def _execute_case_search(self, instruction: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute case search with context awareness"""
        
        # Enhanced case search incorporating context
        knowledge_items = []
        
        # Mock implementation - replace with real case search
        relevant_cases = [
            {
                "case_id": "CASE-2024-001",
                "title": "Topology merge optimization",
                "description": "Improved merge performance by 40% through algorithm optimization",
                "resolution": "Implemented parallel processing and caching strategies",
                "confidence": 0.9,
                "context_relevance": self._calculate_context_relevance(instruction, context)
            }
        ]
        
        knowledge_items.extend(relevant_cases)
        
        return {
            "step_type": "case_search",
            "instruction": instruction,
            "knowledge_items": knowledge_items,
            "sources": ["historical_cases"],
            "confidence": 0.85,
            "context_used": len(context) > 0
        }
    
    async def _execute_code_search(self, instruction: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute code repository search"""
        
        knowledge_items = [
            {
                "repository": "topology-service",
                "file_path": "src/core/merge_engine.py", 
                "code_snippet": "def optimized_merge(nodes, edges, timeout=60):\n    # Parallel processing implementation\n    return merged_topology",
                "confidence": 0.8,
                "context_relevance": self._calculate_context_relevance(instruction, context)
            }
        ]
        
        return {
            "step_type": "code_search",
            "instruction": instruction,
            "knowledge_items": knowledge_items,
            "sources": ["code_repositories"],
            "confidence": 0.8,
            "context_used": len(context) > 0
        }
    
    async def _execute_doc_search(self, instruction: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute documentation search"""
        
        knowledge_items = [
            {
                "document_type": "API_GUIDE",
                "title": "Topology Service Configuration",
                "content": "Configure merge timeout and optimization parameters in config.yaml",
                "confidence": 0.85,
                "context_relevance": self._calculate_context_relevance(instruction, context)
            }
        ]
        
        return {
            "step_type": "doc_search", 
            "instruction": instruction,
            "knowledge_items": knowledge_items,
            "sources": ["documentation"],
            "confidence": 0.85,
            "context_used": len(context) > 0
        }
    
    async def _execute_web_search(self, instruction: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute web search for external knowledge"""
        
        # Mock web search results
        knowledge_items = [
            {
                "source": "Stack Overflow",
                "title": "Graph merge optimization techniques",
                "content": "Best practices for large-scale graph merging and performance optimization",
                "url": "https://stackoverflow.com/questions/example",
                "confidence": 0.7,
                "context_relevance": self._calculate_context_relevance(instruction, context)
            }
        ]
        
        return {
            "step_type": "web_search",
            "instruction": instruction, 
            "knowledge_items": knowledge_items,
            "sources": ["web_search"],
            "confidence": 0.7,
            "context_used": len(context) > 0
        }
    
    async def _execute_knowledge_fusion(self, instruction: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute final knowledge fusion and synthesis"""
        
        # Collect all knowledge from context
        all_knowledge = []
        sources_used = set()
        
        for ctx_item in context:
            all_knowledge.extend(ctx_item.get('knowledge_items', []))
            sources_used.update(ctx_item.get('sources', []))
        
        # Synthesize response (this is where real AI model would be used)
        synthesized_response = await self._synthesize_knowledge(all_knowledge, instruction)
        
        return {
            "step_type": "knowledge_fusion",
            "instruction": instruction,
            "synthesized_response": synthesized_response,
            "sources_synthesized": list(sources_used),
            "knowledge_count": len(all_knowledge),
            "confidence": self._calculate_fusion_confidence(all_knowledge)
        }
    
    async def _synthesize_knowledge(self, knowledge_items: List[Dict[str, Any]], original_query: str) -> str:
        """
        Advanced knowledge synthesis - this is where AI models would be integrated
        For now, using rule-based synthesis
        """
        
        # Group knowledge by type
        cases = [k for k in knowledge_items if k.get('case_id')]
        code = [k for k in knowledge_items if k.get('repository')]
        docs = [k for k in knowledge_items if k.get('document_type')]
        web = [k for k in knowledge_items if k.get('url')]
        
        response_parts = []
        
        if cases:
            case_insights = []
            for case in cases:
                case_insights.append(f"Case {case['case_id']}: {case['resolution']}")
            response_parts.append(f"Historical cases show: {'; '.join(case_insights)}")
        
        if code:
            code_insights = []
            for c in code:
                code_insights.append(f"{c['file_path']}: {c['code_snippet'][:100]}...")
            response_parts.append(f"Code analysis reveals: {'; '.join(code_insights)}")
        
        if docs:
            doc_insights = []
            for doc in docs:
                doc_insights.append(f"{doc['title']}: {doc['content']}")
            response_parts.append(f"Documentation suggests: {'; '.join(doc_insights)}")
        
        if web:
            web_insights = []
            for w in web:
                web_insights.append(f"{w['title']}: {w['content']}")
            response_parts.append(f"External knowledge indicates: {'; '.join(web_insights)}")
        
        return " | ".join(response_parts)
    
    def _calculate_context_relevance(self, instruction: str, context: List[Dict[str, Any]]) -> float:
        """Calculate how relevant current context is to instruction"""
        if not context:
            return 0.5
        
        # Simple keyword overlap calculation
        instruction_words = set(instruction.lower().split())
        context_words = set()
        
        for ctx in context:
            if 'instruction' in ctx:
                context_words.update(ctx['instruction'].lower().split())
        
        if not context_words:
            return 0.5
        
        overlap = len(instruction_words.intersection(context_words))
        return min(0.9, 0.3 + (overlap / max(len(instruction_words), len(context_words))))
    
    def _calculate_fusion_confidence(self, knowledge_items: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence of fused knowledge"""
        if not knowledge_items:
            return 0.0
        
        confidences = [item.get('confidence', 0.5) for item in knowledge_items]
        source_diversity = len(set(item.get('source', 'unknown') for item in knowledge_items))
        
        avg_confidence = sum(confidences) / len(confidences)
        diversity_bonus = min(0.2, source_diversity * 0.05)
        
        return min(0.95, avg_confidence + diversity_bonus)
    
    async def _validate_step(self, step: ExecutionStep, result: Dict[str, Any]) -> bool:
        """Validate if step was completed successfully"""
        
        # Basic validation criteria
        if not result:
            return False
        
        if result.get('confidence', 0) < 0.3:
            return False
        
        if 'knowledge_items' in result and len(result['knowledge_items']) == 0:
            return False
        
        # Step-specific validation
        if step.agent_assigned == "researcher":
            return len(result.get('knowledge_items', [])) > 0
        elif step.agent_assigned == "synthesizer":
            return 'synthesized_response' in result and len(result['synthesized_response']) > 10
        
        return True
    
    async def _adapt_plan(self, plan: KnowledgeFusionPlan, failed_step: ExecutionStep, result: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt plan when step fails"""
        
        # Analyze failure reason
        failure_reason = self._analyze_failure(failed_step, result)
        
        if failure_reason == "low_confidence":
            return {
                "action": "retry_modified",
                "modified_instruction": f"{failed_step.instruction} (focus on high-confidence results)",
                "reason": "Low confidence results - refining search criteria"
            }
        elif failure_reason == "no_results":
            return {
                "action": "skip",
                "reason": "No relevant results found - continuing with available information"
            }
        elif failure_reason == "critical_error":
            return {
                "action": "abort",
                "reason": "Critical error - cannot continue execution"
            }
        else:
            return {
                "action": "retry_modified",
                "modified_instruction": f"Alternative approach: {failed_step.instruction}",
                "reason": "Generic failure - trying alternative approach"
            }
    
    def _analyze_failure(self, step: ExecutionStep, result: Dict[str, Any]) -> str:
        """Analyze why a step failed"""
        
        if not result:
            return "critical_error"
        
        if result.get('confidence', 0) < 0.3:
            return "low_confidence"
        
        if 'knowledge_items' in result and len(result['knowledge_items']) == 0:
            return "no_results"
        
        return "unknown"
    
    async def _check_goal_achievement(self, plan: KnowledgeFusionPlan, execution_result: Dict[str, Any]) -> bool:
        """Check if the overall goal has been achieved"""
        
        # Simple heuristic - if we have knowledge from multiple sources, goal likely achieved
        accumulated_knowledge = execution_result.get('accumulated_knowledge', [])
        sources_used = set()
        
        for knowledge in accumulated_knowledge:
            if hasattr(knowledge, 'get'):
                sources_used.update(knowledge.get('sources', []))
        
        # Goal achieved if we have knowledge from at least 2 different sources
        return len(sources_used) >= 2 and len(accumulated_knowledge) >= 3
    
    async def _synthesize_final_response(self, execution_result: Dict[str, Any], query: EnhancedQuery) -> KnowledgeFusionResponse:
        """Synthesize final response from execution results"""
        
        # Find synthesis step result
        synthesis_result = None
        for step in execution_result.get('steps_completed', []):
            if step.agent_assigned == "synthesizer":
                synthesis_result = step.result
                break
        
        if synthesis_result:
            response_text = synthesis_result.get('synthesized_response', 'Unable to synthesize response')
            sources = synthesis_result.get('sources_synthesized', [])
            confidence = synthesis_result.get('confidence', 0.5)
        else:
            # Fallback synthesis
            accumulated = execution_result.get('accumulated_knowledge', [])
            response_text = f"Based on analysis of {len(accumulated)} knowledge sources: Information available but synthesis incomplete"
            sources = ["fallback_synthesis"]
            confidence = 0.6
        
        return KnowledgeFusionResponse(
            response=response_text,
            execution_plan=self.active_plans.get(execution_result['plan_id']),
            agents_used=[step.agent_assigned for step in execution_result.get('steps_completed', [])],
            sources_synthesized=sources,
            confidence=confidence,
            reasoning=f"Multi-agent execution with {len(execution_result.get('steps_completed', []))} completed steps",
            suggested_follow_ups=[
                "Would you like me to explore any specific aspect in more detail?",
                "Are there related areas you'd like me to investigate?"
            ],
            conversation_id=query.conversation_id or str(uuid.uuid4()),
            knowledge_areas_detected=self._detect_knowledge_areas(query.query),
            execution_metadata={
                "execution_time": "simulated",
                "steps_completed": len(execution_result.get('steps_completed', [])),
                "adaptations_made": len(execution_result.get('adaptations_made', [])),
                "final_status": execution_result.get('final_status', 'unknown')
            }
        )
    
    async def _simple_fusion(self, query: EnhancedQuery) -> KnowledgeFusionResponse:
        """Simple fusion mode for basic queries"""
        
        # Quick single-step response
        response_text = f"Simple response to: {query.query} (using basic knowledge lookup)"
        
        return KnowledgeFusionResponse(
            response=response_text,
            agents_used=["simple_responder"],
            sources_synthesized=["basic_knowledge"],
            confidence=0.7,
            reasoning="Simple mode - direct knowledge lookup",
            conversation_id=query.conversation_id or str(uuid.uuid4()),
            knowledge_areas_detected=self._detect_knowledge_areas(query.query)
        )
    
    async def _planned_fusion(self, query: EnhancedQuery) -> KnowledgeFusionResponse:
        """Planned fusion mode with predefined execution strategy"""
        
        # Create and execute predefined plan
        plan = await self._create_execution_plan(query)
        execution_result = await self._execute_planned_steps(plan)
        response = await self._synthesize_final_response(execution_result, query)
        
        return response
    
    async def _execute_planned_steps(self, plan: KnowledgeFusionPlan) -> Dict[str, Any]:
        """Execute predefined plan without adaptation"""
        
        execution_result = {
            'plan_id': plan.plan_id,
            'steps_completed': [],
            'accumulated_knowledge': [],
            'final_status': 'completed'
        }
        
        for step in plan.steps:
            step_result = await self._execute_step(step, plan.context_accumulated)
            step.result = step_result
            step.status = "completed"
            plan.context_accumulated.append(step_result)
            execution_result['steps_completed'].append(step)
            execution_result['accumulated_knowledge'].extend(step_result.get('knowledge_items', []))
        
        return execution_result
    
    async def _analyze_query_complexity(self, query: str) -> Dict[str, bool]:
        """Analyze query to determine required knowledge sources"""
        
        query_lower = query.lower()
        
        return {
            'requires_historical_data': any(word in query_lower for word in ['case', 'history', 'previous', 'past', 'before']),
            'requires_code_analysis': any(word in query_lower for word in ['code', 'implementation', 'function', 'method', 'api']),
            'requires_documentation': any(word in query_lower for word in ['how', 'configure', 'setup', 'install', 'guide']),
            'requires_external_knowledge': any(word in query_lower for word in ['best practices', 'industry', 'compare', 'alternatives'])
        }
    
    def _detect_knowledge_areas(self, query: str) -> List[str]:
        """Detect knowledge areas from query"""
        
        query_lower = query.lower()
        areas = []
        
        if any(word in query_lower for word in ['topology', 'merge', 'graph']):
            areas.append('topology_management')
        if any(word in query_lower for word in ['timeout', 'performance', 'slow']):
            areas.append('performance_optimization') 
        if any(word in query_lower for word in ['config', 'setting', 'parameter']):
            areas.append('configuration')
        if any(word in query_lower for word in ['error', 'fail', 'issue']):
            areas.append('troubleshooting')
        
        return areas or ['general']

# Initialize multi-agent system
multi_agent_fusion = MultiAgentKnowledgeFusion()

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "4.0.0",
        "service": "IBM Knowledge Fusion Platform - Multi-Agent"
    }

@app.post("/knowledge-fusion/query")
async def knowledge_fusion_query(query: EnhancedQuery):
    """
    Enhanced knowledge fusion with multi-agent execution
    Goes beyond traditional RAG with adaptive planning
    """
    try:
        logger.info(f"Received query: {query.query[:100]}...")
        
        # Process query through multi-agent system
        response = await multi_agent_fusion.process_query(query)
        
        logger.info(f"Response generated with confidence: {response.confidence}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/agents")
async def list_agents():
    """List available knowledge agents"""
    return {
        "agents": KNOWLEDGE_AGENTS,
        "total_count": len(KNOWLEDGE_AGENTS)
    }

@app.get("/execution-plans")
async def list_execution_plans():
    """List active execution plans"""
    return {
        "active_plans": len(multi_agent_fusion.active_plans),
        "total_plans": len(enhanced_store['execution_plans'])
    }

@app.get("/execution-plans/{plan_id}")
async def get_execution_plan(plan_id: str):
    """Get details of specific execution plan"""
    if plan_id not in enhanced_store['execution_plans']:
        raise HTTPException(status_code=404, detail="Execution plan not found")
    
    return enhanced_store['execution_plans'][plan_id]

# Legacy compatibility endpoint
@app.post("/query")
async def legacy_query(request: dict):
    """Legacy endpoint for backward compatibility"""
    
    enhanced_query = EnhancedQuery(
        query=request.get('query', ''),
        execution_mode="simple"
    )
    
    response = await multi_agent_fusion.process_query(enhanced_query)
    
    # Return in legacy format
    return {
        "response": response.response,
        "sources_used": response.sources_synthesized,
        "confidence": response.confidence,
        "reasoning": response.reasoning,
        "suggested_follow_ups": response.suggested_follow_ups,
        "conversation_id": response.conversation_id,
        "knowledge_areas_detected": response.knowledge_areas_detected
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
