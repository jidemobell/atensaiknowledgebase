# 🐳 Docker Deployment Guide - Novel Knowledge Fusion Platform

## 🎯 Overview

This guide provides containerized deployment for your Novel Knowledge Fusion Platform, making it easy to deploy consistently across any environment with Docker support.

## 🏗️ Docker Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                    │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ OpenWebUI       │  │ Knowledge       │  │ Ollama       │ │
│  │ Frontend        │  │ Fusion Backend  │  │ Models       │ │
│  │ (Port 8080)     │  │ (8000,8001,8003)│  │ (Port 11434) │ │
│  │ - Svelte UI     │  │ - Novel Fusion  │  │ - Local LLMs │ │
│  │ - Model Manager │  │ - Multi-Agent   │  │ - Embeddings │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│           │                     │                    │       │
│           └─────────────────────┼────────────────────┘       │
│                                 │                            │
│  ┌─────────────────┐            │            ┌──────────────┐ │
│  │ Redis Cache     │            │            │ Nginx        │ │
│  │ (Port 6379)     │            │            │ (Port 80)    │ │
│  │ - Session store │            │            │ - Load       │ │
│  │ - Cache layer   │            │            │   Balancer   │ │
│  └─────────────────┘            │            └──────────────┘ │
│                                 │                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Persistent Volumes                     │ │
│  │ - Model storage - Knowledge base - Configuration      │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

### System Requirements
```bash
# Docker & Docker Compose
docker --version          # >= 20.10
docker-compose --version  # >= 2.0

# System resources (recommended)
# RAM: 8GB+ (4GB minimum)
# CPU: 4+ cores
# Storage: 20GB+ free space
# Network: Internet access for model downloads
```

### Install Docker (if needed)
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# macOS
brew install docker docker-compose

# Windows
# Download Docker Desktop from docker.com
```

## 🚀 Quick Docker Deployment

### 1. Setup Environment
```bash
# Clone/navigate to your project
cd /your/project/directory/TOPOLOGYKNOWLEDGE

# Create environment file from template
cp .env.docker.template .env

# Edit with your API keys
nano .env
# Update OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.
```

### 2. Start the Complete Stack
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Initialize Ollama Models
```bash
# Download recommended models
docker-compose exec ollama ollama pull llama3.1:8b
docker-compose exec ollama ollama pull mistral:7b
docker-compose exec ollama ollama pull nomic-embed-text
docker-compose exec ollama ollama pull granite3-moe:3b

# Verify models
docker-compose exec ollama ollama list
```

### 4. Verify Deployment
```bash
# Check all services are healthy
curl http://localhost:8003/health    # Novel Fusion Engine
curl http://localhost:8001/health    # Multi-Agent System
curl http://localhost:8000/health    # Basic Service
curl http://localhost:8080          # OpenWebUI Frontend
curl http://localhost:11434/api/tags # Ollama Models

# Access web interface
open http://localhost:8080
```

## 🎛️ Service Management

### Start/Stop Services
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart knowledge-fusion

# View service logs
docker-compose logs -f knowledge-fusion
docker-compose logs -f openwebui
```

### Update Services
```bash
# Rebuild and update
docker-compose build --no-cache
docker-compose up -d

# Update specific service
docker-compose build knowledge-fusion
docker-compose up -d knowledge-fusion
```

## 🎯 Deployment Scenarios

### Development Environment
```bash
# Quick development setup with code changes
docker-compose up -d
# Code changes require restart
```

### Production Environment
```bash
# Full production setup
docker-compose -f docker-compose.yml up -d
# With monitoring and SSL
```

### Cloud Deployment
```bash
# Deploy to cloud platforms
# AWS, GCP, Azure with container services
```

## 🛠️ Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check logs
docker-compose logs knowledge-fusion

# Check resource usage
docker stats

# Restart problematic service
docker-compose restart knowledge-fusion
```

#### Model Loading Issues
```bash
# Check Ollama status
docker-compose exec ollama ollama list

# Re-download models
docker-compose exec ollama ollama pull llama3.1:8b

# Check disk space
docker system df
```

### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check container health
docker-compose ps
```

## 🔄 Backup & Recovery

### Data Backup
```bash
# Backup volumes
docker run --rm -v ollama_data:/data -v $(pwd):/backup \
    alpine tar -czf /backup/ollama_backup.tar.gz -C /data .
```

### Recovery
```bash
# Restore volumes
docker run --rm -v ollama_data:/data -v $(pwd):/backup \
    alpine tar -xzf /backup/ollama_backup.tar.gz -C /data

# Restart services
docker-compose restart
```

## 📋 Quick Commands Reference

```bash
# Essential Commands
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose logs -f            # Follow logs
docker-compose ps                 # Check status
docker-compose restart <service>  # Restart service

# Model Management
docker-compose exec ollama ollama pull llama3.1:8b
docker-compose exec ollama ollama list

# Health Checks
curl http://localhost:8003/health
curl http://localhost:8080

# Cleanup
docker system prune -a           # Clean unused containers/images
docker volume prune              # Clean unused volumes
```

## 🔗 Related Documentation

- **[Startup Guide](./STARTUP_GUIDE.md)** - Basic setup and testing
- **[Model Integration Guide](./MODEL_INTEGRATION.md)** - AI model configuration  
- **[Migration Guide](./MIGRATION_GUIDE.md)** - Moving environments
- **[OpenWebUI Setup](./OPENWEBUI_SETUP.md)** - Model management

---

*Docker deployment provides a consistent, scalable environment for your Novel Knowledge Fusion Platform across all environments.*
