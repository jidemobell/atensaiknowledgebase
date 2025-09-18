#!/bin/bash

# Comprehensive system status display for IBM troubleshooting

echo "🏢 IBM Knowledge Topology System Status"
echo "======================================="
echo ""

# Check basic environment
echo "📋 Environment Information:"
echo "  OS: $(uname -s) $(uname -r)"
echo "  Python: $(python3 --version 2>&1)"
echo "  Current Directory: $(pwd)"
echo "  Date: $(date)"
echo ""

# Check virtual environment
echo "🐍 Python Virtual Environment:"
if [ -d "openwebui_venv" ]; then
    echo "  ✅ Virtual environment exists"
    echo "  📁 Location: $(realpath openwebui_venv)"
    
    # Activate and check packages
    source openwebui_venv/bin/activate
    echo "  🔍 Python executable: $(which python)"
    echo "  📦 Pip version: $(pip --version)"
    
    echo "  🧩 Critical packages:"
    python -c "
import sys
packages = [
    ('itsdangerous', 'Web security'),
    ('cryptography', 'Encryption'),
    ('uvicorn', 'ASGI server'),
    ('fastapi', 'Web framework'),
    ('tiktoken', 'Token processing'),
    ('jinja2', 'Template engine'),
    ('multipart', 'File uploads'),
    ('aiofiles', 'Async file handling')
]

for pkg, desc in packages:
    try:
        if pkg == 'multipart':
            import multipart
        else:
            __import__(pkg)
        print(f'    ✅ {pkg:<15} - {desc}')
    except ImportError:
        print(f'    ❌ {pkg:<15} - {desc} (MISSING)')
"
    deactivate
else
    echo "  ❌ Virtual environment not found"
    echo "  💡 Run: ./setup_ibm.sh"
fi
echo ""

# Check OpenWebUI installation
echo "🌐 OpenWebUI Installation:"
if [ -d "open-webui-cloned" ]; then
    echo "  ✅ OpenWebUI directory exists"
    echo "  📁 Location: $(realpath open-webui-cloned)"
    
    if [ -d "open-webui-cloned/backend" ]; then
        echo "  ✅ Backend directory found"
    else
        echo "  ❌ Backend directory missing"
    fi
    
    if [ -d "open-webui-cloned/backend/open_webui/frontend" ]; then
        echo "  ✅ Frontend directory found"
        echo "  📁 Frontend files:"
        ls -la "open-webui-cloned/backend/open_webui/frontend/" | head -5
    else
        echo "  ⚠️  Frontend directory missing (will be created on startup)"
    fi
    
    # Check for requirements.txt
    if [ -f "open-webui-cloned/backend/requirements.txt" ]; then
        echo "  ✅ Requirements file found"
    else
        echo "  ❌ Requirements file missing"
    fi
else
    echo "  ❌ OpenWebUI not found"
    echo "  💡 Run: ./setup_ibm.sh"
fi
echo ""

# Check service ports
echo "🔌 Service Port Status:"
services=(
    "3000:OpenWebUI"
    "8080:Knowledge Fusion"
    "8000:ChromaDB"
)

for service in "${services[@]}"; do
    port="${service%:*}"
    name="${service#*:}"
    
    if lsof -i ":$port" >/dev/null 2>&1; then
        echo "  🟢 Port $port ($name): IN USE"
        lsof -i ":$port" | tail -1 | awk '{print "      Process: " $2 " (" $1 ")"}'
    else
        echo "  ⚪ Port $port ($name): Available"
    fi
done
echo ""

# Check service health
echo "🏥 Service Health Check:"
services=(
    "http://localhost:3000:OpenWebUI (Root)"
    "http://localhost:3000/docs:OpenWebUI (API Docs)"
    "http://localhost:3000/health:OpenWebUI (Health)"
    "http://localhost:8080/health:Knowledge Fusion"
    "http://localhost:8000/api/v1/heartbeat:ChromaDB"
)

for service in "${services[@]}"; do
    url="${service%:*}"
    name="${service#*:}"
    
    if curl -s --max-time 5 "$url" >/dev/null 2>&1; then
        echo "  ✅ $name: Responding"
    else
        echo "  ❌ $name: Not responding"
    fi
done
echo ""

