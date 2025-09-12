# 🌐 OpenWebUI Setup Guide - Model Management

## 🎯 Overview

This guide explains how to configure OpenWebUI to manage your AI models for the Novel Knowledge Fusion Platform. OpenWebUI provides an excellent interface for model management while your backend handles specialized processing.

## 🏗️ OpenWebUI Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   OpenWebUI Frontend                       │
│                    (Port 8080)                             │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ Chat Interface  │  │ Model Manager   │                  │
│  │ - User queries  │  │ - Model list    │                  │  
│  │ - Conversations │  │ - Add/Remove    │                  │
│  │ - History       │  │ - Configure     │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────┬───────────────────────────────────┘
                         │
┌─────────────────────────┴───────────────────────────────────┐
│                   Model Sources                            │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Ollama (Local)  │  │ OpenAI API      │  │ Anthropic    │ │
│  │ - Llama 3.1     │  │ - GPT-4 Turbo   │  │ - Claude 3.5 │ │
│  │ - Mistral       │  │ - GPT-3.5       │  │ - Claude 3   │ │
│  │ - Granite       │  │ - Embeddings    │  │ - Haiku      │ │
│  │ - Code Llama    │  │                 │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Step-by-Step Setup

### 1. Install Ollama (Local Models)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve &

# Pull recommended models for your use case
ollama pull llama3.1:8b      # Fast, general purpose
ollama pull mistral:7b       # Good reasoning
ollama pull granite3-moe:3b  # IBM-optimized
ollama pull codellama:7b     # Code analysis
ollama pull nomic-embed-text # Embeddings
```

### 2. Configure OpenWebUI

```bash
# Navigate to OpenWebUI directory
cd /Users/jidemobell/Documents/IBMALL/TOPOLOGYKNOWLEDGE/openwebuibase

# Install dependencies
npm install

# Start OpenWebUI
npm run dev

# Access at http://localhost:8080
```

### 3. Verify Ollama Integration

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Should show your installed models
```

### 4. Add API-Based Models

#### OpenAI Integration:
1. Go to OpenWebUI Settings → Connections
2. Add OpenAI Connection:
   ```
   Name: OpenAI Production
   API URL: https://api.openai.com/v1
   API Key: your_openai_api_key
   ```
3. Available models will appear automatically:
   - gpt-4-turbo
   - gpt-3.5-turbo
   - text-embedding-3-large

#### Anthropic Integration:
1. Settings → Connections → Add Connection
2. Add Anthropic:
   ```
   Name: Anthropic Claude
   API URL: https://api.anthropic.com
   API Key: your_anthropic_api_key
   ```
3. Models available:
   - claude-3-5-sonnet-20241022
   - claude-3-haiku-20240307

## 🔧 Model Configuration for Your Novel Platform

### 1. Chat Interface Models (Frontend)
Configure these for user conversations:

```json
{
  "recommended_chat_models": {
    "fast_responses": "llama3.1:8b",
    "high_quality": "gpt-4-turbo", 
    "code_focused": "codellama:7b",
    "cost_effective": "mistral:7b"
  }
}
```

### 2. Integration with Your Backend

Your Novel Fusion Platform can call OpenWebUI's models:

```python
# In your main_novel_architecture.py
import aiohttp

class OpenWebUIModelClient:
    def __init__(self, openwebui_url="http://localhost:8080"):
        self.base_url = openwebui_url
    
    async def generate_response(self, model: str, prompt: str):
        """Use OpenWebUI models from your backend"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                return await response.json()
    
    async def get_available_models(self):
        """Get list of models available in OpenWebUI"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/models") as response:
                return await response.json()
```

### 3. Smart Model Routing

```python
# Add to your knowledge fusion platform
class ModelRouter:
    def __init__(self):
        self.openwebui_client = OpenWebUIModelClient()
        self.direct_api_client = DirectAPIClient()  # Your direct API calls
    
    async def route_request(self, query_type: str, content: str):
        """Smart routing between OpenWebUI and direct APIs"""
        
        if query_type == "user_chat":
            # Use OpenWebUI for user-facing conversations
            return await self.openwebui_client.generate_response(
                model="llama3.1:8b", 
                prompt=content
            )
        
        elif query_type == "temporal_synthesis":
            # Use direct API for specialized processing
            return await self.direct_api_client.temporal_analysis(content)
        
        elif query_type == "knowledge_fusion":
            # Use your novel fusion approach
            return await self.fusion_synthesis(content)
```

## 🎛️ Advanced OpenWebUI Configuration

### 1. Custom Model Parameters

```javascript
// In OpenWebUI settings, configure model parameters
{
  "temperature": 0.7,      // Creativity vs consistency
  "max_tokens": 2048,      // Response length
  "top_p": 0.9,           // Nucleus sampling
  "frequency_penalty": 0,  // Repetition control
  "presence_penalty": 0    // Topic exploration
}
```

### 2. Model Presets for Different Tasks

```json
{
  "model_presets": {
    "creative_writing": {
      "model": "mistral:7b",
      "temperature": 0.9,
      "max_tokens": 1500
    },
    "technical_analysis": {
      "model": "granite3-moe:3b", 
      "temperature": 0.3,
      "max_tokens": 2048
    },
    "code_review": {
      "model": "codellama:7b",
      "temperature": 0.2,
      "max_tokens": 1000
    }
  }
}
```

### 3. Integration with Your Research Foundation

Based on your research document, configure models for specific techniques:

