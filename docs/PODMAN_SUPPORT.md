# 🐳 Container Runtime Support: Docker & Podman

## Overview

The Topology Knowledge Platform provides seamless support for both **Docker** and **Podman** container runtimes. This is particularly valuable for enterprise environments like IBM where Podman is often preferred over Docker.

## How It Works

### Automatic Detection
Our `start_docker_mode.sh` script automatically detects your available container runtime:

1. **Podman Detection**: First checks for `podman` command and running daemon
2. **Docker Fallback**: Falls back to `docker` if Podman isn't available
3. **Compose Tool Selection**: Chooses appropriate compose tool (`podman-compose` or `docker-compose`)

### Runtime Priority
```bash
1. Podman + podman-compose (if available)
2. Podman + docker-compose (compatibility mode)
3. Docker + docker-compose (standard mode)
```

## Enterprise Environments

### IBM & Red Hat Environments
- **Podman** is often the preferred container runtime
- **Security-first** approach with rootless containers by default
- **OCI Compliance** ensuring compatibility with Docker images
- **Enterprise Support** with established security policies

### Migration Benefits
- **Zero Configuration**: Existing Docker setups work unchanged
- **Gradual Migration**: Can switch runtimes without rebuilding images
- **Policy Compliance**: Meets enterprise security requirements

## Technical Details

### Container Runtime Variables
```bash
CONTAINER_RUNTIME="docker|podman"    # Detected runtime
COMPOSE_COMMAND="docker-compose|podman-compose"  # Compose tool
```

### Image Compatibility
All our container images are **OCI-compliant** and work identically with both runtimes:
- `topology-openwebui:latest`
- `topology-corebackend:latest`
- `topology-knowledge-fusion:latest`

### Command Translation
The script automatically translates commands:
```bash
# What you see
$COMPOSE_COMMAND -f docker-compose.yml up -d

# Podman execution
podman-compose -f docker-compose.yml up -d

# Docker execution  
docker-compose -f docker-compose.yml up -d
```

## Setup Requirements

### For Podman Users
```bash
# Install Podman (if not already installed)
# On macOS
brew install podman

# On RHEL/CentOS/Fedora
sudo dnf install podman

# On Ubuntu/Debian
sudo apt install podman

# Install podman-compose (auto-installed by our script if missing)
pip3 install podman-compose
```

### For Docker Users
```bash
# Standard Docker installation
# See: https://docs.docker.com/get-docker/
```

## Security Considerations

### Podman Advantages
- **Rootless Containers**: Run without root privileges by default
- **No Daemon**: Direct interaction with container runtime
- **Pod Support**: Kubernetes-style pod management
- **Security Profiles**: SELinux and other security framework integration

### Docker Compatibility
- **Established Ecosystem**: Broad tool and service support
- **Development Familiarity**: Widespread developer knowledge
- **CI/CD Integration**: Extensive pipeline tool support

## Best Practices

### Development Environment
- Use **Server Mode** (`./start_server_mode.sh`) for development
- Container mode for integration testing

### Production Deployment
- Use **Containerized Mode** (`./start_docker_mode.sh`) for production
- Let the system auto-detect your preferred runtime
- Ensure consistent runtime across cluster nodes

### Enterprise Policies
- Verify your organization's container runtime policy
- Podman often preferred for compliance and security
- Docker may be required for specific CI/CD pipelines

## Troubleshooting

### Podman Issues
```bash
# Check Podman installation
podman --version
podman info

# Start Podman machine (macOS/Windows)
podman machine start

# Check for compose tool
which podman-compose || pip3 install podman-compose
```

### Docker Issues
```bash
# Check Docker installation
docker --version
docker info

# Start Docker daemon
sudo systemctl start docker  # Linux
# or start Docker Desktop   # macOS/Windows
```

### Mixed Environment Issues
```bash
# Force specific runtime (if needed)
export CONTAINER_RUNTIME="podman"  # or "docker"
./start_docker_mode.sh
```

## Enterprise Integration Examples

### IBM Cloud Deployment
```bash
# Works seamlessly with IBM Cloud Container Service
# Both Docker and Podman images supported
```

### Red Hat OpenShift
```bash
# Podman images work directly with OpenShift
# No modification needed for deployment
```

### Standard Kubernetes
```bash
# OCI-compliant images work with any Kubernetes distribution
# Runtime choice independent of deployment platform
```

---

**💡 The beauty of this approach**: You never need to think about which container runtime you're using. The platform adapts to your environment automatically, whether you're in a Docker-first development setup or a Podman-first enterprise environment.
