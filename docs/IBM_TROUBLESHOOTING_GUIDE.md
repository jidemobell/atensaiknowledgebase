# IBM Corporate Network Troubleshooting Guide

## Overview
This guide addresses common issues when deploying the Knowledge Topology system on IBM corporate networks, specifically focusing on CSS styling problems and missing dependencies.

## Quick Diagnosis

### 1. CSS/Styling Issues
If the OpenWebUI interface loads but styles are not applied:

```bash
# Check if frontend assets are properly served
curl -I http://localhost:3000/
curl -I http://localhost:3000/docs

# Check browser developer tools for:
# - 404 errors on CSS/JS files
# - CORS errors
# - Network timeouts
```

### 2. Missing Dependencies
Check for missing Python packages:

```bash
# Activate virtual environment
source openwebui_venv/bin/activate

# Run dependency check
python -c "
import sys
packages = ['itsdangerous', 'cryptography', 'uvicorn', 'fastapi', 'tiktoken']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}: OK')
    except ImportError:
        print(f'❌ {pkg}: MISSING')
"
```

## IBM-Specific Solutions

### Setup for IBM Corporate Network

1. **Initial Setup**:
```bash
# Use IBM-specific setup script
./setup_ibm.sh

# This script:
# - Downloads OpenWebUI without git submodules
# - Installs dependencies with corporate proxy support
# - Configures frontend assets for IBM environment
```

2. **Start Services**:
```bash
# Use IBM-specific startup
./start_ibm.sh

# This provides:
# - Extended timeouts for corporate networks
# - Enhanced frontend asset serving
# - IBM-compatible environment variables
```

### Manual Dependency Installation

If automated installation fails:

```bash
# Activate virtual environment
source openwebui_venv/bin/activate

# Install with corporate proxy support
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
    itsdangerous>=2.0.0 \
    cryptography>=3.4.8 \
    uvicorn[standard] \
    fastapi>=0.104.0 \
    tiktoken>=0.7.0 \
    python-multipart \
    jinja2 \
    aiofiles

# Verify installation
python -c "import itsdangerous, cryptography, uvicorn, fastapi, tiktoken; print('All packages imported successfully')"
```

### Frontend Asset Issues

If OpenWebUI loads but CSS is missing:

1. **Check frontend structure**:
```bash
ls -la open-webui-cloned/backend/open_webui/frontend/
```

2. **Rebuild frontend assets**:
```bash
cd open-webui-cloned
# If npm is available:
npm install
npm run build

# If not available, use our IBM-compatible frontend stub:
mkdir -p backend/open_webui/frontend
# (The start_ibm.sh script creates this automatically)
```

3. **Verify static file serving**:
```bash
# Check environment variables
echo $SERVE_STATIC_FILES
echo $STATIC_FILES_PATH

# Should be set to:
export SERVE_STATIC_FILES="true"
export STATIC_FILES_PATH="./open_webui/frontend"
```

## Corporate Network Configuration

### Proxy Settings
If your IBM network requires proxy configuration:

```bash
# Set proxy environment variables
export HTTP_PROXY="http://proxy.company.com:8080"
export HTTPS_PROXY="http://proxy.company.com:8080"
export NO_PROXY="localhost,127.0.0.1,*.local"

# Configure git for future updates
git config --global http.proxy "$HTTP_PROXY"
git config --global https.proxy "$HTTPS_PROXY"
```

### SSL Certificate Issues
For corporate SSL interception:

```bash
# Download packages with relaxed SSL verification
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org <package_name>

# Or if necessary (less secure):
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host index-url pypi.org <package_name>
```

## Troubleshooting Specific Issues

### Issue: "No module named 'itsdangerous'"

**Solution**:
```bash
source openwebui_venv/bin/activate
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org itsdangerous>=2.0.0
```

### Issue: OpenWebUI starts but UI has no styling

**Symptoms**: 
- Login page loads but looks like plain HTML
- Buttons and inputs have no styling
- Layout is broken

**Solution**:
```bash
# 1. Use IBM-specific startup script
./start_ibm.sh

# 2. If still broken, check browser developer tools:
# - Open http://localhost:3000 in browser
# - Press F12 to open developer tools
# - Check Console tab for errors
# - Check Network tab for failed requests

# 3. Manual frontend fix:
cd open-webui-cloned/backend/open_webui
# Ensure frontend directory exists and is readable
ls -la frontend/
chmod -R 755 frontend/
```

