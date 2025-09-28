#!/usr/bin/env python3
"""
Knowledge Fusion API Gateway - Phase 2 Enhanced
Multi-Agent System Integration with intelligent routing and cross-source validation
Enhanced with intelligent case clustering and specialized knowledge agents
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from typing import Dict, Any, Optional
import uvicorn
import json
import os
from simple_case_clustering import SimpleCaseClusteringSystem

# Phase 2: Multi-Agent System Integration  
try:
    from multi_agent_orchestrator import create_multi_agent_system
    MULTI_AGENT_ENABLED = True
    print("🤖 Multi-Agent System: ENABLED")
except ImportError as e:
    MULTI_AGENT_ENABLED = False
    print(f"⚠️ Multi-Agent System: DISABLED ({e})")

app = FastAPI(
    title="Knowledge Fusion API Gateway",
    description="Gateway for integrating Knowledge Fusion with OpenWebUI",
    version="1.0.0"
)

# CORS middleware for OpenWebUI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
KNOWLEDGE_FUSION_URL = "http://localhost:8002"
COREBACKEND_URL = "http://localhost:8001"

# Initialize intelligent case clustering for enhanced matching
clustering_system = SimpleCaseClusteringSystem()
cluster_cache = {}
knowledge_base_cache = None

# Phase 2: Initialize Multi-Agent System
multi_agent_orchestrator = None
if MULTI_AGENT_ENABLED:
    try:
        multi_agent_orchestrator = create_multi_agent_system()
        print("🎯 Multi-Agent Orchestrator initialized successfully")
    except Exception as e:
        print(f"⚠️ Failed to initialize Multi-Agent System: {e}")
        multi_agent_orchestrator = None

async def load_knowledge_base():
    """Load processed cases for similarity matching"""
    global knowledge_base_cache
    
    if knowledge_base_cache is not None:
        return knowledge_base_cache
    
    try:
        knowledge_base_file = "enterprise_knowledge_base.json"
        if os.path.exists(knowledge_base_file):
            with open(knowledge_base_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                knowledge_base_cache = data.get('cases', [])
                print(f"📚 Loaded {len(knowledge_base_cache)} cases for similarity matching")
                return knowledge_base_cache
    except Exception as e:
        print(f"⚠️ Could not load knowledge base: {e}")
    
    return []

async def enhance_query_with_clustering(request: Dict[str, Any], query: str) -> Dict[str, Any]:
    """Enhance query with intelligent case matching"""
    
    enhanced_request = request.copy()
    
    try:
        # Load knowledge base
        cases = await load_knowledge_base()
        
        if not cases:
            print("📝 No cases available for similarity matching")
            return enhanced_request
        
        # Create a pseudo-case from the query
        query_case = {
            'title': query,
            'description': query,
            'full_text_for_rag': query,
            'services': [],
            'symptoms': [],
            'confidence': 1.0
        }
        
        # Find similar cases
        similar_cases = clustering_system.find_similar_cases(
            query_case, cases, top_k=5
        )
        
        if similar_cases:
            print(f"🎯 Found {len(similar_cases)} similar cases")
            
            # Add similar cases to request
            enhanced_request['similar_cases'] = [
                {
                    'case_number': case.get('case_number', 'Unknown'),
                    'title': case.get('title', '')[:100],
                    'services': case.get('services', [])[:3],
                    'resolution_patterns': case.get('resolution_patterns', [])[:2],
                    'similarity_score': case.get('similarity_score', 0)
                }
                for case in similar_cases[:3]  # Top 3 most similar
            ]
            
            # Extract insights
            all_services = []
            all_resolutions = []
            for case in similar_cases:
                all_services.extend(case.get('services', []))
                all_resolutions.extend(case.get('resolution_patterns', []))
            
            # Add cluster insights
            enhanced_request['cluster_insights'] = {
                'common_services': list(set(all_services))[:5],
                'suggested_resolutions': list(set(all_resolutions))[:3],
                'confidence_score': sum(case.get('similarity_score', 0) for case in similar_cases) / len(similar_cases)
            }
            
            print(f"💡 Enhanced query with insights from similar cases")
        
    except Exception as e:
        print(f"⚠️ Error enhancing query: {e}")
    
    return enhanced_request

def enhance_response_with_insights(core_result: Dict[str, Any], enhanced_request: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance response with clustering insights"""
    
    enhanced_response = core_result.copy()
    
    try:
        similar_cases = enhanced_request.get('similar_cases', [])
        cluster_insights = enhanced_request.get('cluster_insights', {})
        
        if similar_cases or cluster_insights:
            # Add similarity context to response
            context_addition = "\n\n📊 **Context from Similar Cases:**\n"
            
            if similar_cases:
                context_addition += f"Found {len(similar_cases)} similar historical cases:\n"
                for case in similar_cases[:2]:  # Top 2
                    context_addition += f"• Case {case['case_number']}: {case['title'][:80]}...\n"
            
            if cluster_insights.get('suggested_resolutions'):
                context_addition += f"\n🎯 **Common Resolution Patterns:**\n"
                for resolution in cluster_insights['suggested_resolutions']:
                    context_addition += f"• {resolution}\n"
            
            if cluster_insights.get('common_services'):
                context_addition += f"\n🔧 **Related Services:** {', '.join(cluster_insights['common_services'])}\n"
            
            # Enhance the response
            original_response = enhanced_response.get('response', '')
            enhanced_response['response'] = original_response + context_addition
            
            print("✅ Enhanced response with clustering insights")
        
    except Exception as e:
        print(f"⚠️ Error enhancing response: {e}")
    
    return enhanced_response

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Knowledge Fusion API Gateway",
        "version": "2.0.0 (Multi-Agent Enhanced)",
        "backends": {
            "knowledge_fusion": KNOWLEDGE_FUSION_URL,
            "corebackend": COREBACKEND_URL
        },
        "capabilities": {
            "multi_agent_system": MULTI_AGENT_ENABLED,
            "case_clustering": True,
            "cross_validation": MULTI_AGENT_ENABLED,
            "dynamic_source_selection": MULTI_AGENT_ENABLED
        }
    }

