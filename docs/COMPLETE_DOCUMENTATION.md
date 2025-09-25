# 📚 Complete Knowledge Fusion Platform Documentation

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+ 
- Git with SSH access to GitHub
- 8001, 8002, 9000 ports available

### One-Command Setup
```bash
# Clone and start everything
git clone git@github.com:jidemobell/atensaiknowledgebase.git
cd atensaiknowledgebase
./bin/setup_environments.sh  # Creates virtual environments
./bin/start_server_mode.sh   # Starts all services
```

## 🔧 Script Reference

### Core Scripts

#### `./bin/start_server_mode.sh`
**Primary platform launcher** - starts all services in proper order
```bash
./bin/start_server_mode.sh           # Start full platform
./bin/start_server_mode.sh --help    # Show options
```

#### `./bin/run_corebackend_isolated.sh`
**Core Backend only** - isolated environment, no ML dependencies
```bash
./bin/run_corebackend_isolated.sh    # Start Core Backend only
# API available at http://localhost:8001
# Documentation at http://localhost:8001/docs
```

#### `./bin/view_logs.sh`
**Log management and viewing** - comprehensive log analysis
```bash
./bin/view_logs.sh                   # Show recent logs from all services
./bin/view_logs.sh --help            # Show all options
./bin/view_logs.sh --size            # Show log file sizes
./bin/view_logs.sh --service core    # Show only Core Backend logs
./bin/view_logs.sh --service fusion  # Show only Knowledge Fusion logs
./bin/view_logs.sh --follow          # Follow logs in real-time
./bin/view_logs.sh --clear           # Clear all log files
./bin/view_logs.sh --error           # Show only error entries
```

#### `./bin/setup_github_token.sh`
**GitHub authentication setup** - handles both tokens and SSH
```bash
./bin/setup_github_token.sh          # Interactive setup
# - Prompts for GitHub token OR
# - Sets up SSH authentication if tokens unavailable
# - Tests authentication
# - Provides setup instructions
```

#### `./bin/test_core_backend.sh`
**Core Backend diagnostics** - comprehensive API testing
```bash
./bin/test_core_backend.sh           # Full diagnostic suite
./bin/test_core_backend.sh --quick   # Basic connectivity test
./bin/test_core_backend.sh --api     # API endpoint testing
./bin/test_core_backend.sh --deps    # Dependency verification
```

#### `./bin/setup_environments.sh`
**Virtual environment management** - creates isolated environments
```bash
./bin/setup_environments.sh          # Create both environments
# Creates: corebackend_venv/ (lightweight)
# Checks: openwebui_venv/ (ML dependencies)
```

### Specialized Scripts

#### `./bin/manage_hybrid_sources.sh`
**Multi-source knowledge management** - beyond GitHub
```bash
./bin/manage_hybrid_sources.sh --help        # Show all options
./bin/manage_hybrid_sources.sh --web URL     # Add web source
./bin/manage_hybrid_sources.sh --api URL     # Add API source
./bin/manage_hybrid_sources.sh --doc PATH    # Add document source
./bin/manage_hybrid_sources.sh --list        # List all sources
```

#### `./bin/cleanup_platform.sh`
**Platform cleanup and reset**
```bash
./bin/cleanup_platform.sh --soft     # Stop services only
./bin/cleanup_platform.sh --hard     # Stop + clear data
./bin/cleanup_platform.sh --reset    # Full reset to clean state
```

## 🏗️ Architecture Deep Dive

### Service Layout
```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐
│   OpenWebUI     │───▶│ Knowledge Fusion │───▶│ Core Backend   │
│  (External)     │    │   Gateway        │    │  (Isolated)    │
│   Port 8080     │    │   Port 9000      │    │   Port 8001    │
└─────────────────┘    └──────────────────┘    └────────────────┘
                                │                        │
                                ▼                        ▼
                         ┌──────────────┐    ┌─────────────────┐
                         │ Knowledge    │    │   Data Layer    │
                         │  Fusion      │    │  • ChromaDB     │
                         │ Backend      │    │  • File Store   │
                         │ Port 8002    │    │  • Vector DB    │
                         └──────────────┘    └─────────────────┘
```