# Check data directories
echo "📁 Data Directories:"
directories=(
    "data:Application data"
    "logs:Log files"
    "chroma:ChromaDB data"
    "knowledge-fusion-template:KF integration"
)

for dir_info in "${directories[@]}"; do
    dir="${dir_info%:*}"
    desc="${dir_info#*:}"
    
    if [ -d "$dir" ]; then
        size=$(du -sh "$dir" 2>/dev/null | cut -f1)
        echo "  ✅ $dir ($desc): $size"
    else
        echo "  ❌ $dir ($desc): Missing"
    fi
done
echo ""

# Check log files
echo "📋 Recent Log Activity:"
if [ -f "logs/openwebui.log" ]; then
    echo "  📄 OpenWebUI log (last 3 lines):"
    tail -3 "logs/openwebui.log" 2>/dev/null | sed 's/^/    /'
else
    echo "  ❌ OpenWebUI log not found"
fi

if [ -f "logs/knowledge_fusion.log" ]; then
    echo "  📄 Knowledge Fusion log (last 3 lines):"
    tail -3 "logs/knowledge_fusion.log" 2>/dev/null | sed 's/^/    /'
else
    echo "  ❌ Knowledge Fusion log not found"
fi
echo ""

# Check network connectivity
echo "🌐 Network Connectivity:"
if curl -s --max-time 5 "https://pypi.org" >/dev/null 2>&1; then
    echo "  ✅ PyPI (Python packages): Accessible"
else
    echo "  ❌ PyPI (Python packages): Not accessible"
    echo "      💡 This may indicate corporate proxy issues"
fi

if curl -s --max-time 5 "https://github.com" >/dev/null 2>&1; then
    echo "  ✅ GitHub: Accessible"
else
    echo "  ❌ GitHub: Not accessible"
    echo "      💡 This may indicate corporate firewall restrictions"
fi
echo ""

# Check proxy settings
echo "🔗 Proxy Configuration:"
if [ -n "$HTTP_PROXY" ] || [ -n "$HTTPS_PROXY" ]; then
    echo "  🔧 Proxy configured:"
    [ -n "$HTTP_PROXY" ] && echo "    HTTP_PROXY: $HTTP_PROXY"
    [ -n "$HTTPS_PROXY" ] && echo "    HTTPS_PROXY: $HTTPS_PROXY"
    [ -n "$NO_PROXY" ] && echo "    NO_PROXY: $NO_PROXY"
else
    echo "  ⚪ No proxy configured"
fi
echo ""

# Provide recommendations
echo "💡 Recommendations:"

# Check if services are running
running_services=0
for port in 3000 8080 8000; do
    if lsof -i ":$port" >/dev/null 2>&1; then
        ((running_services++))
    fi
done

if [ $running_services -eq 0 ]; then
    echo "  🚀 No services running. To start:"
    echo "     ./start_ibm.sh"
elif [ $running_services -lt 3 ]; then
    echo "  ⚠️  Some services not running. Check logs and restart:"
    echo "     ./start_ibm.sh"
else
    echo "  ✅ All services appear to be running"
    echo "  🌐 Access OpenWebUI at: http://localhost:3000"
fi

# Check for missing dependencies
if [ -d "openwebui_venv" ]; then
    source openwebui_venv/bin/activate
    missing_packages=$(python -c "
packages = ['itsdangerous', 'cryptography', 'uvicorn', 'fastapi', 'tiktoken']
missing = []
for pkg in packages:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)
if missing:
    print(' '.join(missing))
" 2>/dev/null)
    deactivate
    
    if [ -n "$missing_packages" ]; then
        echo "  🔧 Missing packages detected: $missing_packages"
        echo "     Run: source openwebui_venv/bin/activate"
        echo "     pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org $missing_packages"
    fi
fi

# Check if setup is needed
if [ ! -d "openwebui_venv" ] || [ ! -d "open-webui-cloned" ]; then
    echo "  🔧 Setup required:"
    echo "     ./setup_ibm.sh"
fi

echo ""
echo "📚 For detailed troubleshooting:"
echo "   View: docs/IBM_TROUBLESHOOTING_GUIDE.md"
echo "   Logs: ./view_logs.sh"
echo ""
echo "🏢 IBM-specific startup: ./start_ibm.sh"
echo "================================================="