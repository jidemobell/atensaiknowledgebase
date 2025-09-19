# Knowledge Fusion Platform - Scripts & Executables

This directory contains all executable scripts for the IBM Knowledge Fusion Platform, organized for easy access and maintenance.

## 🚀 Main Scripts

### Core Platform Management
- **[start_server_mode.sh](start_server_mode.sh)** - Main platform launcher
  - Starts all Knowledge Fusion services (Gateway, Backend, Core)
  - Checks dependencies and manages service lifecycle
  - **Usage**: `./bin/start_server_mode.sh`

### Knowledge Source Management
- **[add_knowledge_source.sh](add_knowledge_source.sh)** - GitHub repository management
  - Add, remove, and manage GitHub repositories as knowledge sources
  - Handles cloning, indexing, and integration with ChromaDB
  - **Usage**: `./bin/add_knowledge_source.sh`

- **[manage_hybrid_sources.sh](manage_hybrid_sources.sh)** - Multi-source knowledge management
  - Manages web content, APIs, databases, and document collections
  - Automated sync and metadata tracking
  - **Usage**: `./bin/manage_hybrid_sources.sh`

### Monitoring & Operations
- **[view_logs.sh](view_logs.sh)** - Advanced monitoring system
  - Real-time log viewing with filtering and analysis
  - Service health checks and performance metrics
  - **Usage**: `./bin/view_logs.sh`

- **[automated_scheduler.sh](automated_scheduler.sh)** - Update scheduling system
  - Manages cron jobs for automated knowledge source updates
  - Configurable schedules with retry mechanisms
  - **Usage**: `./bin/automated_scheduler.sh`

### Platform Utilities
- **[demo_platform.sh](demo_platform.sh)** - Platform demonstration
  - Comprehensive showcase of platform capabilities
  - Performance comparisons and feature demonstrations
  - **Usage**: `./bin/demo_platform.sh`

- **[cleanup_platform.sh](cleanup_platform.sh)** - Platform cleanup
  - Removes outdated files and optimizes repository structure
  - Safe cleanup with confirmation prompts
  - **Usage**: `./bin/cleanup_platform.sh`

## 📁 Legacy Scripts

The `legacy/` subdirectory contains older implementation scripts that are maintained for reference:

- **[setup.sh](legacy/setup.sh)** - Legacy setup script (empty)
- **[start.sh](legacy/start.sh)** - Legacy service starter
- **[test_backend.sh](legacy/test_backend.sh)** - Legacy testing script (empty)

## 🔧 Script Categories

### By Function:
| Category | Scripts | Purpose |
|----------|---------|---------|
| **Startup** | `start_server_mode.sh` | Platform initialization |
| **Knowledge** | `add_knowledge_source.sh`, `manage_hybrid_sources.sh` | Knowledge source management |
| **Monitoring** | `view_logs.sh`, `automated_scheduler.sh` | Operations and monitoring |
| **Utilities** | `demo_platform.sh`, `cleanup_platform.sh` | Platform utilities |
| **Legacy** | `legacy/*` | Historical reference |

### By Usage Frequency:
| Priority | Scripts | When to Use |
|----------|---------|-------------|
| **Daily** | `start_server_mode.sh`, `view_logs.sh` | Regular operations |
| **Weekly** | `add_knowledge_source.sh`, `manage_hybrid_sources.sh` | Knowledge management |
| **As Needed** | `demo_platform.sh`, `cleanup_platform.sh`, `automated_scheduler.sh` | Maintenance & demos |

## 🚀 Quick Start

```bash
# 1. Start the platform
./bin/start_server_mode.sh

# 2. Add a knowledge source
./bin/add_knowledge_source.sh

# 3. Monitor the system
./bin/view_logs.sh

# 4. Set up automated updates
./bin/automated_scheduler.sh
```

## 📋 Script Dependencies

All scripts are designed to be self-contained with minimal dependencies:

- **Python Environment**: Uses `openwebui_venv/` for Python scripts
- **System Tools**: `curl`, `jq`, `lsof` for service management
- **Optional**: `tree` for directory visualization

## 🔐 Permissions

All main scripts have execute permissions. If needed, restore permissions:

```bash
chmod +x bin/*.sh
chmod +x bin/legacy/*.sh
```

## 📖 Documentation

For detailed information about each script's functionality, see:
- **[Platform Documentation](../docs/)** - Complete platform documentation
- **[Startup Guide](../docs/STARTUP_GUIDE.md)** - Quick start instructions
- **[Architecture Overview](../docs/KNOWLEDGE_FUSION_ARCHITECTURE.md)** - System architecture

## 🔄 Maintenance

### Adding New Scripts:
1. Place in appropriate category (main `bin/` or `bin/legacy/`)
2. Add execute permissions: `chmod +x bin/new_script.sh`
3. Update this README with script description
4. Update main project documentation if needed

### Script Naming Convention:
- Use descriptive names with underscores: `manage_knowledge_sources.sh`
- Include purpose in name: `start_`, `view_`, `cleanup_`, etc.
- Keep consistent with existing naming patterns

---

**Need help?** Run any script with `--help` flag or see the [main documentation](../docs/README.md).