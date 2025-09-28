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
        """Get analysis from Core Backend AI system"""
        try:
            async with aiohttp.ClientSession() as session:
                core_request = {
                    "query": request.query,
                    "session_id": request.conversation_id or "unified"
                }
                
                async with session.post(
                    f"{CORE_BACKEND_URL}/query",
                    json=core_request,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info("✅ Core Backend analysis received")
                        return result
                    else:
                        logger.warning(f"Core Backend returned {response.status}")
                        
        except Exception as e:
            logger.error(f"Core Backend error: {e}")
        
        # Fallback analysis
        return {
            "response": "Core Backend analysis unavailable",
            "confidence": 0.3,
            "similar_cases": [],
            "analysis": "Fallback mode - Core Backend not accessible"
        }
    
    def _create_fusion_prompt(self, query: str, core_analysis: Dict[str, Any]) -> str:
        """Create enhanced prompt that fuses Core Backend analysis with AI synthesis"""
        
        # Extract key information from Core Backend
        core_response = core_analysis.get("response", "")
        confidence = core_analysis.get("confidence", 0.0)
        similar_cases = core_analysis.get("similar_cases", [])
        technical_analysis = core_analysis.get("analysis", "")
        
        # Build comprehensive fusion prompt
        fusion_prompt = f"""You are an expert IBM ASM (Agile Service Manager) consultant with access to advanced technical analysis.

TECHNICAL ANALYSIS FROM CORE SYSTEM:
Core Response: {core_response}
Confidence Level: {confidence}
Technical Analysis: {technical_analysis}

SIMILAR CASES FOUND:
{self._format_similar_cases(similar_cases)}

ASM DOMAIN EXPERTISE:
Services: {', '.join(self.asm_expertise['services'].keys())}
Architecture: {self.asm_expertise['architecture']['data_flow']}
Common Patterns: {', '.join(self.asm_expertise['common_patterns'])}

USER QUERY: {query}

TASK: Provide a comprehensive, intelligent response that:
1. Synthesizes the technical analysis with your ASM expertise
2. Addresses the user's specific question with actionable guidance
3. Uses the similar cases to provide relevant context
4. Explains complex concepts clearly
5. Provides practical next steps

Focus on being helpful, accurate, and ASM-specific. If the technical analysis has low confidence, rely more on your ASM expertise.

RESPONSE:"""
        
        return fusion_prompt
    
    def _format_similar_cases(self, similar_cases: List[Dict]) -> str:
        """Format similar cases for the prompt"""
        if not similar_cases:
            return "No similar cases found"
        
        formatted = []
        for i, case in enumerate(similar_cases[:3], 1):
            case_text = case.get('description', case.get('title', 'Case description'))
            formatted.append(f"{i}. {case_text[:100]}...")
        
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
                        if ai_response:
                            logger.info("✅ Granite AI synthesis completed")
                            return ai_response
                            
        except Exception as e:
            logger.error(f"Granite synthesis error: {e}")
        
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