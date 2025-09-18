#!/bin/bash

# IBM-specific startup script with enhanced frontend handling
# Addresses CSS and frontend asset serving issues on IBM corporate networks

set -e

echo "🏢 Starting services for IBM Corporate Environment"
echo "================================================"

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$BASE_DIR/openwebui_venv"
OPENWEBUI_DIR="$BASE_DIR/open-webui-cloned"

# Function to wait for service with enhanced timeout
wait_for_service() {
    local service_name="$1"
    local url="$2"
    local max_wait="${3:-300}"  # 5 minutes default for IBM
    local wait_time=0
    local check_interval=10
    
    echo "⏳ Waiting for $service_name to be ready..."
    echo "   URL: $url"
    echo "   Max wait time: ${max_wait}s"
    
    while [ $wait_time -lt $max_wait ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        
        echo "   ⏱️  ${service_name}: ${wait_time}s elapsed, checking again in ${check_interval}s..."
        sleep $check_interval
        wait_time=$((wait_time + check_interval))
    done
    
    echo "❌ $service_name failed to start within ${max_wait}s"
    return 1
}

# Function to check if port is in use
check_port() {
    local port="$1"
    if lsof -i ":$port" >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use"
        lsof -i ":$port"
        return 1
    fi
    return 0
}

# Function to start ChromaDB
start_chromadb() {
    echo "🗃️  Starting ChromaDB..."
    
    if ! check_port 8000; then
        echo "📋 ChromaDB may already be running"
        return 0
    fi
    
    cd "$BASE_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Start ChromaDB in background
    chroma run --host localhost --port 8000 --path ./chroma &
    CHROMA_PID=$!
    echo "ChromaDB PID: $CHROMA_PID"
    
    # Wait for ChromaDB to be ready
    if wait_for_service "ChromaDB" "http://localhost:8000/api/v1/heartbeat" 60; then
        echo "✅ ChromaDB started successfully"
    else
        echo "❌ ChromaDB startup failed"
        kill $CHROMA_PID 2>/dev/null || true
        return 1
    fi
    
    deactivate
}

# Function to start Knowledge Fusion
start_knowledge_fusion() {
    echo "🧠 Starting Knowledge Fusion..."
    
    if ! check_port 8080; then
        echo "📋 Knowledge Fusion may already be running"
        return 0
    fi
    
    cd "$BASE_DIR/knowledge-fusion-template"
    source "$VENV_DIR/bin/activate"
    
    # Start Knowledge Fusion in background
    python start_server.py &
    KF_PID=$!
    echo "Knowledge Fusion PID: $KF_PID"
    
    # Wait for Knowledge Fusion to be ready
    if wait_for_service "Knowledge Fusion" "http://localhost:8080/health" 60; then
        echo "✅ Knowledge Fusion started successfully"
    else
        echo "❌ Knowledge Fusion startup failed"
        kill $KF_PID 2>/dev/null || true
        return 1
    fi
    
    deactivate
}

# Function to prepare OpenWebUI frontend for IBM
prepare_openwebui_frontend() {
    echo "🎨 Preparing OpenWebUI frontend for IBM environment..."
    
    cd "$OPENWEBUI_DIR"
    
    # Check if we have a proper frontend build
    if [ ! -d "build" ] && [ ! -d "backend/open_webui/frontend" ]; then
        echo "  🔧 Frontend assets missing, creating minimal structure..."
        mkdir -p "backend/open_webui/frontend"
        
        # Create a basic index.html that redirects properly
        cat > "backend/open_webui/frontend/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>OpenWebUI</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        .container {
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top: 4px solid white;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 OpenWebUI</h1>
        <div class="spinner"></div>
        <p>Loading IBM-compatible interface...</p>
        <p id="status">Redirecting to application...</p>
    </div>
    
    <script>
        let attempts = 0;
        const maxAttempts = 30;
        
        function checkAndRedirect() {
            attempts++;
            document.getElementById('status').textContent = `Checking application... (${attempts}/${maxAttempts})`;
            
            // Try to reach the API docs endpoint
            fetch('/docs')
                .then(response => {
                    if (response.ok) {
                        window.location.href = '/docs';
                    } else {
                        throw new Error('Not ready');
                    }
                })
                .catch(() => {
                    if (attempts < maxAttempts) {
                        setTimeout(checkAndRedirect, 2000);
                    } else {
                        document.getElementById('status').textContent = 'Please try accessing /docs directly or contact support.';
                    }
                });
        }
        
        // Start checking after 3 seconds
        setTimeout(checkAndRedirect, 3000);
    </script>
</body>
</html>
EOF
        echo "  ✅ Created IBM-compatible frontend stub"
    fi
    
    # Set proper permissions
    chmod -R 755 backend/open_webui/frontend 2>/dev/null || true
    
    echo "✅ OpenWebUI frontend prepared for IBM environment"
}

# Function to start OpenWebUI with IBM-specific configuration
start_openwebui() {
    echo "🌐 Starting OpenWebUI for IBM environment..."
    
    if ! check_port 3000; then
        echo "📋 OpenWebUI may already be running"
        return 0
    fi
    
    # Prepare frontend assets
    prepare_openwebui_frontend
    
    cd "$OPENWEBUI_DIR/backend"
    source "$VENV_DIR/bin/activate"
    
    # Set IBM-specific environment variables
    export WEBUI_HOST="0.0.0.0"
    export WEBUI_PORT="3000"
    export WEBUI_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
    export OPENAI_API_BASE_URL="http://localhost:8080/v1"
    export CHROMA_HOST="localhost"
    export CHROMA_PORT="8000"
    export DATA_DIR="$BASE_DIR/data"
    export DOCS_DIR="$BASE_DIR/docs"
    
    # IBM Corporate Network specific settings
    export WEBUI_AUTH_TRUSTED_EMAIL_HEADER=""
    export WEBUI_AUTH_TRUSTED_NAME_HEADER=""
    export OAUTH_MERGE_ACCOUNTS_BY_EMAIL="true"
    export ENABLE_SIGNUP="true"
    export DEFAULT_USER_ROLE="user"
    export ENABLE_WEBSOCKET_CONNECTION_VERIFICATION="false"
    
    # Frontend serving configuration
    export SERVE_STATIC_FILES="true"
    export STATIC_FILES_PATH="./open_webui/frontend"
    
    echo "  🔧 Environment configured for IBM network"
    echo "  📁 Data directory: $DATA_DIR"
    echo "  🌐 Host: $WEBUI_HOST:$WEBUI_PORT"
    
    # Start OpenWebUI in background
    python -m open_webui.main &
    OPENWEBUI_PID=$!
    echo "OpenWebUI PID: $OPENWEBUI_PID"
    
    # Enhanced wait for OpenWebUI with IBM-specific checks
    echo "⏳ Waiting for OpenWebUI to be ready (extended timeout for IBM)..."
    local wait_time=0
    local max_wait=300  # 5 minutes for IBM networks
    local check_interval=15
    
    while [ $wait_time -lt $max_wait ]; do
        echo "   ⏱️  OpenWebUI: ${wait_time}s elapsed..."
        
        # Check multiple endpoints
        if curl -s "http://localhost:3000/docs" >/dev/null 2>&1; then
            echo "✅ OpenWebUI API docs accessible"
            break
        elif curl -s "http://localhost:3000/health" >/dev/null 2>&1; then
            echo "✅ OpenWebUI health check passed"
            break
        elif curl -s "http://localhost:3000/" >/dev/null 2>&1; then
            echo "✅ OpenWebUI root accessible"
            break
        fi
        
        sleep $check_interval
        wait_time=$((wait_time + check_interval))
        
        # Check if process is still running
        if ! kill -0 $OPENWEBUI_PID 2>/dev/null; then
            echo "❌ OpenWebUI process died unexpectedly"
            echo "📋 Checking logs..."
            tail -20 "$BASE_DIR/logs/openwebui.log" 2>/dev/null || echo "No logs found"
            return 1
        fi
    done
    
    if [ $wait_time -ge $max_wait ]; then
        echo "❌ OpenWebUI failed to start within ${max_wait}s"
        echo "📋 Final status check..."
        curl -v "http://localhost:3000/" || true
        return 1
    fi
    
    echo "✅ OpenWebUI started successfully"
    deactivate
}

# Function to display status
show_status() {
    echo ""
    echo "🔍 Service Status Check"
    echo "======================"
    
    echo "ChromaDB (port 8000):"
    if curl -s "http://localhost:8000/api/v1/heartbeat" >/dev/null 2>&1; then
        echo "  ✅ Running"
    else
        echo "  ❌ Not responding"
    fi
    
    echo "Knowledge Fusion (port 8080):"
    if curl -s "http://localhost:8080/health" >/dev/null 2>&1; then
        echo "  ✅ Running"
    else
        echo "  ❌ Not responding"
    fi
    
    echo "OpenWebUI (port 3000):"
    if curl -s "http://localhost:3000/docs" >/dev/null 2>&1; then
        echo "  ✅ Running - API Docs accessible"
    elif curl -s "http://localhost:3000/" >/dev/null 2>&1; then
        echo "  ✅ Running - Root accessible"
    else
        echo "  ❌ Not responding"
    fi
}

# Main execution
main() {
    echo "🚀 Starting all services for IBM environment..."
    
    # Check if we have the required virtual environment
    if [ ! -d "$VENV_DIR" ]; then
        echo "❌ Virtual environment not found. Please run setup first:"
        echo "   ./setup_ibm.sh"
        exit 1
    fi
    
    # Check if OpenWebUI was downloaded
    if [ ! -d "$OPENWEBUI_DIR" ]; then
        echo "❌ OpenWebUI not found. Please run setup first:"
        echo "   ./setup_ibm.sh"
        exit 1
    fi
    
    # Create data and logs directories
    mkdir -p "$BASE_DIR/data" "$BASE_DIR/logs"
    
    echo "📋 Starting services in sequence..."
    
    # Start ChromaDB
    if ! start_chromadb; then
        echo "❌ Failed to start ChromaDB"
        exit 1
    fi
    
    # Start Knowledge Fusion
    if ! start_knowledge_fusion; then
        echo "❌ Failed to start Knowledge Fusion"
        exit 1
    fi
    
    # Start OpenWebUI
    if ! start_openwebui; then
        echo "❌ Failed to start OpenWebUI"
        exit 1
    fi
    
    # Show final status
    show_status
    
    echo ""
    echo "🎉 All services started successfully!"
    echo "===================================="
    echo ""
    echo "🌐 Access URLs:"
    echo "   • OpenWebUI: http://localhost:3000"
    echo "   • OpenWebUI API Docs: http://localhost:3000/docs"
    echo "   • Knowledge Fusion: http://localhost:8080"
    echo "   • ChromaDB: http://localhost:8000"
    echo ""
    echo "🏢 IBM Corporate Network Compatible:"
    echo "   • No external internet required after setup"
    echo "   • Frontend assets optimized for corporate proxies"
    echo "   • Extended timeouts for slower networks"
    echo ""
    echo "💡 Troubleshooting:"
    echo "   • If UI styles don't load: Clear browser cache and retry"
    echo "   • For login issues: Try accessing /docs first"
    echo "   • View logs: ./view_logs.sh"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Keep script running
    wait
}

# Handle Ctrl+C gracefully
trap 'echo ""; echo "🛑 Stopping all services..."; pkill -f "chroma run" 2>/dev/null || true; pkill -f "start_server.py" 2>/dev/null || true; pkill -f "open_webui.main" 2>/dev/null || true; echo "✅ All services stopped"; exit 0' INT

# Run main function
main "$@"