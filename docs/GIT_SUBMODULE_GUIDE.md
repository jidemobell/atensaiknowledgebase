# 🔄 Git Submodule Management Guide

## Overview

The Topology Knowledge Platform uses **git submodules** to manage the OpenWebUI dependency. This approach allows us to:

- Track a specific version of OpenWebUI
- Keep our custom modifications separate and manageable
- Update OpenWebUI independently when needed
- Maintain a clean separation between our code and upstream dependencies

## Current Setup

```
TOPOLOGYKNOWLEDGE/                 # Main repository
├── openwebuibase/                # Git submodule → open-webui/open-webui
│   ├── knowledge-fusion/         # Our custom integration (tracked)
│   ├── .env.example             # Our template (tracked)
│   └── [other OpenWebUI files]  # Submodule content (tracked as commit hash)
├── corebackend/                 # Our code (tracked)
├── docs/                        # Our documentation (tracked)
└── start*.sh                    # Our startup scripts (tracked)
```

## Git Submodule Commands

### For Repository Cloning
When someone clones your repository, they need to initialize submodules:

```bash
# Clone with submodules
git clone --recursive https://github.com/YOUR_USERNAME/YOUR_REPO.git

# OR clone normally then initialize submodules
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
git submodule init
git submodule update
```

### For Submodule Updates
When you want to update to a newer version of OpenWebUI:

```bash
# Go to submodule directory
cd openwebuibase

# Fetch and checkout latest OpenWebUI
git fetch
git checkout main  # or specific tag like v0.6.28

# Return to main repository
cd ..

# Commit the submodule update
git add openwebuibase
git commit -m "Update OpenWebUI to latest version"
```

### For Development Workflow
When working with the project:

```bash
# Check submodule status
git submodule status

# Update all submodules to their latest commits
git submodule update --recursive

# Reset submodule to committed version
git submodule update --init --recursive
```

## Our Custom Modifications

### What We Track in the Submodule
- `knowledge-fusion/` - Our IBM Knowledge Fusion integration
- `.env.example` - Our environment template
- Key configuration files we customize

### What We Don't Track
- `node_modules/` - Dependencies (installed locally)
- Build artifacts (`dist/`, `build/`)
- Environment files (`.env`, `.env.local`)
- IDE files (`.vscode/`, `.idea/`)
- Logs and cache files

## Development Best Practices

### 1. Making Changes to OpenWebUI
```bash
# Go to submodule
cd openwebuibase

# Create a branch for your changes
git checkout -b custom-modifications

# Make your changes
# Edit files, add knowledge-fusion integration, etc.

# Commit your changes in the submodule
git add .
git commit -m "Add Knowledge Fusion integration"

# Return to main repo and commit the submodule update
cd ..
git add openwebuibase
git commit -m "Update OpenWebUI with Knowledge Fusion integration"
```

### 2. Keeping Our Integration Up to Date
```bash
# Fetch latest OpenWebUI
cd openwebuibase
git fetch origin

# Merge or rebase our changes onto latest OpenWebUI
git rebase origin/main custom-modifications

# Update the main repository
cd ..
git add openwebuibase
git commit -m "Rebase Knowledge Fusion on latest OpenWebUI"
```

### 3. Handling Merge Conflicts
If OpenWebUI updates conflict with our modifications:

```bash
cd openwebuibase

# During rebase, if conflicts occur:
# 1. Resolve conflicts in affected files
# 2. Continue the rebase
git add .
git rebase --continue

# Return to main repo
cd ..
git add openwebuibase
git commit -m "Resolve conflicts in OpenWebUI integration"
```

## Repository Management

### For Team Members
Add this to your team's setup documentation:

```bash
# Initial setup (one time)
git clone --recursive YOUR_REPO_URL
cd REPO_NAME

# Daily workflow
git pull                    # Update main repo
git submodule update       # Update submodules to committed versions

# Before making changes
git submodule status       # Check submodule state
```

### For CI/CD Pipelines
Ensure your CI/CD handles submodules:

```yaml
# GitHub Actions example
- uses: actions/checkout@v3
  with:
    submodules: recursive
```

### For Docker Builds
Your Dockerfile can handle submodules:

```dockerfile
# In Dockerfile
COPY .gitmodules .
RUN git submodule init && git submodule update
```

## Troubleshooting

### Common Issues

**1. Submodule shows as modified but no changes**
```bash
# Reset to committed version
git submodule update --init --recursive
```

**2. Can't push submodule changes**
```bash
# Make sure you're on a branch in the submodule
cd openwebuibase
git checkout -b my-changes
git commit -am "My changes"
cd ..
git add openwebuibase
git commit -m "Update submodule"
```

**3. Submodule points to wrong commit**
```bash
# Check what commit the submodule should be at
git ls-tree HEAD openwebuibase

# Reset submodule to that commit
cd openwebuibase
git checkout COMMIT_HASH
cd ..
```

**4. Want to switch to different OpenWebUI version**
```bash
cd openwebuibase
git checkout v0.6.28  # or any tag/branch
cd ..
git add openwebuibase
git commit -m "Switch to OpenWebUI v0.6.28"
```

## Benefits of This Approach

### ✅ Advantages
- **Version Control**: Track exactly which OpenWebUI version you're using
- **Clean Updates**: Update OpenWebUI independently of your code
- **Isolation**: Your modifications don't interfere with upstream code
- **Reproducibility**: Anyone can clone and get the exact same environment
- **History**: Clear history of when you updated OpenWebUI

### ⚠️ Considerations
- **Complexity**: Team members need to understand submodules
- **Merge Conflicts**: Updates may conflict with your modifications
- **Branch Management**: Need to manage branches in both repos

## Quick Reference

```bash
# Clone project
git clone --recursive YOUR_REPO

# Update OpenWebUI
cd openwebuibase && git pull origin main && cd .. && git add openwebuibase && git commit -m "Update OpenWebUI"

# Reset everything
git submodule update --init --recursive

# Check status
git submodule status

# Add custom changes
cd openwebuibase && git add . && git commit -m "Custom changes" && cd .. && git add openwebuibase && git commit -m "Update submodule"
```

This approach gives you the flexibility to customize OpenWebUI while keeping your modifications organized and maintainable!
