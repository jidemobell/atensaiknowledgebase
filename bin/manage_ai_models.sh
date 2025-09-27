#!/bin/bash
# AI Model Management Script for Knowledge Fusion Platform
# Configure and optimize AI models for maximum intelligence

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/../config"
CONFIG_FILE="$CONFIG_DIR/ai_models_config.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗"
    echo -e "║                    🤖 AI Model Manager                       ║"
    echo -e "║              Knowledge Fusion Platform v2.0                  ║"
    echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
}

print_section() {
    echo -e "${PURPLE}▶ $1${NC}"
}

check_ollama() {
    print_section "Checking Ollama availability..."
    
    if ! command -v ollama &> /dev/null; then
        echo -e "${RED}❌ Ollama not found. Please install Ollama first.${NC}"
        echo "Visit: https://ollama.ai"
        exit 1
    fi
    
    if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️ Ollama service not running. Starting Ollama...${NC}"
        ollama serve &
        sleep 3
    fi
    
    echo -e "${GREEN}✅ Ollama is available${NC}"
}

list_available_models() {
    print_section "Available Models:"
    ollama list
    echo
}

recommend_models() {
    print_section "🎯 Model Recommendations for Maximum Intelligence:"
    echo
    echo -e "${GREEN}🥇 TIER 1: Maximum Intelligence (Recommended)${NC}"
    echo "   Primary LLM:     llama3.1:8b        (Excellent reasoning)"
    echo "   Code Specialist: codellama:13b      (Superior code analysis)" 
    echo "   Embedding:       nomic-embed-text   (Best semantic search)"
    echo "   Vision:          llava:13b          (Advanced vision capabilities)"
    echo
    echo -e "${BLUE}🥈 TIER 2: Granite Optimized (Your Current Setup)${NC}"
    echo "   Primary LLM:     granite3.2:8b-instruct-q8.0"
    echo "   Code Specialist: granite3.2:8b"
    echo "   Vision:          granite3.2-vision:2b"
    echo "   Embedding:       nomic-embed-text"
    echo
    echo -e "${YELLOW}🥉 TIER 3: High Performance${NC}"
    echo "   Primary LLM:     llama3.1:70b       (Ultimate intelligence)"
    echo "   Code Specialist: codellama:34b      (Best code understanding)"
    echo "   Embedding:       nomic-embed-text"
    echo "   Note: Requires 64GB+ RAM"
    echo
}

pull_recommended_models() {
    local tier="$1"
    
    case "$tier" in
        "1"|"tier1"|"maximum")
            print_section "Pulling Tier 1: Maximum Intelligence Models..."
            ollama pull llama3.1:8b
            ollama pull codellama:13b  
            ollama pull nomic-embed-text
            ollama pull llava:13b
            echo -e "${GREEN}✅ Tier 1 models installed${NC}"
            ;;
        "2"|"tier2"|"granite") 
            print_section "Optimizing Granite Setup..."
            # You already have granite models, just need embedding
            ollama pull nomic-embed-text
            echo -e "${GREEN}✅ Granite setup optimized${NC}"
            ;;
        "3"|"tier3"|"high")
            print_section "Pulling Tier 3: High Performance Models..."
            echo -e "${YELLOW}⚠️ This requires significant resources (64GB+ RAM)${NC}"
            read -p "Continue? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                ollama pull llama3.1:70b
                ollama pull codellama:34b
                ollama pull nomic-embed-text
                echo -e "${GREEN}✅ High performance models installed${NC}"
            fi
            ;;
        *)
            echo -e "${RED}❌ Invalid tier. Use: 1, 2, or 3${NC}"
            exit 1
            ;;
    esac
}

configure_profile() {
    local profile="$1"
    
    print_section "Configuring AI Model Profile: $profile"
    
    # Update the active profile in config
    if [ -f "$CONFIG_FILE" ]; then
        # Create a backup
        cp "$CONFIG_FILE" "$CONFIG_FILE.backup"
        
        # Update active profile using jq if available, otherwise manual
        if command -v jq &> /dev/null; then
            jq ".active_profile = \"$profile\"" "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
            echo -e "${GREEN}✅ Profile '$profile' activated${NC}"
        else
            echo -e "${YELLOW}⚠️ jq not available. Please manually update active_profile to '$profile' in $CONFIG_FILE${NC}"
        fi
    else
        echo -e "${RED}❌ Configuration file not found: $CONFIG_FILE${NC}"
        exit 1
    fi
}

test_models() {
    print_section "Testing AI Models..."
    
    echo "Testing primary model..."
    echo "What is ASM topology?" | ollama run llama3.1:8b 2>/dev/null | head -n 3
    
    echo
    echo "Testing embedding model..." 
    if ollama list | grep -q "nomic-embed-text"; then
        echo -e "${GREEN}✅ Embedding model available${NC}"
    else
        echo -e "${YELLOW}⚠️ Embedding model not found${NC}"
    fi
}

show_current_config() {
    print_section "Current Configuration:"
    
    if [ -f "$CONFIG_FILE" ]; then
        if command -v jq &> /dev/null; then
            echo "Active Profile: $(jq -r '.active_profile' "$CONFIG_FILE")"
            echo
            echo "Current Models:"
            jq -r '.model_profiles[.active_profile] | to_entries[] | "  \(.key): \(.value)"' "$CONFIG_FILE"
        else
            echo "Configuration file exists: $CONFIG_FILE"
            echo "Install 'jq' for detailed configuration display"
        fi
    else
        echo -e "${YELLOW}⚠️ No configuration file found${NC}"
    fi
    echo
}

show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  recommend              Show model recommendations"
    echo "  pull <tier>           Pull recommended models (1=balanced, 2=granite, 3=high-performance)"
    echo "  configure <profile>    Set active model profile"
    echo "  test                  Test current models"
    echo "  status                Show current configuration"
    echo "  list                  List available models"
    echo
    echo "Profiles:"
    echo "  balanced_performance   Optimal balance (recommended)"
    echo "  granite_optimized     Use your existing Granite models"  
    echo "  maximum_intelligence  Best possible performance"
    echo "  efficient_setup       Lightweight configuration"
    echo
    echo "Examples:"
    echo "  $0 recommend"
    echo "  $0 pull 1"
    echo "  $0 configure balanced_performance"
    echo "  $0 test"
}

# Main script logic
print_header

case "${1:-help}" in
    "recommend"|"rec")
        check_ollama
        recommend_models
        ;;
    "pull")
        check_ollama
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Please specify tier (1, 2, or 3)${NC}"
            exit 1
        fi
        pull_recommended_models "$2"
        ;;
    "configure"|"config")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Please specify profile${NC}"
            exit 1
        fi
        configure_profile "$2"
        ;;
    "test")
        check_ollama
        test_models
        ;;
    "status"|"current")
        show_current_config
        ;;
    "list"|"ls")
        check_ollama
        list_available_models
        ;;
    "help"|"--help"|"-h")
        show_usage
        ;;
    *)
        show_usage
        exit 1
        ;;
esac