### Virtual Environment Strategy
- **`corebackend_venv/`**: Lightweight, FastAPI only, no ML conflicts
- **`openwebui_venv/`**: Full ML stack, transformers, ChromaDB

### Data Flow
1. **OpenWebUI** → Query via function interface
2. **Gateway (9000)** → Routes and manages requests  
3. **Knowledge Fusion (8002)** → Processes with ML models
4. **Core Backend (8001)** → Provides enterprise logic
5. **Data Layer** → ChromaDB, vector storage, file systems

## 🔐 Authentication Options

### Option 1: SSH Authentication (Recommended for Enterprise)
```bash
./bin/setup_github_token.sh    # Choose SSH option
# - Generates SSH key if needed
# - Shows public key for GitHub
# - Tests connection
# - Works without personal tokens
```

### Option 2: Personal Access Token
```bash
export GITHUB_TOKEN="ghp_your_token_here"
./bin/setup_github_token.sh    # Will detect and use token
```

## 🚨 Troubleshooting

### Common Issues

#### "Port already in use"
```bash
./bin/cleanup_platform.sh --soft  # Stop all services
lsof -i :8001,8002,9000           # Check what's using ports
```

#### "Failed to load API definition"
```bash
./bin/run_corebackend_isolated.sh  # Start isolated Core Backend
curl http://localhost:8001/health   # Test directly
```

#### "ML dependencies conflict"
This is solved by isolated environments:
- Core Backend runs in `corebackend_venv/` (no ML)
- Knowledge Fusion runs in `openwebui_venv/` (with ML)

#### GitHub authentication fails
```bash
./bin/setup_github_token.sh        # Interactive setup
ssh -T git@github.com              # Test SSH directly
```

### Log Analysis
```bash
./bin/view_logs.sh --error          # Show only errors
./bin/view_logs.sh --service core   # Core Backend logs
./bin/view_logs.sh --follow         # Real-time monitoring
```

### Complete Reset
```bash
./bin/cleanup_platform.sh --reset   # Nuclear option
./bin/setup_environments.sh         # Recreate environments
./bin/start_server_mode.sh          # Fresh start
```

## 📊 Service Health Checks

### Manual Testing
```bash
# Core Backend
curl http://localhost:8001/health

# Knowledge Fusion Backend  
curl http://localhost:8002/health

# Knowledge Fusion Gateway
curl http://localhost:9000/health

# OpenWebUI (external)
curl http://localhost:8080/health
```

### Automated Testing
```bash
./bin/test_core_backend.sh          # Comprehensive test suite
```

## 🔄 Development Workflow

### 1. Start Development Environment
```bash
./bin/run_corebackend_isolated.sh   # Core Backend only
# Develop and test API changes
# API docs: http://localhost:8001/docs
```

### 2. Test Changes
```bash
./bin/test_core_backend.sh --api    # Test API endpoints
curl -X POST http://localhost:8001/diagnose \
  -H "Content-Type: application/json" \
  -d '{"issue_description": "test"}'
```

### 3. Full Platform Testing
```bash
./bin/start_server_mode.sh          # Start everything
# Test integration with OpenWebUI
```

### 4. Production Deployment
```bash
./bin/cleanup_platform.sh --soft    # Clean restart
./bin/start_server_mode.sh          # Production start
./bin/view_logs.sh --follow         # Monitor
```

## 📁 Project Structure
```
TOPOLOGYKNOWLEDGE/
├── bin/                    # All executable scripts
│   ├── start_server_mode.sh           # Main launcher
│   ├── run_corebackend_isolated.sh    # Core Backend only
│   ├── view_logs.sh                   # Log management
│   ├── setup_github_token.sh          # Auth setup
│   └── test_core_backend.sh           # Diagnostics
├── corebackend/           # Core Backend implementation
├── knowledge-fusion-template/         # Knowledge Fusion engine
├── docs/                  # Documentation
├── data/                  # Data storage
├── logs/                  # Service logs
├── corebackend_venv/      # Isolated Core Backend environment
└── openwebui_venv/        # Knowledge Fusion environment
```

This documentation provides comprehensive coverage of all scripts, options, and workflows. Each section includes practical examples and troubleshooting guidance.