@app.post("/knowledge-fusion/intelligent")
async def intelligent_knowledge_query(request: Dict[str, Any]):
    """
    Phase 2: Intelligent routing endpoint
    Automatically selects multi-agent or standard processing based on query complexity
    """
    query = request.get("query", "")
    
    # Analyze query complexity and requirements
    should_use_multi_agent = await _should_use_multi_agent_processing(query, request)
    
    if should_use_multi_agent and multi_agent_orchestrator:
        print(f"🧠 Routing to Multi-Agent System (complexity: high)")
        return await multi_agent_knowledge_query(request)
    else:
        print(f"🔄 Routing to Standard Processing (complexity: standard)")
        return await knowledge_fusion_query(request)

async def _should_use_multi_agent_processing(query: str, request: Dict[str, Any]) -> bool:
    """Determine if query requires multi-agent processing"""
    
    if not MULTI_AGENT_ENABLED:
        return False
    
    # Simple queries should always go to Core Backend
    simple_queries = ['hello', 'hi', 'test', 'ping', 'status', 'help']
    if query.lower().strip() in simple_queries:
        print(f"🔄 Simple query detected: '{query}' -> routing to Core Backend")
        return False
    
    # Very short queries (< 3 words) should use Core Backend
    if len(query.split()) < 3:
        print(f"🔄 Short query detected: '{query}' -> routing to Core Backend")  
        return False
    
    # Complexity indicators that benefit from multi-agent processing
    complexity_indicators = [
        # Multiple domain query
        len([domain for domain in ['topology', 'case', 'github', 'service', 'config'] 
             if domain in query.lower()]) > 1,
        
        # Comparative questions
        any(word in query.lower() for word in ['compare', 'versus', 'vs', 'difference', 'better']),
        
        # Complex troubleshooting
        any(word in query.lower() for word in ['troubleshoot', 'diagnose', 'root cause', 'analyze']),
        
        # Multi-step requests
        any(word in query.lower() for word in ['step by step', 'how to setup', 'configure and']),
        
        # Cross-validation needs
        any(word in query.lower() for word in ['validate', 'verify', 'confirm', 'check multiple']),
        
        # Query length (longer queries often need multiple perspectives)
        len(query.split()) > 15,
        
        # Historical context requested
        'similar_cases' in request or 'historical' in query.lower()
    ]
    
    # Use multi-agent if 2 or more complexity indicators are present
    complexity_score = sum(complexity_indicators)
    print(f"🤖 Query complexity analysis: '{query}' -> score: {complexity_score}")
    return complexity_score >= 2

