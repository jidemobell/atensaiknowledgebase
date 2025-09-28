"""
Unified Knowledge Fusion System - True Integration
Both backends work together as a single intelligent unit
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import aiohttp
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Unified Knowledge Fusion System", 
    version="3.0.0",
    description="True knowledge fusion - Core Backend + AI Synthesis working as one"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UnifiedQueryRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class FusedKnowledgeResponse(BaseModel):
    response: str
    core_analysis: Dict[str, Any]
    ai_synthesis: str
    confidence: float
    sources_used: List[str]
    reasoning_trace: Dict[str, Any]
    suggested_follow_ups: List[str]
    conversation_id: str

# Configuration
CORE_BACKEND_URL = "http://localhost:8001"
OLLAMA_URL = "http://localhost:11434" 
GRANITE_MODEL = "granite3.2:8b"

class UnifiedKnowledgeFusionEngine:
    """
    Unified engine that combines Core Backend analysis with AI synthesis
    Creates true knowledge fusion instead of separate systems
    """
    
    def __init__(self):
        self.asm_expertise = self._load_asm_expertise()
        
    def _load_asm_expertise(self) -> Dict[str, Any]:
        """Load ASM domain expertise for enhanced prompts"""
        return {
            "services": {
                "nasm-topology": "Core topology data processing and management service",
                "hdm-analytics": "Analytics and monitoring service for ASM data",
                "ui-content": "Dashboard and user interface management",
                "observer-services": "Data collection from multiple sources",
                "file-observer": "Monitors file system changes and data files",
                "rest-observer": "Collects data via REST API endpoints",
                "kubernetes-observer": "Monitors Kubernetes cluster resources"
            },
            "architecture": {
                "data_flow": "External Sources → Observers → Topology Service → Analytics → UI",
                "layers": ["Data Ingestion", "Processing", "Presentation", "Storage"]
            },
            "common_patterns": [
                "check service health and connectivity",
                "verify data source configuration", 
                "review topology merge settings",
                "analyze processing logs",
                "validate dashboard connectivity"
            ]
        }
    
    async def unified_knowledge_fusion(self, request: UnifiedQueryRequest) -> FusedKnowledgeResponse:
        """
        TRUE KNOWLEDGE FUSION: Combines Core Backend + AI Synthesis
        """
        query = request.query
        logger.info(f"🔄 Unified fusion processing: {query}")
        
        # Phase 1: Get technical analysis from Core Backend
        core_analysis = await self._get_core_backend_analysis(request)
        
        # Phase 2: Enhance with AI synthesis using Core Backend results
        enhanced_prompt = self._create_fusion_prompt(query, core_analysis)
        ai_synthesis = await self._get_granite_synthesis(enhanced_prompt)
        
        # Phase 3: Fuse both analyses into unified response
        fused_response = await self._fuse_knowledge(query, core_analysis, ai_synthesis)
        
        # Phase 4: Generate intelligent follow-ups based on both systems
        follow_ups = await self._generate_unified_follow_ups(query, core_analysis, ai_synthesis)
        
        return FusedKnowledgeResponse(
            response=fused_response,
            core_analysis=core_analysis,
            ai_synthesis=ai_synthesis,
            confidence=self._calculate_unified_confidence(core_analysis, ai_synthesis),
            sources_used=["core_backend_analysis", "granite_ai_synthesis", "asm_expertise"],
            reasoning_trace={
                "core_backend_confidence": core_analysis.get("confidence", 0.5),
                "ai_synthesis_quality": "high" if ai_synthesis else "fallback",
                "fusion_method": "unified_knowledge_synthesis",
                "asm_domain_detected": self._detect_asm_domain(query)
            },
            suggested_follow_ups=follow_ups,
            conversation_id=request.conversation_id or "unified"
        )
    
    async def _get_core_backend_analysis(self, request: UnifiedQueryRequest) -> Dict[str, Any]:
        """Get analysis with case search from Core Backend AI system"""
        try:
            async with aiohttp.ClientSession() as session:
                # Use the unified search endpoint for proper case retrieval
                search_request = {
                    "query": request.query,
                    "search_mode": "all",  # Search across all knowledge sources
                    "session_id": request.conversation_id or "unified",
                    "filters": {}
                }
                
                async with session.post(
                    f"{CORE_BACKEND_URL}/api/search",
                    json=search_request,
                    timeout=aiohttp.ClientTimeout(total=20)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ Core Backend search received: {result.get('total_results', 0)} results")
                        
                        # Format the search results into analysis format
                        formatted_result = {
                            "query": request.query,
                            "total_results": result.get('total_results', 0),
                            "case_results": result.get('case_results', []),
                            "code_results": result.get('code_results', []),
                            "doc_results": result.get('doc_results', []),
                            "suggestions": result.get('suggestions', []),
                            "confidence": min(0.9, result.get('total_results', 0) * 0.1),  # Higher confidence with more results
                            "search_metadata": {
                                "search_mode": "unified",
                                "has_case_matches": len(result.get('case_results', [])) > 0,
                                "has_code_matches": len(result.get('code_results', [])) > 0,
                                "has_doc_matches": len(result.get('doc_results', [])) > 0
                            }
                        }
                        return formatted_result
                    else:
                        logger.warning(f"Core Backend search returned {response.status}")
                        
        except Exception as e:
            logger.error(f"Core Backend search error: {e}")
        
        # Fallback analysis
        return {
            "response": "Core Backend analysis unavailable",
            "confidence": 0.3,
            "similar_cases": [],
            "analysis": "Fallback mode - Core Backend not accessible"
        }
    
    def _create_fusion_prompt(self, query: str, core_analysis: Dict[str, Any]) -> str:
        """Create enhanced prompt that fuses Core Backend search results with AI synthesis"""
        
        # Extract search results from Core Backend
        total_results = core_analysis.get("total_results", 0)
        case_results = core_analysis.get("case_results", [])
        code_results = core_analysis.get("code_results", [])
        doc_results = core_analysis.get("doc_results", [])
        confidence = core_analysis.get("confidence", 0.0)
        search_metadata = core_analysis.get("search_metadata", {})
        
        # Build comprehensive fusion prompt with actual retrieved knowledge
        fusion_prompt = f"""You are an expert IBM ASM (Agile Service Manager) consultant with access to retrieved knowledge from {total_results} relevant sources.

