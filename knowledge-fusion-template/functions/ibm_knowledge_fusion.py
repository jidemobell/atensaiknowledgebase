"""
OpenWebUI Custom Function for IBM Knowledge Fusion
This function integrates with your enhanced backend to provide
intelligent multi-source knowledge synthesis in chat conversations.
"""

import json
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

class Function:
    """
    IBM Knowledge Fusion Function for OpenWebUI
    
    This function provides intelligent conversational AI that combines:
    - Historical cases and knowledge
    - GitHub code repositories  
    - Documentation sources
    - Previous chat conversations
    - External APIs and real-time data
    """
    
    def __init__(self):
        # Configuration
        self.knowledge_fusion_url = "http://localhost:8002"  # Your enhanced backend
        self.function_id = "ibm_knowledge_fusion"
        self.name = "IBM Knowledge Fusion"
        self.description = "Intelligent multi-source knowledge synthesis for technical support"
        
        # IBM styling and branding
        self.ibm_colors = {
            "primary": "#0f62fe",
            "secondary": "#393939", 
            "success": "#24a148",
            "warning": "#f1c21b",
            "danger": "#da1e28"
        }

    async def __call__(
        self,
        query: str,
        __user__: Dict[str, Any],
        __conversation_id__: str,
        __message_id__: str,
        **kwargs
    ) -> str:
        """
        Main function called by OpenWebUI when user sends a message
        """
        try:
            # Prepare request for knowledge fusion backend
            fusion_request = {
                "query": query,
                "conversation_id": __conversation_id__,
                "user_id": __user__.get("id", "anonymous"),
                "preferred_sources": kwargs.get("preferred_sources", []),
                "context_window": kwargs.get("context_window", 5)
            }
            
            # Call knowledge fusion backend
            response = await self._call_knowledge_fusion(fusion_request)
            
            if response:
                # Format response with IBM styling and source attribution
                formatted_response = self._format_response(response)
                return formatted_response
            else:
                return self._fallback_response(query)
                
        except Exception as e:
            error_msg = f"Knowledge fusion error: {str(e)}"
            return self._format_error_response(error_msg)

    async def _call_knowledge_fusion(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call the enhanced knowledge fusion backend"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.knowledge_fusion_url}/knowledge-fusion/query",
                    json=request,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Knowledge fusion backend error: {response.status}")
                        return None
        except Exception as e:
            print(f"Error calling knowledge fusion backend: {e}")
            return None

    def _format_response(self, fusion_response: Dict[str, Any]) -> str:
        """Format the fusion response with IBM styling and clear source attribution"""
        
        response_text = fusion_response.get("response", "")
        sources_used = fusion_response.get("sources_used", [])
        confidence = fusion_response.get("confidence", 0.0)
        reasoning = fusion_response.get("reasoning", "")
        follow_ups = fusion_response.get("suggested_follow_ups", [])
        knowledge_areas = fusion_response.get("knowledge_areas_detected", [])
        
        # Build formatted response
        formatted_parts = []
        
        # Main response
        formatted_parts.append(f"**💡 IBM Knowledge Synthesis**\n")
        formatted_parts.append(f"{response_text}\n")
        
        # Confidence and reasoning
        confidence_emoji = self._get_confidence_emoji(confidence)
        formatted_parts.append(f"\n**{confidence_emoji} Analysis Confidence:** {confidence:.1%}")
        
        if reasoning:
            formatted_parts.append(f"**🔍 Reasoning:** {reasoning}")
        
        # Knowledge areas detected
        if knowledge_areas:
            areas_text = ", ".join([area.replace("_", " ").title() for area in knowledge_areas])
            formatted_parts.append(f"**🎯 Detected Areas:** {areas_text}")
        
        # Sources used
        if sources_used:
            formatted_parts.append(f"\n**📚 Knowledge Sources:**")
            for source in sources_used:
                source_emoji = self._get_source_emoji(source)
                source_name = source.replace("_", " ").title()
                formatted_parts.append(f"  {source_emoji} {source_name}")
        
        # Follow-up suggestions
        if follow_ups:
            formatted_parts.append(f"\n**❓ Follow-up Options:**")
            for i, follow_up in enumerate(follow_ups, 1):
                formatted_parts.append(f"  {i}. {follow_up}")
        
        # IBM branding footer
        formatted_parts.append(f"\n---")
        formatted_parts.append(f"*🔵 Powered by IBM Knowledge Fusion Platform*")
        
        return "\n".join(formatted_parts)

    def _get_confidence_emoji(self, confidence: float) -> str:
        """Get emoji based on confidence level"""
        if confidence >= 0.8:
            return "🟢"  # High confidence
        elif confidence >= 0.6:
            return "🟡"  # Medium confidence
        else:
            return "🔴"  # Low confidence

    def _get_source_emoji(self, source: str) -> str:
        """Get emoji for different knowledge sources"""
        source_emojis = {
            "cases": "📋",           # Historical cases
            "github_code": "💻",     # Code repositories
            "documentation": "📖",   # Documentation
            "chat_history": "💬",    # Previous conversations
            "external_apis": "🌐",   # External API data
            "real_time_logs": "📊"   # Real-time monitoring
        }
        return source_emojis.get(source, "📄")

    def _fallback_response(self, query: str) -> str:
        """Fallback response when knowledge fusion is unavailable"""
        return f"""**⚠️ Knowledge Fusion Temporarily Unavailable**

I understand you're asking about: "{query}"

I'm currently unable to access the full knowledge fusion system, but I can still help you with general guidance. 

**🔵 IBM Support Options:**
- Check the knowledge base for similar issues
- Review documentation for your specific service
- Contact your system administrator for technical support

*Would you like me to try processing your request again, or can I help in another way?*

---
*🔵 IBM Knowledge Fusion Platform*"""

    def _format_error_response(self, error_msg: str) -> str:
        """Format error responses with IBM styling"""
        return f"""**🚨 System Error**

{error_msg}

**🔧 Troubleshooting Steps:**
1. Check if the knowledge fusion backend is running
2. Verify network connectivity
3. Try your request again in a moment

*If the issue persists, please contact system support.*

---
*🔵 IBM Knowledge Fusion Platform*"""

# OpenWebUI Function Metadata
def get_function_metadata():
    """Return function metadata for OpenWebUI registration"""
    return {
        "id": "ibm_knowledge_fusion",
        "name": "IBM Knowledge Fusion",
        "description": "Intelligent multi-source knowledge synthesis for technical support and troubleshooting",
        "author": "IBM AIOps Team",
        "version": "1.0.0",
        "type": "function",
        "requirements": ["aiohttp", "asyncio"],
        "parameters": {
            "preferred_sources": {
                "type": "array",
                "description": "Preferred knowledge sources to prioritize",
                "items": {
                    "type": "string",
                    "enum": ["cases", "github_code", "documentation", "chat_history", "external_apis"]
                },
                "default": []
            },
            "context_window": {
                "type": "integer",
                "description": "Number of previous messages to consider for context",
                "minimum": 1,
                "maximum": 20,
                "default": 5
            }
        }
    }

# For OpenWebUI integration
function = Function()
