#!/bin/bash
# GitHub Token Configuration Script
# Run this to set up your GitHub token for the Knowledge Fusion Platform

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔑 GitHub Authentication Setup for Knowledge Fusion Platform${NC}"
echo "============================================================"

echo "This script supports two authentication methods:"
echo "1. 🔑 Personal Access Token (if available)"
echo "2. 🔐 SSH Authentication (enterprise-friendly)"
echo ""

# Check if token is already set
if [ -n "$GITHUB_TOKEN" ]; then
    echo -e "${GREEN}✅ GITHUB_TOKEN is already set${NC}"
    echo "   Token preview: ${GITHUB_TOKEN:0:8}..."
    echo ""
else
    echo -e "${YELLOW}⚠️  GITHUB_TOKEN is not set${NC}"
    echo ""
    echo "🏢 Enterprise GitHub Note:"
    echo "If your organization doesn't allow personal tokens, we'll set up SSH instead."
    echo ""
    echo ""
fi

echo "📋 To set up your GitHub token:"
echo ""
echo "1️⃣  Get your token from GitHub:"
echo "   🔗 https://github.com/settings/tokens"
echo ""
echo "2️⃣  Set the environment variable:"
echo "   For current session:"
echo "   export GITHUB_TOKEN=\"your_token_here\""
echo ""
echo "   For permanent setup (add to ~/.zshrc or ~/.bashrc):"
echo "   echo 'export GITHUB_TOKEN=\"your_token_here\"' >> ~/.zshrc"
echo "   source ~/.zshrc"
echo ""
echo "3️⃣  Required token permissions:"
echo "   ✅ repo (Full repository access)"
echo "   ✅ public_repo (Public repository access)"
echo "   ✅ read:org (Read organization membership)"
echo ""
echo "4️⃣  Test your setup:"
echo "   ./bin/test_github_token.sh"
echo ""

# Offer to help set the token
echo -e "${YELLOW}💡 Would you like to set the token now? (y/n)${NC}"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "Please enter your GitHub token:"
    read -s token
    
    if [ -n "$token" ]; then
        export GITHUB_TOKEN="$token"
        echo -e "${GREEN}✅ Token set for current session${NC}"
        echo ""
        echo "To make this permanent, add this line to your shell config:"
        echo "export GITHUB_TOKEN=\"$token\""
        
        # Test the token
        echo ""
        echo "🧪 Testing token..."
        if curl -s -H "Authorization: token $token" https://api.github.com/user > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Token is valid!${NC}"
        else
            echo -e "${RED}❌ Token test failed. Please check your token.${NC}"
        fi
    else
        echo -e "${RED}❌ No token provided${NC}"
        echo ""
        echo -e "${BLUE}🔐 Setting up SSH authentication instead...${NC}"
        setup_ssh_auth
    fi
fi

# SSH Authentication Setup Function
setup_ssh_auth() {
    echo ""
    echo -e "${BLUE}🔐 SSH Authentication Setup${NC}"
    echo "============================"
    echo ""
    
    # Check if SSH key exists
    if [ -f ~/.ssh/id_rsa.pub ] || [ -f ~/.ssh/id_ed25519.pub ]; then
        echo -e "${GREEN}✅ SSH key found${NC}"
        
        # Show public key
        if [ -f ~/.ssh/id_ed25519.pub ]; then
            echo ""
            echo "📋 Your Ed25519 public key (copy this to GitHub):"
            echo "================================================"
            cat ~/.ssh/id_ed25519.pub
        elif [ -f ~/.ssh/id_rsa.pub ]; then
            echo ""
            echo "📋 Your RSA public key (copy this to GitHub):"
            echo "============================================="
            cat ~/.ssh/id_rsa.pub
        fi
    else
        echo -e "${YELLOW}⚠️  No SSH key found. Generating Ed25519 key...${NC}"
        ssh-keygen -t ed25519 -C "knowledge-fusion-$(whoami)@$(hostname)" -f ~/.ssh/id_ed25519 -N ""
        echo -e "${GREEN}✅ SSH key generated${NC}"
        echo ""
        echo "📋 Your new public key (copy this to GitHub):"
        echo "=============================================="
        cat ~/.ssh/id_ed25519.pub
    fi
    
    echo ""
    echo -e "${BLUE}🔗 GitHub SSH Setup Instructions:${NC}"
    echo "1. Copy the public key shown above"
    echo "2. Go to GitHub.com → Settings → SSH and GPG keys"
    echo "3. Click 'New SSH key'"
    echo "4. Give it a title like 'Knowledge Fusion Platform'"
    echo "5. Paste the key and click 'Add SSH key'"
    echo ""
    
    # Test GitHub SSH connection
    echo "🔍 Testing GitHub SSH connection..."
    ssh_test_output=$(ssh -T git@github.com 2>&1 || true)
    
    if echo "$ssh_test_output" | grep -q "successfully authenticated"; then
        echo -e "${GREEN}✅ GitHub SSH access working perfectly!${NC}"
        echo ""
        echo -e "${GREEN}🎯 SSH authentication is ready!${NC}"
        echo "The Knowledge Fusion platform can now access GitHub repositories via SSH."
    else
        echo -e "${YELLOW}⚠️  SSH connection test completed${NC}"
        echo "Output: $ssh_test_output"
        echo ""
        echo "This is often normal. If you added the key to GitHub, SSH should work."
        echo "You can test manually with: ssh -T git@github.com"
    fi
    
    echo ""
    echo -e "${BLUE}📝 Important Notes:${NC}"
    echo "• SSH authentication doesn't require tokens"
    echo "• Works with enterprise GitHub restrictions"  
    echo "• The platform will automatically use SSH URLs for cloning"
    echo "• Repository URLs will be converted: https://github.com/user/repo → git@github.com:user/repo"
}