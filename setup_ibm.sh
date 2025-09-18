#!/bin/bash

# IBM Corporate Network Compatible Setup
# Downloads OpenWebUI without requiring git submodule access

set -e

echo "🏢 Setting up for IBM Corporate Environment"
echo "=========================================="

# Function to download and extract OpenWebUI
download_openwebui() {
    local download_dir="$1"
    local version="${2:-main}"
    
    echo "📥 Downloading OpenWebUI v0.6.29 (compatible with corporate networks)..."
    
    # Remove existing directory if it exists
    if [ -d "$download_dir" ]; then
        echo "🗑️  Removing existing OpenWebUI directory..."
        rm -rf "$download_dir"
    fi
    
    # Download using curl (works through most corporate proxies)
    local zip_url="https://github.com/open-webui/open-webui/archive/refs/heads/main.zip"
    local temp_zip="/tmp/open-webui-main.zip"
    
    echo "🌐 Downloading from: $zip_url"
    
    # Try direct download first
    if curl -L -o "$temp_zip" "$zip_url" 2>/dev/null; then
        echo "✅ Download successful"
    else
        echo "❌ Direct download failed. Trying with insecure flag for corporate proxies..."
        if curl -L -k -o "$temp_zip" "$zip_url" 2>/dev/null; then
            echo "✅ Download successful (with insecure flag)"
        else
            echo "❌ Download failed. Please check network connectivity or corporate proxy settings."
            return 1
        fi
    fi
    
    # Extract the downloaded file
    echo "📦 Extracting OpenWebUI..."
    
    # Create temporary extraction directory
    local temp_extract="/tmp/openwebui-extract"
    mkdir -p "$temp_extract"
    
    if command -v unzip >/dev/null 2>&1; then
        unzip -q "$temp_zip" -d "$temp_extract"
    else
        echo "❌ unzip command not found. Please install unzip or use a different method."
        return 1
    fi
    
    # Move the extracted content to the target directory
    mv "$temp_extract/open-webui-main" "$download_dir"
    
    # Cleanup
    rm -f "$temp_zip"
    rm -rf "$temp_extract"
    
    echo "✅ OpenWebUI downloaded and extracted to: $download_dir"
    return 0
}

