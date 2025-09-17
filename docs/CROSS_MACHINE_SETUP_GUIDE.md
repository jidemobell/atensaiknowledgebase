# 🔧 Cross-Machine Setup Guide

This guide helps you set up the Topology Knowledge platform on different computers, handling various access scenarios.

## 📋 Setup Scenarios

### **Scenario 1: New Computer (No SSH Keys)**
*Most common for fresh installations or enterprise environments*

```bash
# Clone with HTTPS (works without SSH setup)
git clone https://github.com/jidemobell/knowledgebase.git
cd knowledgebase

# Initialize submodules (will use HTTPS automatically)
git submodule update --init --recursive

# Run setup
./setup.sh
```

### **Scenario 2: Personal Computer (SSH Available)**
*For development machines with GitHub SSH keys*

```bash
# Clone with SSH (faster for development)
git clone git@github.com:jidemobell/knowledgebase.git
cd knowledgebase

# Submodules will still use HTTPS for compatibility
git submodule update --init --recursive

# Run setup
./setup.sh
```

### **Scenario 3: Enterprise/Corporate Environment**
*For environments with restricted access or proxy requirements*

```bash
# Clone with HTTPS
git clone https://github.com/jidemobell/knowledgebase.git
cd knowledgebase

# If behind corporate proxy, configure git first:
# git config --global http.proxy http://your-proxy:port
# git config --global https.proxy https://your-proxy:port

# Initialize submodules
git submodule update --init --recursive

# Run setup with HTTPS preference
./setup.sh --https
```

## 🔍 Troubleshooting Access Issues

### **SSH Key Issues**
If you see errors like `Permission denied (publickey)`:

```bash
# Solution 1: Switch to HTTPS
git remote set-url origin https://github.com/jidemobell/knowledgebase.git

# Solution 2: Set up SSH keys (one-time setup)
ssh-keygen -t ed25519 -C "your-email@example.com"
# Then add the public key to GitHub Settings > SSH Keys
```

### **Corporate Firewall Issues**
If submodule cloning fails:

```bash
# Configure git to use HTTPS for all GitHub URLs
git config --global url."https://github.com/".insteadOf git@github.com:

# Or for just this repository
git config url."https://github.com/".insteadOf git@github.com:
```

### **Private Repository Access**
If you need access to private repositories:

```bash
# Option 1: Use Personal Access Token
git config --global credential.helper store
# Then enter username and token when prompted

# Option 2: Use GitHub CLI
gh auth login
```

## ⚙️ Automatic Setup Detection

The `setup.sh` script automatically detects your environment:

- **SSH Available**: Uses SSH for faster cloning
- **HTTPS Only**: Falls back to HTTPS automatically
- **Corporate Environment**: Detects proxy settings
- **Fresh Installation**: Guides through first-time setup

## 📚 Updated Documentation

### **For Fresh Installations**
```bash
# Quick start (works everywhere)
git clone https://github.com/jidemobell/knowledgebase.git
cd knowledgebase
./setup.sh
./start.sh
```

### **For Development**
```bash
# Development setup (with SSH if available)
git clone git@github.com:jidemobell/knowledgebase.git
cd knowledgebase
git submodule update --init --recursive
./setup.sh --dev
```

## 🎯 Key Changes Made

1. **✅ HTTPS Submodule URLs**: Submodules now use HTTPS by default
2. **✅ Flexible Remote URLs**: Main repository supports both SSH and HTTPS
3. **✅ Corporate Compatibility**: Works in enterprise environments
4. **✅ Automatic Fallback**: Setup script detects and adapts to available access methods

## 🔧 Manual Configuration

If you need to manually configure access:

```bash
# Check current remotes
git remote -v

# Switch main repository to HTTPS
git remote set-url origin https://github.com/jidemobell/knowledgebase.git

# Update submodule URLs to HTTPS
git config submodule.open-webui-cloned.url https://github.com/jidemobell/atensai-open-webui.git

# Sync submodule configuration
git submodule sync
git submodule update --init --recursive
```

## ✅ Verification

After setup, verify everything works:

```bash
# Check repository status
git status
git submodule status

# Verify submodule content
ls -la open-webui-cloned/knowledge-fusion/

# Test platform startup
./start.sh
```

---

*This guide ensures the Topology Knowledge platform works consistently across all computing environments, from personal laptops to enterprise data centers.*
