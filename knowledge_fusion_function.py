"""
Title: IBM Knowledge Fusion
Author: IBM AIOps Team
Version: 1.0.0
"""

from fastapi import Request
import json
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional, Callable, Awaitable
from pydantic import BaseModel, Field
import logging


class Pipe:
    """
    IBM Knowledge Fusion Pipe for OpenWebUI
    Advanced knowledge synthesis beyond basic RAG
    """
    
    class Valves(BaseModel):
        """Configuration for the Knowledge Fusion function"""
        GATEWAY_URL: str = Field(
            default="http://localhost:9000",
            description="Knowledge Fusion API Gateway URL"
        )
        TIMEOUT: int = Field(
            default=30,
            description="Request timeout in seconds"
        )
        ENABLED: bool = Field(
            default=True,
            description="Enable/disable Knowledge Fusion"
        )

    def __init__(self):
        self.type = "pipe"
        self.id = "ibm_knowledge_fusion"
        self.name = "IBM Knowledge Fusion"
        self.valves = self.Valves()

    def get_provider_models(self):
        """Return available models for this pipe"""
        return [
            {"id": "knowledge-fusion", "name": "Knowledge Fusion Gateway"},
        ]

    async def emit_event_safe(self, message):
        """Safely emit events to OpenWebUI"""
        event_data = {
            "type": "message",
            "data": {"content": message + "\n"},
        }
        try:
            if hasattr(self, 'event_emitter') and self.event_emitter:
                await self.event_emitter(event_data)
        except Exception as e:
            logging.error(f"Error emitting event: {e}")

    async def pipe(
        self,
        body: dict,
        __user__: Optional[dict],
        __request__: Request,
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
    ) -> str:
        """
        Main pipe method called by OpenWebUI when user sends a message
        """
        self.event_emitter = __event_emitter__
        
        if not self.valves.ENABLED:
            return "Knowledge Fusion is currently disabled."
        
        # Extract the user's message
        try:
            latest_message = body["messages"][-1]["content"]
            if isinstance(latest_message, list):
                # Handle multipart content (text + images)
                text_content = ""
                for content in latest_message:
                    if content.get("type") == "text":
                        text_content += content.get("text", "")
                latest_message = text_content
        except (KeyError, IndexError):
            return "❌ No message content found."

        # await self.emit_event_safe("🔍 Routing query to Knowledge Fusion Gateway...")
            
        try:
            request_data = {
                "query": latest_message,
                "conversation_id": body.get("conversation_id", "unknown"),
                "user_id": __user__.get("id", "anonymous") if __user__ else "anonymous",
                "context": {
                    "model": body.get("model", "unknown"),
                    "temperature": body.get("temperature", 0.7),
                    "messages": body.get("messages", [])
                }
            }
            
            async with aiohttp.ClientSession() as session:
                # Try Phase 2 Multi-Agent intelligent routing first
                async with session.post(
                    f"{self.valves.GATEWAY_URL}/knowledge-fusion/intelligent",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.valves.TIMEOUT)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # processing_mode = result.get("processing_details", {}).get("multi_agent_enabled", False)
                        # if processing_mode:
                        #     await self.emit_event_safe("🤖 Multi-Agent Intelligence response received")
                        # else:
                        #     await self.emit_event_safe("✅ Knowledge Fusion response received")
                        return result.get("response", "No response from Knowledge Fusion")
                    elif response.status == 404:
                        # Multi-agent endpoint not available, fall back to standard processing
                        # await self.emit_event_safe("🔄 Multi-agent not available, using standard processing...")
                        return await self._fallback_to_standard_processing(request_data)
                    else:
                        # await self.emit_event_safe(f"⚠️ Gateway returned status {response.status}")
                        return f"🔧 Knowledge Fusion temporarily unavailable (status: {response.status})\n\nPlease check if the Knowledge Fusion Gateway is running on port 9000."
                        
        except aiohttp.ClientTimeout:
            # await self.emit_event_safe("⏱️ Request timed out")
            return f"⏱️ Knowledge Fusion request timed out after {self.valves.TIMEOUT} seconds.\n\nPlease try again or check the gateway status."
            
        except aiohttp.ClientConnectorError:
            # await self.emit_event_safe("🔌 Connection failed")
            return f"🔌 Cannot connect to Knowledge Fusion Gateway at {self.valves.GATEWAY_URL}\n\nPlease ensure the gateway is running on port 9000."
            
        except Exception as e:
            # await self.emit_event_safe(f"❌ Error: {str(e)}")
            return f"❌ Knowledge Fusion error: {str(e)}\n\nPlease contact system administrator if this persists."
    
    async def _fallback_to_standard_processing(self, request_data):
        """Fallback to standard Phase 1 processing when multi-agent is unavailable"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.valves.GATEWAY_URL}/knowledge-fusion/query",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.valves.TIMEOUT)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # await self.emit_event_safe("✅ Standard processing response received")
                        return result.get("response", "No response from Knowledge Fusion")
                    else:
                        return f"🔧 Knowledge Fusion unavailable (status: {response.status})"
        except Exception as e:
            return f"❌ Fallback processing failed: {str(e)}"

