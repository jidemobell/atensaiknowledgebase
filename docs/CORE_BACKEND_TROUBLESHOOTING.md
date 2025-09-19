# Core Backend API Troubleshooting Guide

## Issue: "Failed to load API definition" with "fetch error internal server Error /openapi.json"

### Quick Diagnosis

Run this command on your second computer:
```bash
./bin/diagnose_core_backend.sh
```

### Common Causes & Solutions

#### 1. Core Backend Not Running
**Symptoms:** 
- Connection refused errors
- No process listening on port 8001

**Solution:**
```bash
# Start the platform
./bin/start_server_mode.sh

# Check if it's running
curl http://localhost:8001/health
```

#### 2. Port Conflicts
**Symptoms:** 
- Different service running on port 8001
- Unexpected responses

**Solution:**
```bash
# Check what's on port 8001
lsof -i :8001

# If wrong service, kill it and restart
./bin/start_server_mode.sh
```

#### 3. Network Configuration Issues
**Symptoms:** 
- Can't reach localhost:8001
- Timeouts

**Solution:**
```bash
# Test basic connectivity
ping localhost
nc -z localhost 8001

# Check firewall settings
```

#### 4. Incomplete Startup
**Symptoms:** 
- Health endpoint works but OpenAPI fails
- Some endpoints work, others don't

**Solution:**
```bash
# Check logs for errors
./bin/view_logs.sh

# Restart the platform
./bin/start_server_mode.sh
```

#### 5. Browser Cache Issues
**Symptoms:** 
- Works in one browser but not another
- Inconsistent behavior

**Solution:**
- Clear browser cache
- Try incognito/private window
- Try different browser

### Manual Testing Commands

Test these endpoints individually:

```bash
# 1. Health check (should return JSON)
curl http://localhost:8001/health

# 2. OpenAPI spec (should return large JSON)
curl http://localhost:8001/openapi.json

# 3. Documentation page (should return HTML)
curl http://localhost:8001/docs

# 4. Status endpoint (should return system info)
curl http://localhost:8001/status
```

### Expected Responses

1. **Health endpoint** should return:
```json
{"status":"healthy","timestamp":"...","version":"2.0.0"}
```

2. **OpenAPI endpoint** should return large JSON starting with:
```json
{"openapi":"3.1.0","info":{"title":"Enhanced AI-Powered Support System"...
```

3. **Docs endpoint** should return HTML with Swagger UI

### If All Else Fails

1. **Restart everything:**
```bash
# Kill all processes
pkill -f "uvicorn\|python.*8001"

# Wait a moment
sleep 5

# Start fresh
./bin/start_server_mode.sh
```

2. **Check Python environment:**
```bash
# Verify Python is working
python3 --version

# Check if uvicorn is installed
python3 -m uvicorn --version
```

3. **Check project structure:**
```bash
# Make sure you're in the right directory
pwd
ls -la

# Check if required files exist
ls -la corebackend/implementation/backend/
```

### Getting Help

If the diagnostic script shows all green checkmarks but you still have issues:

1. Compare the diagnostic output between your working and non-working computers
2. Check if there are any differences in:
   - Python versions
   - Network configurations
   - Firewall settings
   - Browser versions

3. Share the diagnostic script output for further troubleshooting