RETRIEVED KNOWLEDGE FROM CASE DATABASE:
{self._format_case_results(case_results)}

RETRIEVED CODE KNOWLEDGE:
{self._format_code_results(code_results)}

RETRIEVED DOCUMENTATION:
{self._format_doc_results(doc_results)}

SEARCH METADATA:
- Total Results Found: {total_results}
- Cases Found: {len(case_results)}
- Code References: {len(code_results)}
- Documentation: {len(doc_results)}
- Search Confidence: {confidence:.2f}

ASM DOMAIN EXPERTISE:
Services: {', '.join(self.asm_expertise['services'].keys())}
Architecture: {self.asm_expertise['architecture']['data_flow']}
Common Patterns: {', '.join(self.asm_expertise['common_patterns'])}

USER QUERY: {query}

TASK: Provide a comprehensive, intelligent response that:
1. Uses the RETRIEVED KNOWLEDGE to provide specific, relevant solutions
2. References actual case numbers, code examples, and documentation when available
3. Addresses the user's specific question with actionable guidance
4. Explains complex concepts clearly with examples from the retrieved knowledge
5. Provides practical next steps based on similar resolved cases

Focus on being helpful, accurate, and ASM-specific. Use the retrieved knowledge as your primary source, supplemented by your ASM expertise.

RESPONSE:"""
        
        return fusion_prompt
    
    def _format_case_results(self, case_results: List[Dict]) -> str:
        """Format case search results for the prompt"""
        if not case_results:
            return "No relevant cases found"
        
        formatted = []
        for i, case in enumerate(case_results[:5], 1):  # Top 5 cases
            case_number = case.get('case_number', case.get('id', f'Case-{i}'))
            title = case.get('title', 'Untitled Case')
            description = case.get('description', case.get('full_text_for_rag', ''))[:200]
            services = case.get('affected_services', case.get('services', []))
            severity = case.get('severity', 'Unknown')
            search_score = case.get('search_score', 0)
            
            formatted.append(f"""
Case {i}: {case_number}
Title: {title}
Severity: {severity}
Services: {', '.join(services[:3])}
Description: {description}...
Relevance Score: {search_score:.2f}
""")
        
        return "\n".join(formatted)
    
    def _format_code_results(self, code_results: List[Dict]) -> str:
        """Format code search results for the prompt"""
        if not code_results:
            return "No relevant code found"
        
        formatted = []
        for i, code in enumerate(code_results[:3], 1):  # Top 3 code results
            repo = code.get('repository', 'Unknown Repo')
            file_path = code.get('file_path', 'Unknown File')
            content = code.get('code_content', '')[:150]
            
            formatted.append(f"""
Code {i}: {repo}/{file_path}
Content: {content}...
""")
        
        return "\n".join(formatted)
    
    def _format_doc_results(self, doc_results: List[Dict]) -> str:
        """Format documentation search results for the prompt"""
        if not doc_results:
            return "No relevant documentation found"
        
        formatted = []
        for i, doc in enumerate(doc_results[:3], 1):  # Top 3 docs
            title = doc.get('title', 'Untitled Document')
            doc_type = doc.get('doc_type', 'documentation')
            content = doc.get('content', '')[:150]
            source_url = doc.get('source_url', '')
            
            formatted.append(f"""