```python
# Map research techniques to OpenWebUI models
class ResearchModelMapping:
    TECHNIQUES = {
        "GraphRAG": {
            "model": "claude-3-5-sonnet",
            "purpose": "Knowledge graph reasoning"
        },
        "ReAct": {
            "model": "gpt-4-turbo", 
            "purpose": "Tool-augmented reasoning"
        },
        "PAL": {
            "model": "codellama:7b",
            "purpose": "Program-aided language"
        },
        "Toolformer": {
            "model": "granite3-moe:3b",
            "purpose": "Tool learning"
        }
    }
```

## 🔌 API Endpoints for Integration

### OpenWebUI API Endpoints Your Backend Can Use:

```bash
# Get available models
GET http://localhost:8080/api/models

# Generate response
POST http://localhost:8080/api/generate
{
  "model": "llama3.1:8b",
  "prompt": "Your query here",
  "stream": false
}

# Chat completion
POST http://localhost:8080/api/chat/completions  
{
  "model": "gpt-4-turbo",
  "messages": [
    {"role": "user", "content": "Your message"}
  ]
}

# Get model info
GET http://localhost:8080/api/models/{model_name}
```

### Example Integration in Your Backend:

```python
# In your enhanced_backend/main_novel_architecture.py
@app.post("/synthesize")
async def synthesize_knowledge(request: KnowledgeRequest):
    """Novel synthesis using OpenWebUI + Direct APIs"""
    
    # 1. Use OpenWebUI for initial processing
    initial_response = await openwebui_client.generate_response(
        model="mistral:7b",
        prompt=f"Initial analysis of: {request.query}"
    )
    
    # 2. Use direct API for specialized synthesis
    synthesis = await anthropic_client.advanced_synthesis(
        query=request.query,
        context=initial_response
    )
    
    # 3. Your novel temporal fusion
    temporal_analysis = await self.temporal_knowledge_fusion(
        query=request.query,
        synthesis=synthesis
    )
    
    return {
        "response": temporal_analysis,
        "approach": "hybrid_openwebui_plus_direct_api",
        "confidence": 0.89
    }
```

## 📊 Model Performance Monitoring

### 1. Track Model Usage

```python
# Add monitoring to your platform
class ModelUsageTracker:
    def __init__(self):
        self.usage_stats = {}
    
    async def track_model_call(self, model: str, tokens: int, cost: float):
        if model not in self.usage_stats:
            self.usage_stats[model] = {
                "calls": 0,
                "tokens": 0, 
                "cost": 0.0
            }
        
        self.usage_stats[model]["calls"] += 1
        self.usage_stats[model]["tokens"] += tokens
        self.usage_stats[model]["cost"] += cost
    
    def get_usage_report(self):
        return self.usage_stats
```

### 2. Model Performance Dashboard

```bash
# Add endpoint to monitor model performance
curl http://localhost:8003/model-stats
```

```json
{
  "model_performance": {
    "llama3.1:8b": {
      "avg_response_time": "1.2s",
      "success_rate": "98%",
      "total_calls": 1250
    },
    "gpt-4-turbo": {
      "avg_response_time": "3.1s", 
      "success_rate": "99.5%",
      "total_calls": 456
    }
  }
}
```

## 🎯 Best Practices

### 1. Model Selection Strategy
- **Fast queries**: Ollama local models (llama3.1, mistral)
- **Complex reasoning**: OpenAI/Anthropic APIs (gpt-4, claude-3.5)
- **Code analysis**: CodeLlama or specialized models
- **Embeddings**: Local embedding models or OpenAI embeddings

### 2. Cost Optimization
```python
# Implement cost-aware routing
class CostAwareRouter:
    MODEL_COSTS = {
        "llama3.1:8b": 0.0,        # Free local
        "mistral:7b": 0.0,         # Free local  
        "gpt-3.5-turbo": 0.002,    # $2/1M tokens
        "gpt-4-turbo": 0.01,       # $10/1M tokens
        "claude-3-5-sonnet": 0.003 # $3/1M tokens
    }
    
    def select_model(self, complexity: str, budget: float):
        if budget == 0:
            return "llama3.1:8b"  # Free local
        elif complexity == "high" and budget > 0.01:
            return "gpt-4-turbo"  # Best quality
        else:
            return "claude-3-5-sonnet"  # Good balance
```

### 3. Fallback Strategy
```python
# Implement model fallbacks
async def generate_with_fallback(prompt: str):
    try:
        # Try premium model first
        return await openai_generate(prompt)
    except Exception:
        try:
            # Fallback to alternative
            return await anthropic_generate(prompt)
        except Exception:
            # Final fallback to local
            return await ollama_generate(prompt)
```

## 🚨 Troubleshooting

### Common Issues:

#### Ollama Models Not Appearing:
```bash
# Check Ollama service
ollama list
ollama serve

# Restart OpenWebUI
npm run dev
```

#### API Key Issues:
```bash
# Verify API keys
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

#### Model Loading Errors:
```bash
# Check model status
curl http://localhost:11434/api/show -d '{"name": "llama3.1:8b"}'
```

## 🔄 Next Steps

1. **Test model integration**: Verify all models work through OpenWebUI
2. **Configure your backend**: Integrate OpenWebUI API calls
3. **Implement smart routing**: Right model for right task
4. **Monitor performance**: Track usage and costs
5. **Optimize selection**: Balance quality vs cost vs speed

## 📚 Related Guides

- **[Model Integration Guide](./MODEL_INTEGRATION.md)** - Detailed API integration
- **[Docker Deployment Guide](./DOCKER_DEPLOYMENT.md)** - Containerized setup
- **[Performance Optimization](./PERFORMANCE_OPTIMIZATION.md)** - Speed and cost optimization

---

*OpenWebUI provides excellent model management while your Novel Knowledge Fusion Platform handles the specialized processing that makes your approach unique.*
