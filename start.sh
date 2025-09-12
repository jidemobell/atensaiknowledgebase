#!/bin/bash

# =============================================================================
# TOPOLOGY KNOWLEDGE - MAIN LAUNCHER
# =============================================================================
# Simple launcher script for choosing between Server Mode and Containerized Mode
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║            🚀 TOPOLOGY KNOWLEDGE PLATFORM 🚀                ║"
echo "║                                                              ║"
echo "║  📁 Core Backend (QwenRoute) + OpenWebUI + Knowledge Fusion ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}Choose your deployment mode:${NC}"
echo ""
echo -e "${GREEN}1. 🖥️  SERVER MODE${NC}"
echo "   • Runs everything directly on your system"
echo "   • Uses Python virtual environments"
echo "   • Easier for development and debugging"
echo "   • Requires Python 3.11+ and dependencies"
echo ""
echo -e "${GREEN}2. 🐳 CONTAINERIZED MODE${NC}"
echo "   • Runs everything in containers (Docker/Podman)"
echo "   • Isolated and reproducible environment"
echo "   • Easier for production deployment"
echo "   • Auto-detects Docker or Podman runtime"
echo ""
echo -e "${YELLOW}3. 🔍 STATUS CHECK${NC}"
echo "   • Check what's currently running"
echo "   • View system information"
echo ""
echo -e "${RED}4. 🛑 STOP ALL${NC}"
echo "   • Stop all running services"
echo "   • Clean up processes and containers"
echo ""

# Get user choice
while true; do
    echo -n -e "${CYAN}Enter your choice (1-4): ${NC}"
    read choice
    
    case $choice in
        1)
            echo -e "\n${GREEN}🖥️  Starting SERVER MODE...${NC}"
            exec ./start_server_mode.sh
            break
            ;;
        2)
            echo -e "\n${GREEN}🐳 Starting DOCKER MODE...${NC}"
            exec ./start_docker_mode.sh
            break
            ;;
        3)
            echo -e "\n${YELLOW}🔍 CHECKING STATUS...${NC}"
            echo ""
            
            # Check what's running
            echo -e "${BLUE}Active Processes:${NC}"
            echo "Core Backend (8001):"
            curl -s http://localhost:8001/health >/dev/null 2>&1 && echo -e "  ${GREEN}✅ RUNNING${NC}" || echo -e "  ${RED}❌ STOPPED${NC}"
            
            echo "Knowledge Fusion (8002):"
            curl -s http://localhost:8002/health >/dev/null 2>&1 && echo -e "  ${GREEN}✅ RUNNING${NC}" || echo -e "  ${RED}❌ STOPPED${NC}"
            
            echo "OpenWebUI (3000):"
            curl -s http://localhost:3000 >/dev/null 2>&1 && echo -e "  ${GREEN}✅ RUNNING${NC}" || echo -e "  ${RED}❌ STOPPED${NC}"
            
            echo "Ollama (11434):"
            curl -s http://localhost:11434 >/dev/null 2>&1 && echo -e "  ${GREEN}✅ RUNNING${NC}" || echo -e "  ${RED}❌ STOPPED${NC}"
            
            echo ""
            echo -e "${BLUE}Containers:${NC}"
            # Check for Docker
            if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
                docker ps --filter "name=topology" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  No topology containers running"
            # Check for Podman
            elif command -v podman >/dev/null 2>&1 && podman info >/dev/null 2>&1; then
                podman ps --filter "name=topology" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  No topology containers running"
            else
                echo "  No container runtime available"
            fi
            
            echo ""
            echo -e "${CYAN}Press Enter to return to menu...${NC}"
            read
            exec $0
            ;;
        4)
            echo -e "\n${RED}🛑 STOPPING ALL SERVICES...${NC}"
            echo ""
            
            # Stop server mode processes
            if [ -f ".topology_pids" ]; then
                echo "Stopping server mode processes..."
                while read -r service pid; do
                    if kill -0 "$pid" 2>/dev/null; then
                        echo "  Stopping $service (PID: $pid)"
                        kill "$pid" 2>/dev/null || true
                    fi
                done < ".topology_pids"
                rm -f ".topology_pids"
            fi
            
            # Stop containers
            if [ -f "docker-compose.knowledge-fusion.yml" ]; then
                if command -v docker-compose >/dev/null 2>&1; then
                    echo "Stopping containers (Docker)..."
                    docker-compose -f docker-compose.knowledge-fusion.yml down --remove-orphans 2>/dev/null || true
                elif command -v podman-compose >/dev/null 2>&1; then
                    echo "Stopping containers (Podman)..."
                    podman-compose -f docker-compose.knowledge-fusion.yml down --remove-orphans 2>/dev/null || true
                fi
            fi
            
            echo -e "${GREEN}✅ All services stopped${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please enter 1, 2, 3, or 4.${NC}"
            ;;
    esac
done
