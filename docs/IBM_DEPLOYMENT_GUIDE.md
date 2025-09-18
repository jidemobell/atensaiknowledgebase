# 🏢 IBM Corporate Network Setup Guide

## Quick Setup for IBM Computers

### **For IBM Corporate Networks (Recommended)**

```bash
# Clone the repository (works without GitHub authentication)
git clone https://github.com/jidemobell/knowledgebase.git
cd knowledgebase

# Use special IBM setup (downloads OpenWebUI without git submodules)
./setup.sh --ibm

# Start the platform
./start.sh
```

### **Alternative: Standard Setup (if corporate network allows)**

```bash
git clone https://github.com/jidemobell/knowledgebase.git
cd knowledgebase
./setup.sh --enterprise
./start.sh
```

## 🔧 How IBM Setup Works

The `--ibm` option bypasses git submodule issues by:

1. **Direct Download**: Downloads OpenWebUI as a ZIP file instead of using git submodules
2. **Corporate Proxy Compatible**: Uses curl with corporate proxy support
3. **No Authentication Required**: Downloads from public GitHub URLs without needing authentication
4. **Knowledge Fusion Integration**: Automatically installs all Knowledge Fusion customizations

## 🌐 Corporate Network Compatibility

### **Proxy Configuration**
If your network uses a proxy, set these environment variables before running setup:

```bash
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=https://your-proxy:port
export NO_PROXY=localhost,127.0.0.1
```

### **SSL Certificate Issues**
If you encounter SSL certificate errors:

```bash
# Run setup with insecure flag (only for corporate networks)
git config --global http.sslverify false
./setup.sh --ibm
```

## 📋 Step-by-Step IBM Setup

### **1. Clone Repository**
```bash
git clone https://github.com/jidemobell/knowledgebase.git
cd knowledgebase
```

### **2. Configure Corporate Network (if needed)**
```bash
# For proxy environments
export HTTP_PROXY=http://your-corporate-proxy:port
export HTTPS_PROXY=https://your-corporate-proxy:port

# For SSL certificate issues
git config --global http.sslverify false
```

### **3. Run IBM Setup**
```bash
./setup.sh --ibm
```

This will:
- ✅ Download OpenWebUI v0.6.29 directly (no git submodules)
- ✅ Install Knowledge Fusion integration
- ✅ Configure for corporate networks
- ✅ Set up Python virtual environment
- ✅ Install all dependencies

### **4. Start Platform**
```bash
./start.sh
```

### **5. Access Platform**
- **Web Interface**: http://localhost:3000
- **API**: http://localhost:8080

## 🔍 Troubleshooting IBM Networks

### **Issue: Download Fails**
```bash
# Check proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Test connectivity
curl -I https://github.com/open-webui/open-webui
```

### **Issue: SSL Certificate Errors**
```bash
# Disable SSL verification (corporate networks only)
git config --global http.sslverify false
export PYTHONHTTPSVERIFY=0
```

### **Issue: Permission Denied**
```bash
# Ensure script is executable
chmod +x setup.sh
chmod +x setup_ibm.sh
chmod +x start.sh
```

## 🎯 What Gets Installed

### **OpenWebUI v0.6.29**
- Complete web interface for AI interactions
- User management and authentication
- Vector database for knowledge storage
- API endpoints for integration

### **Knowledge Fusion Integration**
- Advanced AI reasoning capabilities
- Multi-source knowledge synthesis
- GitHub repository analysis tools
- Enhanced conversation memory

### **Corporate Network Optimizations**
- HTTPS-only configuration
- Proxy-aware downloads
- SSL certificate bypass options
- No SSH key requirements

## 🚀 Deployment Options

### **Single Machine Setup**
```bash
./setup.sh --ibm && ./start.sh
```

### **Team Deployment**
1. One person runs the setup on a shared machine
2. Team members access via: `http://shared-machine-ip:3000`
3. No individual setup required

### **Container Deployment** (if Docker allowed)
```bash
# After IBM setup
docker build -t topology-knowledge .
docker run -p 3000:3000 -p 8080:8080 topology-knowledge
```

## ✅ Verification

After setup, verify everything works:

```bash
# Check if OpenWebUI downloaded correctly
ls -la open-webui-cloned/

# Check Knowledge Fusion integration
ls -la open-webui-cloned/knowledge-fusion/

# Test web interface
curl http://localhost:3000

# Check API endpoint
curl http://localhost:8080/health
```

## 📞 Support

If you encounter issues specific to IBM corporate networks:

1. **Check network policies** with your IT department
2. **Verify proxy settings** are correctly configured
3. **Test basic internet connectivity** to GitHub
4. **Contact repository maintainer** with specific error messages

---

**💡 Note**: This setup is specifically designed for IBM corporate environments where traditional git submodule access may be restricted. It provides the same functionality as the standard setup but with better corporate network compatibility.
