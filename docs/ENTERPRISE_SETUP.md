# 🏢 Enterprise Setup Guide (IBM/Corporate Environments)

## Quick Start for Corporate Environments

### One-Command Setup
```bash
git clone https://github.com/jidemobell/knowledgebase.git
cd knowledgebase
./setup.sh --https
./start.sh
```

### Why This Approach?

#### 🔐 Enterprise Security Compliance
- **HTTPS URLs**: Works with corporate firewalls and proxy servers
- **No SSH Keys Required**: Bypasses SSH key management complexity
- **Proxy Friendly**: Works through corporate HTTP/HTTPS proxies

#### 🎯 Automatic Fallback System
The `setup.sh` script intelligently handles different environments:

```bash
# Auto-detection (recommended)
./setup.sh              # Tries SSH first, falls back to HTTPS

# Force HTTPS (for enterprise)
./setup.sh --https      # Always uses HTTPS URLs

# Force SSH (for development)
./setup.sh --ssh        # Always uses SSH URLs
```

## Common Enterprise Issues & Solutions

### Issue: "Permission denied (publickey)"
**Solution**: Use HTTPS mode
```bash
./setup.sh --https
```

### Issue: "Submodule openwebuibase is empty"
**Solution**: Run the setup script
```bash
./setup.sh
```

### Issue: "Connection timeout"
**Solution**: Configure proxy (if needed)
```bash
git config --global http.proxy http://proxy.company.com:8080
git config --global https.proxy https://proxy.company.com:8080
./setup.sh --https
```

### Issue: "SSL certificate problem"
**Solution**: Configure certificates (consult IT)
```bash
git config --global http.sslVerify false  # Temporary - not recommended
# Better: Configure proper certificates with IT team
```

## Container Runtime Support

### Docker vs Podman
The platform automatically detects and supports both:

```bash
# Works with Docker
./start_docker_mode.sh

# Also works with Podman (common in IBM/Red Hat environments)
./start_docker_mode.sh  # Auto-detects Podman
```

### Why This Matters for Enterprise:
- **Podman**: Rootless containers, better security compliance
- **Docker**: Established in many dev workflows
- **Auto-detection**: No configuration needed

## Team Collaboration

### For Team Leads
Share this setup with your team:
```bash
# Standard setup for team members
git clone https://github.com/jidemobell/knowledgebase.git
cd knowledgebase
./setup.sh --https  # Use --https for enterprise environments
./start.sh
```

### For CI/CD Pipelines
```yaml
# GitHub Actions example
- name: Setup repository
  run: |
    git submodule update --init --recursive
    ./setup.sh --https
```

## Network Configuration

### Corporate Proxy Setup
If your organization uses HTTP proxies:

```bash
# Set git proxy configuration
git config --global http.proxy http://proxy.company.com:8080
git config --global https.proxy https://proxy.company.com:8080

# For npm (if using Node.js components)
npm config set proxy http://proxy.company.com:8080
npm config set https-proxy https://proxy.company.com:8080

# For pip (Python packages)
pip config set global.proxy http://proxy.company.com:8080
```

### Firewall Considerations
Ensure these ports are accessible:
- **Port 443**: HTTPS to GitHub
- **Port 11434**: Ollama API (local)
- **Port 3000**: OpenWebUI interface
- **Port 8001**: Core Backend API
- **Port 8002**: Knowledge Fusion API

## Security Best Practices

### Repository Access
- Uses HTTPS for better corporate compliance
- No SSH keys required on corporate machines
- Respects corporate proxy and certificate policies

### Container Security
- Podman support for rootless containers
- Isolated environments prevent conflicts
- Clear separation of development and production

### Data Privacy
- All processing can be done locally
- No external API calls required (when using local models)
- Knowledge Fusion operates within your environment

## Troubleshooting

### Common Commands
```bash
# Check repository status
git status
git submodule status

# Reset to clean state
git submodule update --init --recursive --force

# Verify setup
./setup.sh
ls -la openwebuibase/knowledge-fusion/  # Should show files
```

### Support
- Check the main README.md for complete documentation
- Review docs/GIT_SUBMODULE_GUIDE.md for advanced git operations
- Use `./start.sh` and choose option 3 for system status check

---

**💡 Pro Tip**: Bookmark this setup command for your team:
```bash
git clone https://github.com/jidemobell/knowledgebase.git && cd knowledgebase && ./setup.sh --https && ./start.sh
```
