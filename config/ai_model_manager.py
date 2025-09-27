"""
Enhanced AI Model Integration for Knowledge Fusion Platform
Optimized for maximum intelligence with flexible model configuration
"""

import json
import os
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path

class AIModelManager:
    def __init__(self, config_path: str = None):
        """Initialize AI Model Manager with configuration"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "ai_models_config.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.ollama_base_url = self.config.get("ollama_configuration", {}).get("base_url", "http://localhost:11434")
        
    def _load_config(self) -> Dict[str, Any]:
        """Load AI model configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load AI model config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "active_profile": "granite_optimized",
            "model_profiles": {
                "granite_optimized": {
                    "primary_llm": "granite3.2:8b-instruct-q8.0",
                    "code_specialist": "granite3.2:8b",
                    "embedding_model": "nomic-embed-text",
                    "vision_model": "granite3.2-vision:2b"
                }
            },
            "ollama_configuration": {
                "base_url": "http://localhost:11434",
                "timeout": 300,
                "temperature": 0.3
            }
        }
    
    def get_active_profile(self) -> Dict[str, Any]:
        """Get the currently active model profile"""
        active_profile_name = self.config.get("active_profile", "granite_optimized")
        return self.config.get("model_profiles", {}).get(active_profile_name, {})
    
    def get_model_for_task(self, task: str) -> str:
        """Get the best model for a specific task"""
        profile = self.get_active_profile()
        
        task_mapping = {
            "reasoning": "primary_llm",
            "code_analysis": "code_specialist", 
            "embedding": "embedding_model",
            "vision": "vision_model",
            "general": "primary_llm",
            "synthesis": "primary_llm"
        }
        
        model_key = task_mapping.get(task, "primary_llm")
        return profile.get(model_key, "granite3.2:8b-instruct-q8.0")
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is available in Ollama"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]
                return model_name in available_models
            return False
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            return []
        except:
            return []
    
    def recommend_optimal_setup(self) -> Dict[str, Any]:
        """Recommend optimal model setup based on available models"""
        available = self.get_available_models()
        
        # Your current models
        granite_models = [m for m in available if "granite" in m.lower()]
        
        # Recommended models for maximum intelligence
        recommended = {
            "current_models": available,
            "granite_models": granite_models,
            "recommendations": {},
            "setup_commands": []
        }
        
        # Primary LLM recommendations (in order of preference)
        primary_options = [
            "llama3.1:8b",      # Best balance
            "llama3.1:70b",     # Maximum intelligence  
            "granite3.2:8b-instruct-q8.0",  # Your current
            "mistral:7b",       # Alternative
            "qwen2.5:14b"       # High performance
        ]
        
        for model in primary_options:
            if model in available:
                recommended["recommendations"]["primary_llm"] = model
                break
        
        # Code specialist recommendations
        code_options = [
            "codellama:13b",    # Optimal
            "codellama:34b",    # Maximum
            "codellama:7b",     # Efficient
            "granite3.2:8b"     # Your current
        ]
        
        for model in code_options:
            if model in available:
                recommended["recommendations"]["code_specialist"] = model
                break
        
        # Embedding model (essential for semantic search)
        if "nomic-embed-text" not in available:
            recommended["setup_commands"].append("ollama pull nomic-embed-text")
        
        # If no optimal models found, suggest installations
        if not recommended["recommendations"].get("primary_llm"):
            recommended["setup_commands"].extend([
                "ollama pull llama3.1:8b",
                "ollama pull codellama:13b",
                "ollama pull nomic-embed-text"
            ])
        
        return recommended
    
    def generate_configuration(self, models: Dict[str, str]) -> str:
        """Generate configuration for given models"""
        config = {
            "active_profile": "custom_optimized",
            "model_profiles": {
                "custom_optimized": {
                    "description": "Custom optimized configuration",
                    "primary_llm": models.get("primary_llm", "granite3.2:8b-instruct-q8.0"),
                    "code_specialist": models.get("code_specialist", "granite3.2:8b"), 
                    "embedding_model": models.get("embedding_model", "nomic-embed-text"),
                    "vision_model": models.get("vision_model", "granite3.2-vision:2b")
                }
            }
        }
        
        return json.dumps(config, indent=2)

# Usage example and testing
if __name__ == "__main__":
    manager = AIModelManager()
    
    print("🤖 AI Model Manager - Knowledge Fusion Platform")
    print("=" * 60)
    
    print("\n📋 Current Configuration:")
    profile = manager.get_active_profile()
    for key, value in profile.items():
        print(f"  {key}: {value}")
    
    print(f"\n🔍 Available Models:")
    available = manager.get_available_models()
    for model in available:
        print(f"  ✅ {model}")
    
    print(f"\n🎯 Recommended Setup:")
    recommendations = manager.recommend_optimal_setup()
    
    if recommendations["recommendations"]:
        print("  Optimal models found:")
        for task, model in recommendations["recommendations"].items():
            print(f"    {task}: {model}")
    
    if recommendations["setup_commands"]:
        print("  Suggested installations:")
        for cmd in recommendations["setup_commands"]:
            print(f"    {cmd}")
    
    print(f"\n🧠 Task-Specific Models:")
    tasks = ["reasoning", "code_analysis", "embedding", "vision"]
    for task in tasks:
        model = manager.get_model_for_task(task)
        available = "✅" if manager.is_model_available(model) else "❌"
        print(f"  {task}: {model} {available}")