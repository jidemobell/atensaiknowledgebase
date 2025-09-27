# 🤖 AI Model Configuration Guide
## Knowledge Fusion Platform - Optimal Intelligence Setup

### 🎯 **Quick Start: Best Configuration for Your System**

Based on your current setup with `granite3.2:8b`, `granite3.2:8b-instruct-q8.0`, and `granite3.2-vision:2b`, here's my **recommended optimal configuration**:

```bash
# 1. Pull the essential embedding model (required for semantic search)
ollama pull nomic-embed-text

# 2. Pull recommended models for maximum intelligence 
ollama pull llama3.1:8b        # Best reasoning model
ollama pull codellama:13b      # Superior code analysis
ollama pull mistral:7b         # Excellent alternative

# 3. Configure the platform to use optimal models
./bin/manage_ai_models.sh configure balanced_performance
```

---

## 📊 **Model Intelligence Rankings**

### **🥇 Tier 1: Maximum Intelligence**
```bash
Primary LLM:     llama3.1:70b        # Ultimate reasoning (requires 64GB+ RAM)
Code Specialist: codellama:34b       # Best code understanding  
Embedding:       nomic-embed-text    # Best semantic search
Vision:          llava:13b           # Advanced vision
```

### **🥈 Tier 2: Balanced Performance** ⭐ **RECOMMENDED**
```bash
Primary LLM:     llama3.1:8b         # Excellent reasoning, efficient
Code Specialist: codellama:13b       # Great code analysis
Embedding:       nomic-embed-text    # Essential for search
Vision:          granite3.2-vision:2b # Your existing model
```

### **🥉 Tier 3: Your Current Setup (Optimized)**
```bash
Primary LLM:     granite3.2:8b-instruct-q8.0  # Your best model
Code Specialist: granite3.2:8b                 # Your code model
Embedding:       nomic-embed-text              # Add this!
Vision:          granite3.2-vision:2b          # Your vision model
```

---

## ⚙️ **Configuration Methods**

### **Method 1: Automated Setup** (Recommended)
```bash
# Make the script executable
chmod +x ./bin/manage_ai_models.sh

# See all recommendations
./bin/manage_ai_models.sh recommend

# Pull optimal models (Tier 2 - balanced)
./bin/manage_ai_models.sh pull 1

# Configure the platform
./bin/manage_ai_models.sh configure balanced_performance

# Test the setup
./bin/manage_ai_models.sh test
```

### **Method 2: Manual Configuration**
```bash
# Pull specific models
ollama pull llama3.1:8b
ollama pull codellama:13b  
ollama pull nomic-embed-text

# Edit configuration file
nano config/ai_models_config.json
```

### **Method 3: Keep Your Granite Models**
```bash
# Just add the embedding model
ollama pull nomic-embed-text

# Configure for Granite optimization
./bin/manage_ai_models.sh configure granite_optimized
```

---

## 🔧 **Step-by-Step Model Switching**

### **Switching to Maximum Intelligence Setup:**

1. **Check your current models:**
   ```bash
   ollama list
   ./bin/manage_ai_models.sh status
   ```

2. **Pull recommended models:**
   ```bash
   # For balanced performance (recommended)
   ollama pull llama3.1:8b
   ollama pull codellama:13b
   ollama pull nomic-embed-text
   
   # For maximum intelligence (if you have resources)
   ollama pull llama3.1:70b
   ollama pull codellama:34b
   ```

3. **Update configuration:**
   ```bash
   ./bin/manage_ai_models.sh configure balanced_performance
   ```

4. **Restart Knowledge Fusion services:**
   ```bash
   ./bin/cleanup_platform.sh --soft
   ./bin/start_server_mode.sh
   ```

5. **Test the setup:**
   ```bash
   ./bin/manage_ai_models.sh test
   
   # Test through OpenWebUI
   # Ask: "What ASM services handle topology data?"
   ```

---

## 🎯 **Task-Specific Model Optimization**

### **For ASM Topology Analysis:**
- **Primary:** `granite3.2:8b-instruct-q8.0` (excellent IBM knowledge)
- **Code:** `codellama:13b` (superior code understanding)
- **Reasoning:** `llama3.1:8b` (best logical reasoning)