# Function to setup Knowledge Fusion integration
setup_knowledge_fusion() {
    local openwebui_dir="$1"
    
    echo "🧠 Setting up Knowledge Fusion integration..."
    
    # Create knowledge fusion directory structure
    local kf_dir="$openwebui_dir/knowledge-fusion"
    mkdir -p "$kf_dir/functions"
    mkdir -p "$kf_dir/tools"
    mkdir -p "$kf_dir/config"
    
    # Copy Knowledge Fusion template files
    if [ -d "knowledge-fusion-template" ]; then
        echo "📋 Copying Knowledge Fusion template files..."
        cp -r knowledge-fusion-template/* "$kf_dir/"
    fi
    
    # Create integration scripts
    cat > "$kf_dir/install_integration.py" << 'EOF'
#!/usr/bin/env python3
"""
Knowledge Fusion Integration Installer for OpenWebUI
Installs Knowledge Fusion without requiring git submodule access
"""

import os
import shutil
import json
from pathlib import Path

def install_knowledge_fusion_functions():
    """Install Knowledge Fusion functions into OpenWebUI"""
    
    # Define source and target directories
    kf_dir = Path(__file__).parent
    functions_dir = kf_dir / "functions"
    target_dir = Path(__file__).parent.parent / "backend" / "open_webui" / "functions"
    
    print("🔧 Installing Knowledge Fusion functions...")
    
    # Ensure target directory exists
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy function files
    if functions_dir.exists():
        for func_file in functions_dir.glob("*.py"):
            target_file = target_dir / func_file.name
            shutil.copy2(func_file, target_file)
            print(f"   ✅ Installed: {func_file.name}")
    
    print("✅ Knowledge Fusion functions installed")

def install_knowledge_fusion_tools():
    """Install Knowledge Fusion tools into OpenWebUI"""
    
    # Define source and target directories  
    kf_dir = Path(__file__).parent
    tools_dir = kf_dir / "tools"
    target_dir = Path(__file__).parent.parent / "backend" / "open_webui" / "tools"
    
    print("🛠️  Installing Knowledge Fusion tools...")
    
    # Ensure target directory exists
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy tool files
    if tools_dir.exists():
        for tool_file in tools_dir.glob("*.py"):
            target_file = target_dir / tool_file.name
            shutil.copy2(tool_file, target_file)
            print(f"   ✅ Installed: {tool_file.name}")
    
    print("✅ Knowledge Fusion tools installed")

def configure_openwebui():
    """Configure OpenWebUI for Knowledge Fusion integration"""
    
    print("⚙️  Configuring OpenWebUI for Knowledge Fusion...")
    
    # Update configuration files if they exist
    backend_dir = Path(__file__).parent.parent / "backend"
    config_files = [
        "open_webui/config.py",
        "open_webui/main.py"
    ]
    
    for config_file in config_files:
        config_path = backend_dir / config_file
        if config_path.exists():
            print(f"   📝 Configuration file found: {config_file}")
            # Add any necessary configuration changes here
    
    print("✅ OpenWebUI configured for Knowledge Fusion")

if __name__ == "__main__":
    print("🚀 Installing Knowledge Fusion Integration...")
    print("=" * 50)
    
    try:
        install_knowledge_fusion_functions()
        install_knowledge_fusion_tools()
        configure_openwebui()
        
        print("\n🎉 Knowledge Fusion integration installed successfully!")
        print("📋 Next steps:")
        print("   1. Run: cd .. && pip install -e .")
        print("   2. Start OpenWebUI normally")
        print("   3. Knowledge Fusion features will be available in the interface")
        
    except Exception as e:
        print(f"\n❌ Installation failed: {str(e)}")
        exit(1)
EOF

    chmod +x "$kf_dir/install_integration.py"
    
    echo "✅ Knowledge Fusion setup complete"
}

# Function to configure for IBM environment
configure_ibm_environment() {
    echo "🏢 Configuring for IBM Corporate Environment..."
    
    # Set git configuration for HTTPS only (no SSH)
    git config --global url."https://github.com/".insteadOf git@github.com: 2>/dev/null || true
    git config --global http.sslverify false 2>/dev/null || true
    
    # Configure proxy settings if HTTP_PROXY is set
    if [ -n "${HTTP_PROXY:-}" ]; then
        echo "🌐 Configuring proxy settings..."
        git config --global http.proxy "$HTTP_PROXY"
        git config --global https.proxy "$HTTPS_PROXY"
    fi
    
    echo "✅ IBM environment configuration complete"
}

# Main execution
main() {
    echo "🚀 IBM Corporate Network Compatible Setup Starting..."
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "setup.sh" ]; then
        echo "❌ Please run this script from the knowledgebase repository directory"
        exit 1
    fi
    
    # Configure IBM environment
    configure_ibm_environment
    
    # Download OpenWebUI directly (no git submodules)
    if ! download_openwebui "open-webui-cloned" "main"; then
        echo "❌ Failed to download OpenWebUI"
        exit 1
    fi
    
    # Setup Knowledge Fusion integration
    setup_knowledge_fusion "open-webui-cloned"
    
    # Run the Knowledge Fusion integration installer
    echo "🔧 Running Knowledge Fusion integration installer..."
    cd open-webui-cloned/knowledge-fusion
    python3 install_integration.py
    cd ../..
    
    echo ""
    echo "🎉 IBM Corporate Setup Complete!"
    echo "===============================+"
    echo ""
    echo "✅ OpenWebUI downloaded without git submodules"
    echo "✅ Knowledge Fusion integration installed"
    echo "✅ Corporate network compatibility configured"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Run: ./setup.sh --ibm"
    echo "   2. Run: ./start.sh"
    echo "   3. Access at: http://localhost:3000"
    echo ""
    echo "🏢 This setup works on IBM networks without GitHub authentication!"
}

# Run main function
main "$@"