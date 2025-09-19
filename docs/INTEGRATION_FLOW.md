# Knowledge Fusion Integration Flow

> **From Setup to Running to Integration**: A step-by-step guide for getting your Knowledge Fusion platform operational and integrated with OpenWebUI.

## 🔄 Complete Integration Flow

```
Setup → Running → Integration → Testing → Production
  │        │         │          │         │
  ▼        ▼         ▼          ▼         ▼
 🔧      🚀        🔗        ✅       🏭
```

## Phase 1: Setup 📦

### Prerequisites Check
```bash
# Verify you have these ready:
✅ OpenWebUI installed and accessible
✅ Python 3.8+ with virtual environment capability
✅ Git for repository management
✅ Network access (proxy support included for corporate networks)
```

### Platform Setup
```bash
# For IBM corporate networks
./setup_ibm.sh

# For standard environments
./setup.sh
```

**What this does:**
- Creates isolated Python virtual environment
- Installs Knowledge Fusion dependencies
- Sets up directory structure
- Configures proxy settings (if needed)
- Prepares the Knowledge Fusion template

**Expected output:**
```
✅ Virtual environment created: openwebui_venv
✅ Dependencies installed successfully
✅ Knowledge Fusion template prepared
✅ Corporate proxy configured (if applicable)
```

## Phase 2: Running 🚀

### Start Knowledge Fusion Services

**Server Mode (Recommended):**
```bash
./bin/start_server_mode.sh
```

**Container Mode:**
```bash
./start_docker_mode.sh
```

### Service Startup Sequence

1. **Core Backend** (Port 8001)
   ```
   🔄 Starting Core Backend...
   ✅ Core Backend is ready (port 8001)
   ```

2. **Knowledge Fusion Backend** (Port 8002)
   ```
   🔄 Starting Knowledge Fusion Backend...
   ✅ Knowledge Fusion Backend is ready (port 8002)
   ```

3. **Knowledge Fusion Gateway** (Port 9000)
   ```
   🔄 Starting Knowledge Fusion Gateway...
   ✅ Knowledge Fusion Gateway is ready (port 9000)
   ```

4. **OpenWebUI Check** (Port 8080)
   ```
   🔍 Checking OpenWebUI Status...
   ✅ OpenWebUI is already running on port 8080
   ```

### Verify All Services

```bash
./status_ibm.sh
```

**Expected output:**
```
✅ Knowledge Fusion Backend (8002) - Running
✅ CoreBackend (8001) - Running  
✅ Knowledge Fusion Gateway (9000) - Running
✅ OpenWebUI (8080) - External Running
```

## Phase 3: Integration 🔗

### Step 1: Get the Pipe Function Code

```bash
cat knowledge_fusion_function.py
```

### Step 2: Upload to OpenWebUI

1. **Access OpenWebUI Admin Panel**
   - Go to http://localhost:8080 (or your OpenWebUI URL)
   - Log in as admin
   - Navigate to **Admin Panel** → **Functions**

2. **Add New Function**
   - Click the **"+"** button to add new function
   - Select **"Create New Function"**

3. **Upload the Code**
   - Paste the complete code from `knowledge_fusion_function.py`
   - Save the function

4. **Enable the Function**
   - Toggle the function to **"Enabled"**
   - Verify it appears in your functions list

### Step 3: Configure Function Settings

In the function's **Valves** configuration:

```python
GATEWAY_URL: "http://localhost:9000"    # Knowledge Fusion Gateway
TIMEOUT: 30                             # Request timeout in seconds  
ENABLED: True                           # Enable/disable the function
```

## Phase 4: Testing ✅

### Test the Integration

1. **Start a New Chat**
   - Go to OpenWebUI chat interface
   - Start a new conversation

2. **Test Query**
   ```
   How do I debug memory leaks in microservices?
   ```

3. **Watch the Flow**
   ```
   User Query → OpenWebUI → Pipe Function → Gateway (9000) 
             → Knowledge Fusion Backend (8002) → CoreBackend (8001)
             → Response → User
   ```

4. **Expected Behavior**
   - You should see status messages: "🔍 Routing query to Knowledge Fusion Gateway..."
   - Response should include intelligent synthesis from multiple sources
   - Graceful fallback if any service is unavailable

### Monitor Logs

```bash
# Real-time monitoring
./view_logs.sh

# Or monitor specific logs
tail -f logs/knowledge_fusion.log
tail -f logs/openwebui.log
```

## Phase 5: Production 🏭

### Data Organization

```
data/
├── cases/                  # Your case studies and examples
│   ├── microservices/      # Microservices patterns and issues
│   ├── debugging/          # Debugging guides and solutions
│   └── architecture/       # Architecture decisions and patterns
├── chromadb/              # Vector database storage
└── functions/             # Custom function definitions
```

### Adding Knowledge Sources

**Git Repositories:**
```bash
# Add repository for knowledge extraction
git submodule add <repo-url> data/repos/<repo-name>

# Update knowledge base
python knowledge_fusion_function.py --index data/repos/<repo-name>
```

**Case Studies:**
```bash
# Add case studies to data/cases/
mkdir -p data/cases/microservices
echo "Case study content..." > data/cases/microservices/circuit_breaker_pattern.md
```

### Advanced Configuration

**Environment Variables:**
```bash
export KNOWLEDGE_FUSION_GATEWAY_PORT=9000
export KNOWLEDGE_FUSION_BACKEND_PORT=8002
export CORE_BACKEND_PORT=8001
```

**Custom Routing:**
- Modify `knowledge_fusion_gateway.py` for custom routing logic
- Extend `knowledge-fusion-template/` for additional backends
- Customize `knowledge_fusion_function.py` for specialized integration

## 🎯 Success Criteria

After completing this flow, you should have:

✅ **All services running** on their designated ports  
✅ **Pipe function uploaded** and enabled in OpenWebUI  
✅ **Test queries working** with intelligent routing  
✅ **Logs accessible** for monitoring and debugging  
✅ **Data structure organized** for knowledge sources  

## 🛠️ Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check port conflicts
lsof -i :8001,8002,9000

# Restart individual service
pkill -f "knowledge_fusion"
./bin/start_server_mode.sh
```

**OpenWebUI not detected:**
```bash
# Check if OpenWebUI is running
curl http://localhost:8080/health

# Start OpenWebUI if needed
open-webui serve --port 8080
```

**Function upload fails:**
```bash
# Verify function format
python -c "import knowledge_fusion_function; print('Function format OK')"

# Check OpenWebUI admin access
# Ensure you're logged in as admin user
```

### Log Analysis

**Debug connection issues:**
```bash
# Test the complete chain
curl -X POST http://localhost:9000/knowledge-fusion/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test connection"}'
```

**Monitor real-time activity:**
```bash
# Web-based log viewer
python web_logs.py
# Access at http://localhost:8005
```

## 📚 Next Steps

1. **Customize for your domain** - Add your specific knowledge sources
2. **Scale the architecture** - Add more backends or specialized routing
3. **Integrate with enterprise systems** - Connect to your existing knowledge bases
4. **Monitor and optimize** - Use logs to improve performance and accuracy

---

**Ready for advanced features?** Check out the [Architecture Documentation](KNOWLEDGE_FUSION_ARCHITECTURE.md) for deep customization options.