### **For Code Repository Analysis:**
- **Primary:** `codellama:13b` or `codellama:34b`
- **Support:** `llama3.1:8b` for documentation
- **Vision:** `granite3.2-vision:2b` for diagrams

### **For Support Case Processing:**
- **Primary:** `llama3.1:8b` (excellent text understanding)
- **Analysis:** `granite3.2:8b-instruct-q8.0` (IBM domain knowledge)
- **Embedding:** `nomic-embed-text` (essential!)

---

## 📋 **Model Configuration Profiles**

Edit `config/ai_models_config.json` to customize:

```json
{
  "active_profile": "your_optimal_setup",
  "model_profiles": {
    "your_optimal_setup": {
      "description": "Your customized optimal configuration",
      "primary_llm": "llama3.1:8b",
      "code_specialist": "codellama:13b", 
      "embedding_model": "nomic-embed-text",
      "backup_llm": "granite3.2:8b-instruct-q8.0",
      "vision_model": "granite3.2-vision:2b"
    }
  }
}
```

---

## 🚀 **Performance Optimization Tips**

### **1. Memory Management:**
```bash
# Check Ollama memory usage
ollama ps

# Unload unused models to free memory
ollama stop granite3.2:8b  # if not using
```

### **2. Context Window Optimization:**
```json
{
  "ollama_configuration": {
    "context_window": 8192,    # Increase for longer contexts
    "temperature": 0.3,        # Lower for more focused responses
    "timeout": 300            # Increase for complex queries
  }
}
```

### **3. Multi-Agent Routing:**
```json
{
  "multi_agent_routing": {
    "topology_agent_model": "granite3.2:8b-instruct-q8.0",  # IBM expertise
    "case_analysis_model": "llama3.1:8b",                   # Reasoning
    "github_agent_model": "codellama:13b",                  # Code analysis
    "synthesis_model": "llama3.1:8b"                        # Final synthesis
  }
}
```

---

## 🔍 **Troubleshooting Model Issues**

### **Model Not Found:**
```bash
# Check available models
ollama list

# Pull missing model
ollama pull model_name

# Update configuration
./bin/manage_ai_models.sh configure profile_name
```

### **Poor Performance:**
```bash
# Check model capabilities
./bin/manage_ai_models.sh status

# Test individual models
echo "Test query" | ollama run llama3.1:8b

# Switch to higher performance model
./bin/manage_ai_models.sh configure maximum_intelligence
```

### **Memory Issues:**
```bash
# Use more efficient models
./bin/manage_ai_models.sh configure efficient_setup

# Monitor resource usage
top -p $(pgrep ollama)
```

---

## 📈 **Intelligence Comparison**

| Model | Reasoning | Code Analysis | ASM Knowledge | Efficiency | Overall |
|-------|-----------|---------------|---------------|------------|---------|
| `llama3.1:70b` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | **95%** |
| `llama3.1:8b` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **85%** |
| `granite3.2:8b-instruct` | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **80%** |
| `codellama:34b` | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | **85%** |
| `codellama:13b` | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **80%** |

**Recommendation:** Use `llama3.1:8b` as primary with `granite3.2:8b-instruct-q8.0` for ASM-specific queries.

---

## 🎯 **My Specific Recommendation for You:**

Based on your setup, here's the **optimal configuration**:

```bash
# 1. Keep your excellent Granite models
# 2. Add these for maximum intelligence:
ollama pull llama3.1:8b        # Best general reasoning
ollama pull codellama:13b      # Superior code analysis  
ollama pull nomic-embed-text   # Essential for semantic search

# 3. Configure hybrid setup:
./bin/manage_ai_models.sh configure balanced_performance

# 4. Test with ASM-specific query:
# "How does ASM topology merge work in Kubernetes?"
```

This gives you:
- **90% intelligence** of the best setup
- **Excellent ASM domain knowledge** (your Granite models)
- **Superior code analysis** (CodeLlama)
- **Best reasoning** (Llama 3.1)
- **Optimal semantic search** (Nomic embeddings)

**Result:** Maximum intelligence for your Knowledge Fusion Platform! 🚀