@app.post("/knowledge-fusion/multi-agent")
async def multi_agent_knowledge_query(request: Dict[str, Any]):
    """
    Phase 2: Multi-Agent Knowledge Fusion endpoint
    Routes: OpenWebUI → Gateway → Multi-Agent Orchestrator → Specialized Agents → Cross-Validation
    """
    if not multi_agent_orchestrator:
        # Fallback to standard processing
        return await knowledge_fusion_query(request)
    
    try:
        query = request.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        print(f"🤖 Multi-Agent Processing: {query}")
        
        # Build enhanced context from existing clustering
        enhanced_request = await enhance_query_with_clustering(request, query)
        context = {
            **enhanced_request,
            "conversation_id": request.get("conversation_id", "default"),
            "user_preferences": request.get("preferences", {}),
            "priority": request.get("priority", "normal")
        }
        
        # Process query through multi-agent system
        session_id = request.get("conversation_id", "default")
        result = await multi_agent_orchestrator.process_query(query, context, session_id)
        
        # Format response for OpenWebUI
        multi_agent_response = {
            "response": f"""🧠 **Multi-Agent Knowledge Analysis**

{result['response']}

---
**Intelligence Summary:**
• **Confidence**: {result['confidence']:.1%}
• **Agents Consulted**: {result['agents_consulted']} specialized knowledge agents
• **Processing Time**: {result['processing_time']:.2f}s
• **Sources Cross-Validated**: {len(result['sources'])}

**Agent Breakdown:**""",
            
            "sources_used": [source["agent_id"] for source in result["sources"]],
            "confidence": result["confidence"],
            "reasoning": f"Multi-agent analysis with {result['agents_consulted']} specialized agents",
            "knowledge_areas_detected": list(set([
                tag for source in result["sources"] 
                for tag in source.get("metadata", {}).get("tags", [])
            ])),
            "processing_details": {
                "multi_agent_enabled": True,
                "agents_consulted": result["agents_consulted"],
                "cross_validation": result.get("validation_results", {}),
                "recommendations": result.get("recommendations", [])
            },
            "suggested_follow_ups": [
                "Would you like more details from specific knowledge agents?",
                "Do you need analysis from additional knowledge sources?",
                "Should I cross-validate this information with other agents?"
            ]
        }
        
        # Add agent details
        for i, source in enumerate(result["sources"], 1):
            agent_name = source["agent_id"].replace("_", " ").title()
            confidence = source["confidence"]
            multi_agent_response["response"] += f"\n{i}. **{agent_name}**: {confidence:.1%} confidence"
        
        if result.get("recommendations"):
            multi_agent_response["response"] += "\n\n**Recommendations:**"
            for rec in result["recommendations"][:3]:
                multi_agent_response["response"] += f"\n• {rec}"
        
        print(f"✅ Multi-Agent response generated with {result['confidence']:.1%} confidence")
        return multi_agent_response
        
    except Exception as e:
        print(f"❌ Multi-Agent processing error: {e}")
        # Fallback to standard processing
        return await knowledge_fusion_query(request)