Doc {i}: {title} ({doc_type})
Content: {content}...
Source: {source_url}
""")
        
        return "\n".join(formatted)
    
    async def _get_granite_synthesis(self, prompt: str) -> str:
        """Get AI synthesis from granite model"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": GRANITE_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 1500
                    }
                }
                
                async with session.post(
                    f"{OLLAMA_URL}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result.get("response", "").strip()
                        if ai_response and len(ai_response) > 20:  # Ensure substantial response
                            logger.info("✅ Granite AI synthesis completed")
                            return ai_response
                        else:
                            logger.warning("Granite returned empty/short response, using fallback")
                    else:
                        logger.warning(f"Granite returned status {response.status}")
                            
        except asyncio.TimeoutError:
            logger.error("Granite synthesis timeout - model may be busy")
        except Exception as e:
            logger.error(f"Granite synthesis error: {str(e)}")
        
        return ""
    
    async def _fuse_knowledge(self, query: str, core_analysis: Dict[str, Any], ai_synthesis: str) -> str:
        """Fuse Core Backend analysis with AI synthesis into unified response"""
        
        if ai_synthesis:
            # AI synthesis successful - this is our primary response
            fused = ai_synthesis
            
            # Add technical details from Core Backend if relevant
            if core_analysis.get("confidence", 0) > 0.5:
                technical_note = f"\n\n**Technical Analysis:** {core_analysis.get('analysis', '')}"
                if len(technical_note.strip()) > 25:  # Only add if substantial
                    fused += technical_note
            
            return fused
        
        else:
            # AI synthesis failed - use enhanced Core Backend response
            core_response = core_analysis.get("response", "")
            confidence = core_analysis.get("confidence", 0.0)
            
            if confidence > 0.4:
                return f"""**ASM Analysis Based on Technical Diagnosis:**

{core_response}

**Confidence:** {confidence:.1%}

**Recommended Approach:**
{self._generate_approach_from_core(query, core_analysis)}

*Note: This response combines technical analysis with ASM best practices.*"""
            else:
                return self._generate_fallback_response(query)
    
    def _generate_approach_from_core(self, query: str, core_analysis: Dict[str, Any]) -> str:
        """Generate approach based on Core Backend analysis"""
        approaches = []
        
        # Add relevant common patterns
        query_lower = query.lower()
        for pattern in self.asm_expertise["common_patterns"]:
            if any(word in pattern.lower() for word in query_lower.split()):
                approaches.append(f"• {pattern}")
        
        if not approaches:
            approaches = [
                "• Verify ASM service health and status",
                "• Check configuration and connectivity", 
                "• Review logs for detailed diagnostics"
            ]
        
        return "\n".join(approaches[:3])
    
    def _generate_fallback_response(self, query: str) -> str:
        """Generate intelligent fallback when both systems have issues"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['hello', 'hi', 'test']):
            return """Hello! I'm your unified ASM Knowledge Fusion assistant.

I combine technical analysis with AI synthesis to provide comprehensive ASM guidance.

**I can help with:**
• ASM topology and observer configuration
• Service troubleshooting and optimization
• Best practices and architectural guidance
• Integration patterns and data flow analysis

What specific ASM challenge can I help you with?"""
        
        # Specific ASM sync question handling
        if 'sync' in query_lower and any(word in query_lower for word in ['kubernetes', 'k8s', 'asm']):
            return """**ASM Sync in Kubernetes Environments**

ASM topology synchronization in Kubernetes works through several key components:

**🔄 Sync Architecture:**
• **kubernetes-observer**: Monitors K8s cluster resources and events
• **nasm-topology**: Processes and correlates topology data
• **merge-service**: Synchronizes data from multiple sources
• **ui-content**: Provides real-time dashboard updates

**📊 Sync Process:**
1. **Data Collection**: kubernetes-observer watches K8s API for changes
2. **Processing**: nasm-topology processes resource relationships  
3. **Merging**: merge-service combines data from observers
4. **Storage**: Topology data stored in ASM knowledge base
5. **Visualization**: ui-content displays synchronized topology

**⚙️ Key Configuration:**
```yaml
observers:
  kubernetes-observer:
    cluster_url: "https://kubernetes.default.svc"
    sync_interval: "30s"
    watch_namespaces: ["default", "asm-system"]
```

**🔧 Common Sync Issues:**
• RBAC permissions for kubernetes-observer
• Network connectivity to K8s API server
• Resource quotas and rate limiting
• Merge conflicts with multiple data sources

**📋 Troubleshooting Steps:**
1. Check kubernetes-observer pod status: `oc get pods -l app=kubernetes-observer`
2. Verify service account permissions: `oc get clusterrolebinding`
3. Review sync logs: `oc logs -f deployment/kubernetes-observer`
4. Monitor merge service: `oc logs -f deployment/nasm-topology`

Would you like me to elaborate on any specific aspect of ASM sync configuration?"""
        
        # Domain-specific fallbacks
        domain = self._detect_asm_domain(query)
        if domain in self.asm_expertise["services"]:
            service_desc = self.asm_expertise["services"][domain]
            return f"""**ASM {domain.replace('-', ' ').title()} Guidance**

**Service Overview:** {service_desc}

**Common Tasks:**
• Service health monitoring and status checks
• Configuration review and optimization
• Integration and data flow verification
• Performance analysis and troubleshooting

**Next Steps:** Please provide more specific details about your {domain} requirements or issues for targeted assistance."""
        
        return f"""**ASM Knowledge Synthesis**

I can provide guidance on your ASM question: "{query}"

**ASM Architecture Context:**
• **Data Flow:** {self.asm_expertise['architecture']['data_flow']}
• **Key Services:** {', '.join(list(self.asm_expertise['services'].keys())[:4])}

**Recommended Approach:**
{self._generate_approach_from_core(query, {})}

For more specific guidance, please provide additional details about your ASM environment or the particular challenge you're facing."""
    
    def _detect_asm_domain(self, query: str) -> str:
        """Detect ASM domain from query"""
        query_lower = query.lower()
        
        for service in self.asm_expertise["services"]:
            if service.replace('-', ' ') in query_lower or service in query_lower:
                return service
        
        # Check for domain keywords
        if 'topology' in query_lower:
            return 'nasm-topology'
        elif 'observer' in query_lower:
            return 'observer-services'
        elif any(word in query_lower for word in ['ui', 'dashboard', 'interface']):
            return 'ui-content'
        elif 'analytics' in query_lower:
            return 'hdm-analytics'
        
        return 'asm-general'
    
    async def _generate_unified_follow_ups(self, query: str, core_analysis: Dict[str, Any], ai_synthesis: str) -> List[str]:
        """Generate intelligent follow-ups based on both Core Backend and AI analysis"""
        
        domain = self._detect_asm_domain(query)
        confidence = core_analysis.get("confidence", 0.5)
        
        follow_ups = []
        
        if domain == 'nasm-topology':
            follow_ups = [
                "How do I configure topology merge settings?",
                "What observers should I use for topology data collection?",
                "How can I troubleshoot topology service connectivity issues?"
            ]
        elif 'observer' in domain:
            follow_ups = [
                "How do I configure observer data collection?", 
                "What are the best practices for observer performance?",
                "How do I troubleshoot observer connectivity issues?"
            ]
        elif confidence < 0.5:
            follow_ups = [
                "Can you provide more specific details about your ASM environment?",
                "What error messages or symptoms are you seeing?",
                "Would you like guidance on ASM architecture and components?"
            ]
        else:
            follow_ups = [
                "Can you show me specific configuration examples?",
                "What are the best practices for this scenario?",
                "How do I implement monitoring for this component?"
            ]
        
        return follow_ups[:3]
    
    def _calculate_unified_confidence(self, core_analysis: Dict[str, Any], ai_synthesis: str) -> float:
        """Calculate unified confidence score"""
        core_confidence = core_analysis.get("confidence", 0.0)
        ai_confidence = 0.8 if ai_synthesis else 0.3
        
        # Weighted combination: 40% Core Backend, 60% AI synthesis
        unified_confidence = (core_confidence * 0.4) + (ai_confidence * 0.6)
        return min(0.95, unified_confidence)  # Cap at 95%

# Initialize unified engine
unified_engine = UnifiedKnowledgeFusionEngine()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check if Core Backend is accessible
    core_status = "unknown"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{CORE_BACKEND_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                core_status = "connected" if response.status == 200 else "error"
    except:
        core_status = "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "architecture": "unified_knowledge_fusion",
        "core_backend_status": core_status,
        "granite_model": GRANITE_MODEL,
        "fusion_capabilities": [
            "core_backend_integration",
            "granite_ai_synthesis", 
            "unified_knowledge_fusion",
            "asm_domain_expertise"
        ]
    }

@app.post("/unified-fusion")
async def unified_knowledge_fusion(request: UnifiedQueryRequest):
    """Unified Knowledge Fusion endpoint - true integration"""
    try:
        response = await unified_engine.unified_knowledge_fusion(request)
        return response.dict()
    except Exception as e:
        logger.error(f"Unified fusion error: {e}")
        raise HTTPException(status_code=500, detail=f"Knowledge fusion error: {str(e)}")

# Legacy endpoint for compatibility
@app.post("/knowledge-fusion/query")
async def legacy_knowledge_fusion(request: UnifiedQueryRequest):
    """Legacy endpoint redirects to unified fusion"""
    return await unified_knowledge_fusion(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)