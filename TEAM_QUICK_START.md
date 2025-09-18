# 🚀 Quick Start for Team Members

## For Any Computer (No SSH Keys Needed)

```bash
# Clone the repository with submodules
git clone --recursive https://github.com/jidemobell/knowledgebase.git

# Enter the directory
cd knowledgebase

# Run setup (auto-detects your environment)
./setup.sh

# Start the platform
./start.sh
```

## Alternative: Step-by-Step

```bash
# Clone main repository
git clone https://github.com/jidemobell/knowledgebase.git
cd knowledgebase

# Initialize submodules
git submodule update --init --recursive

# Setup environment
./setup.sh

# Start platform
./start.sh
```

## For Corporate/Enterprise Environments

### **IBM Corporate Networks**
```bash
git clone https://github.com/jidemobell/knowledgebase.git
cd knowledgebase
./setup.sh --ibm
./start.sh
```

### **Other Corporate Environments**
```bash
git clone https://github.com/jidemobell/knowledgebase.git
cd knowledgebase
./setup.sh --enterprise
./start.sh
```

## Troubleshooting

**If you see "Permission denied (publickey)" errors:**
- Use the `--enterprise` flag: `./setup.sh --enterprise`
- This configures everything to use HTTPS instead of SSH

**If submodules fail to initialize:**
```bash
git config --global url."https://github.com/".insteadOf git@github.com:
git submodule update --init --recursive
```

## What This Sets Up

- ✅ **OpenWebUI v0.6.29** - Latest stable version with full frontend
- ✅ **Knowledge Fusion** - Advanced AI integration layer  
- ✅ **Topology Knowledge** - Next-generation knowledge synthesis
- ✅ **Cross-machine compatibility** - Works anywhere with internet access

## Access Points

After successful startup:
- **Web Interface**: http://localhost:3000
- **API Endpoint**: http://localhost:8080
- **Knowledge Fusion**: Integrated within the web interface

---

*Repository is now configured for universal access - no SSH keys required!*