@app.post("/knowledge-fusion/query")
async def knowledge_fusion_query(request: Dict[str, Any]):
    """
    Standard Knowledge Fusion query endpoint (Phase 1)
    Routes: OpenWebUI → Gateway → Enhanced Matching → Knowledge Fusion Backend → CoreBackend
    """
    try:
        query = request.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        print(f"🔍 Processing query: {query}")
        
        # ENHANCEMENT: Add intelligent case matching
        enhanced_request = await enhance_query_with_clustering(request, query)
        
        # For simple queries, prioritize Core Backend (AI-enabled)
        simple_queries = ['hello', 'hi', 'test', 'ping', 'status', 'help']
        is_simple_query = query.lower().strip() in simple_queries or len(query.split()) < 3
        
        if is_simple_query:
            print(f"🎯 Simple query detected: '{query}' -> routing directly to AI-enabled Core Backend")
            # Route to Unified Knowledge Fusion for simple queries (it will handle Core Backend integration)
            try:
                async with httpx.AsyncClient() as client:
                    print(f"📡 Routing simple query to Unified Knowledge Fusion: {KNOWLEDGE_FUSION_URL}")
                    
                    response = await client.post(
                        f"{KNOWLEDGE_FUSION_URL}/unified-fusion",
                        json=enhanced_request,
                        timeout=15.0
                    )
                    
                    if response.status_code == 200:
                        unified_result = response.json()
                        print("✅ Unified Knowledge Fusion (simple query) responded successfully")
                        return unified_result
                    else:
                        print(f"⚠️ Unified Knowledge Fusion returned {response.status_code}")
                        
            except Exception as unified_error:
                print(f"⚠️ Unified Knowledge Fusion error: {unified_error}")
        
        # For complex queries, try Unified Knowledge Fusion first
        try:
            async with httpx.AsyncClient() as client:
                print(f"📡 Routing to Unified Knowledge Fusion: {KNOWLEDGE_FUSION_URL}")
                response = await client.post(
                    f"{KNOWLEDGE_FUSION_URL}/unified-fusion",
                    json=enhanced_request,  # Send enhanced request
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Unified Knowledge Fusion responded successfully")
                    return result
                else:
                    print(f"⚠️ Unified Knowledge Fusion returned {response.status_code}")
                    
        except Exception as kf_error:
            print(f"⚠️ Unified Knowledge Fusion error: {kf_error}")
        
        # Try CoreBackend as final fallback
        try:
            async with httpx.AsyncClient() as client:
                print(f"📡 Routing to CoreBackend: {COREBACKEND_URL}")
                
                # Format request for CoreBackend (matches QueryRequest model)
                corebackend_request = {
                    "query": query,
                    "session_id": request.get("conversation_id", "default")
                }
                
                response = await client.post(
                    f"{COREBACKEND_URL}/query",
                    json=corebackend_request,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    core_result = response.json()
                    print("✅ CoreBackend responded successfully")
                    
                    # Enhance response with clustering insights
                    enhanced_response = enhance_response_with_insights(core_result, enhanced_request)
                    return enhanced_response
                    
                    # Format CoreBackend response for OpenWebUI
                    return {
                        "response": f"""🔵 **IBM Knowledge Fusion Analysis** (via CoreBackend)

**Query:** {query}

**Analysis Result:**
{core_result.get('analysis', 'Analysis completed')}

**Recommendations:**
{core_result.get('recommendations', 'See detailed analysis above')}

**Confidence:** {core_result.get('confidence', 0.8):.1%}

*Powered by IBM CoreBackend Knowledge System*""",
                        
                        "sources_used": core_result.get("sources", ["corebackend"]),
                        "confidence": core_result.get("confidence", 0.8),
                        "reasoning": f"Processed via CoreBackend: {core_result.get('reasoning', 'Advanced diagnostic analysis')}",
                        "knowledge_areas_detected": core_result.get("knowledge_areas", ["system_analysis"]),
                        "suggested_follow_ups": core_result.get("follow_ups", [
                            "Would you like more detailed analysis?",
                            "Do you need specific troubleshooting steps?"
                        ]),
                        "backend_status": {
                            "knowledge_fusion": "fallback",
                            "corebackend": "active",
                            "mode": "corebackend_integration"
                        }
                    }
                else:
                    print(f"⚠️ CoreBackend returned {response.status_code}")
                    
        except Exception as core_error:
            print(f"⚠️ CoreBackend error: {core_error}")
        
        # Final fallback to simulated response
        print("🔄 Using simulated response")
        return await simulate_knowledge_fusion_response(request)
                
    except Exception as e:
        print(f"❌ Knowledge Fusion gateway error: {e}")
        return await simulate_knowledge_fusion_response(request)

async def simulate_knowledge_fusion_response(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced ASM-specific response when backend endpoints are not available
    Uses intelligent routing and case clustering insights
    """
    query = request.get("query", "")
    similar_cases = request.get("similar_cases", [])
    cluster_insights = request.get("cluster_insights", {})
    
    # ASM-specific keyword detection
    asm_services = {
        'topology': ['topology', 'merge', 'composite', 'nasm-topology'],
        'observer': ['observer', 'file-observer', 'rest-observer', 'data-ingestion'],
        'ui': ['ui', 'dashboard', 'hdm-common-ui', 'interface'],
        'analytics': ['analytics', 'aggregation', 'dedup', 'spark'],
        'kafka': ['kafka', 'message', 'topic', 'queue'],
        'performance': ['slow', 'timeout', 'memory', 'cpu', 'performance']
    }
    
    detected_services = []
    for service, keywords in asm_services.items():
        if any(keyword in query.lower() for keyword in keywords):
            detected_services.append(service)
    
    # Determine response type based on query content
    if 'topology' in query.lower():
        response_type = "ASM Topology Analysis"
        primary_service = "nasm-topology"
        related_services = ["hdm-analytics", "ui-content", "merge-service"]
        
        specific_response = f"""
� **ASM Topology Services Analysis**

**Primary Service:** `{primary_service}`
- Handles topology data ingestion, processing, and management
- Manages composite topology creation and merging
- Coordinates with observer services for data collection

**Related Services:**
• `merge-service` - Merges topology data from multiple sources
• `hdm-analytics` - Processes and analyzes topology relationships  
• `ui-content` - Provides topology visualization and management UI
• `file-observer` / `rest-observer` - Collect raw topology data

**Common Configuration Patterns:**
```yaml
topology:
  merge:
    enabled: true
    sources: ["file", "rest", "kubernetes"]
  processing:
    deduplication: true
    validation: strict
```

**Typical Troubleshooting Steps:**
1. Check topology merge service status
2. Verify observer data ingestion
3. Review topology validation logs
4. Examine UI dashboard for errors
"""
    elif any(word in query.lower() for word in ['observer', 'ingestion', 'data']):
        response_type = "ASM Observer Analysis"
        primary_service = "observer-services"
        
        specific_response = f"""
🔍 **ASM Observer Services Analysis**

**Observer Types:**
• `file-observer` - Monitors file system changes and data files
• `rest-observer` - Collects data via REST API endpoints
• `kubernetes-observer` - Monitors Kubernetes cluster resources

**Data Flow:**
Raw Data → Observer → Processing → Topology Merge → Analytics → UI

**Common Issues & Solutions:**
1. **Data not appearing**: Check observer connectivity and permissions
2. **Performance issues**: Review batch sizes and processing intervals
3. **Validation errors**: Examine data format and schema compliance
"""
    else:
        response_type = "ASM General Analysis"
        primary_service = "multiple services"
        
        specific_response = f"""
🔍 **ASM System Analysis**

**Detected Context:** {', '.join(detected_services) if detected_services else 'General IBM ASM inquiry'}

**Key ASM Services:**
• **Topology Services** - Data ingestion, merging, composite creation
• **Observer Services** - Data collection from various sources  
• **Analytics Services** - Processing, aggregation, and analysis
• **UI Services** - Dashboard, visualization, management interface

**For specific help, try asking:**
• "How does ASM topology merge work?"
• "What observers collect Kubernetes data?"
• "Show me ASM analytics configuration"
"""
    
    # Add similar cases context if available
    context_addition = ""
    if similar_cases:
        context_addition += f"\n\n📊 **Similar Historical Cases Found:**\n"
        for case in similar_cases[:2]:
            context_addition += f"• {case.get('title', 'Case')} (similarity: {case.get('similarity_score', 0):.1%})\n"
    
    if cluster_insights and cluster_insights.get('common_services'):
        context_addition += f"\n🔧 **Related Services:** {', '.join(cluster_insights['common_services'][:3])}\n"
    
    if cluster_insights and cluster_insights.get('suggested_resolutions'):
        context_addition += f"\n💡 **Common Solutions:** {', '.join(cluster_insights['suggested_resolutions'][:2])}\n"
    
    return {
        "response": f"""🔵 **IBM ASM Knowledge Fusion**

**Query:** "{query}"

{response_type}

{specific_response}{context_addition}

---
*💡 Note: Backend services are running but endpoints need configuration. This response uses intelligent routing and ASM domain knowledge.*"""
    }

@app.get("/functions/openwebui")
async def get_openwebui_function():
    """
    Returns the OpenWebUI function code that should be uploaded
    """
    function_code = '''"""
Knowledge Fusion Function for OpenWebUI
Connects to the Knowledge Fusion API Gateway
"""

import json
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional

class Function:
    def __init__(self):
        self.gateway_url = "http://localhost:9000"  # Knowledge Fusion API Gateway
        self.name = "IBM Knowledge Fusion"
        self.description = "Advanced knowledge synthesis beyond basic RAG"
    
    async def __call__(
        self,
        query: str,
        __user__: Dict[str, Any],
        __conversation_id__: str,
        __message_id__: str,
        **kwargs
    ) -> str:
        """Main function called by OpenWebUI"""
        try:
            request_data = {
                "query": query,
                "conversation_id": __conversation_id__,
                "user_id": __user__.get("id", "anonymous"),
                "context": kwargs
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.gateway_url}/knowledge-fusion/query",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "No response from Knowledge Fusion")
                    else:
                        return f"Knowledge Fusion temporarily unavailable (status: {response.status})"
        except Exception as e:
            return f"Knowledge Fusion error: {str(e)}"

# Create function instance for OpenWebUI
function = Function()
'''
    
    return {
        "function_code": function_code,
        "instructions": [
            "1. Copy the function code above",
            "2. Go to OpenWebUI Admin Panel → Functions",
            "3. Click 'Add Function' and paste the code",
            "4. Save and enable the function",
            "5. The Knowledge Fusion function will appear in your chat interface"
        ],
        "gateway_url": "http://localhost:9000",
        "status": "ready_for_integration"
    }

if __name__ == "__main__":
    print("🚀 Starting Knowledge Fusion API Gateway on port 9000...")
    print("🔗 This gateway bridges OpenWebUI functions with Knowledge Fusion backend")
    print("📋 Access function code at: http://localhost:9000/functions/openwebui")
    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")