### Issue: Services fail to start on IBM network

**Symptoms**:
- Timeout errors during startup
- Connection refused errors
- Services start but become unresponsive

**Solution**:
```bash
# 1. Use extended timeouts
./start_ibm.sh  # Has 5-minute timeouts for IBM networks

# 2. Check port availability
lsof -i :3000  # OpenWebUI
lsof -i :8080  # Knowledge Fusion  
lsof -i :8000  # ChromaDB

# 3. Start services individually for debugging
source openwebui_venv/bin/activate

# Start ChromaDB
chroma run --host localhost --port 8000 --path ./chroma &

# Start Knowledge Fusion
cd knowledge-fusion-template
python start_server.py &
cd ..

# Start OpenWebUI
cd open-webui-cloned/backend
export WEBUI_HOST="0.0.0.0"
export WEBUI_PORT="3000"
python -m open_webui.main &
```

### Issue: "Permission denied" during setup

**Solution**:
```bash
# Ensure scripts are executable
chmod +x setup_ibm.sh start_ibm.sh

# Check directory permissions
ls -la 
chmod 755 .

# If using shared directory, check mounting permissions
```

## IBM Environment Validation

Run this validation script to ensure your IBM environment is properly configured:

```bash
#!/bin/bash
echo "🏢 IBM Environment Validation"
echo "=========================="

# Check Python environment
python3 --version
which python3

# Check virtual environment
if [ -d "openwebui_venv" ]; then
    echo "✅ Virtual environment exists"
    source openwebui_venv/bin/activate
    python --version
    pip list | grep -E "(itsdangerous|cryptography|uvicorn|fastapi|tiktoken)"
    deactivate
else
    echo "❌ Virtual environment not found"
fi

# Check OpenWebUI installation
if [ -d "open-webui-cloned" ]; then
    echo "✅ OpenWebUI directory exists"
    ls -la open-webui-cloned/backend/open_webui/frontend/ 2>/dev/null || echo "⚠️  Frontend directory missing"
else
    echo "❌ OpenWebUI not found"
fi

# Check network connectivity
echo "🌐 Network connectivity:"
curl -I https://pypi.org 2>/dev/null && echo "✅ PyPI accessible" || echo "❌ PyPI not accessible"

# Check ports
echo "🔌 Port availability:"
for port in 3000 8080 8000; do
    if lsof -i ":$port" >/dev/null 2>&1; then
        echo "⚠️  Port $port in use"
    else
        echo "✅ Port $port available"
    fi
done

echo "=========================="
echo "Validation complete"
```

## Getting Help

### Log Files
Check these log files for detailed error information:

```bash
# View real-time logs
tail -f logs/openwebui.log
tail -f logs/knowledge_fusion.log

# Use log viewing script
./view_logs.sh
```

### Debug Mode
Run services in debug mode for more information:

```bash
# OpenWebUI debug mode
export WEBUI_DEBUG="true"
export LOG_LEVEL="DEBUG"

# Then start normally
./start_ibm.sh
```

### Support Information
When reporting issues, include:

1. **Environment Details**:
   - Python version: `python3 --version`
   - Operating system: `uname -a`
   - Virtual environment: `source openwebui_venv/bin/activate && pip list`

2. **Error Logs**:
   - OpenWebUI logs: `cat logs/openwebui.log`
   - Browser console errors (F12 → Console)
   - Network tab errors (F12 → Network)

3. **Service Status**:
   - Process list: `ps aux | grep -E "(uvicorn|chroma|knowledge_fusion)"`
   - Port status: `lsof -i :3000,8080,8000`

4. **Configuration**:
   - Environment variables: `env | grep -E "(WEBUI|CHROMA|OPENAI)"`
   - Directory structure: `ls -la open-webui-cloned/backend/open_webui/`

## Quick Recovery

If everything fails, use this complete reset procedure:

```bash
# 1. Stop all services
pkill -f "uvicorn\|chroma\|knowledge_fusion" 2>/dev/null || true

# 2. Clean up
rm -rf openwebui_venv open-webui-cloned

# 3. Fresh IBM setup
./setup_ibm.sh

# 4. Start with IBM script
./start_ibm.sh
```

This should resolve most IBM corporate network issues with the Knowledge Topology system.