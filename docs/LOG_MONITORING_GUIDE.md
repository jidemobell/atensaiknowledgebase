# 🔍 Topology Knowledge - Log Monitoring Guide

This guide covers the comprehensive logging tools available for monitoring all services in the Topology Knowledge platform.

## 📋 Available Log Viewers

### 1. Shell-based Log Viewer (`view_logs.sh`)
A command-line tool for quick log access and monitoring.

### 2. Web-based Log Viewer (`web_logs.py`)
A browser-based interface for real-time log monitoring with advanced features.

---

## 🖥️ Shell Log Viewer (`./view_logs.sh`)

### Quick Start
```bash
# View recent logs from all services
./view_logs.sh

# Show log file sizes
./view_logs.sh --size

# Follow logs in real-time
./view_logs.sh --follow

# View logs from specific service
./view_logs.sh --service OpenWebUI

# Show only errors
./view_logs.sh --errors
```

### All Options
- `-f, --follow` - Follow logs in real-time (like tail -f)
- `-s, --service NAME` - Show logs from specific service only
- `-g, --grep PATTERN` - Filter logs containing pattern
- `-e, --errors` - Show only error messages
- `-w, --warnings` - Show warnings and errors
- `-l, --lines N` - Show last N lines from each log (default: 50)
- `-c, --clear` - Clear all log files
- `-z, --size` - Show log file sizes
- `-h, --help` - Show help message

### Available Services
- `CoreBackend` - Core Backend service logs
- `OpenWebUI` - OpenWebUI interface logs
- `KnowledgeFusion` - Knowledge Fusion service logs
- `Ollama` - Ollama LLM service logs
- `System` - System-wide logs

### Examples
```bash
# View last 100 lines from all services
./view_logs.sh --lines 100

# Follow only Knowledge Fusion logs
./view_logs.sh --service KnowledgeFusion --follow

# Search for specific patterns
./view_logs.sh --grep "startup"
./view_logs.sh --grep "error" --service CoreBackend

# Monitor warnings and errors in real-time
./view_logs.sh --warnings --follow

# Clear all logs (be careful!)
./view_logs.sh --clear
```

---

## 🌐 Web Log Viewer (`python web_logs.py`)

### Quick Start
```bash
# Start web log viewer on default port (9000)
python web_logs.py

# Start on custom host/port
python web_logs.py --host 0.0.0.0 --port 8888

# Enable debug mode
python web_logs.py --debug
```

### Access URL
- **Default**: http://localhost:9000
- **Custom**: http://[host]:[port]

### Web Interface Features

#### 🎛️ Controls
- **Service Filter**: Show logs from specific service or all services
- **Level Filter**: Filter by log level (All, Errors Only, Warnings & Errors, Info & Above)
- **Text Filter**: Search logs with text pattern
- **Auto Scroll**: Automatically scroll to new log entries
- **Clear**: Clear the current view (doesn't delete log files)
- **Pause**: Pause real-time log updates

#### 📊 Dashboard Features
- **Real-time Updates**: Logs update every second automatically
- **Service Statistics**: Shows total logs, errors, and warnings per service
- **Color-coded Services**: Each service has a unique color for easy identification
- **Responsive Design**: Works on desktop and mobile devices
- **Log Levels**: Automatic detection of Error, Warning, and Info levels

#### 🎨 Visual Features
- **Dark Theme**: Easy on the eyes for long monitoring sessions
- **Syntax Highlighting**: Different colors for different services
- **Timestamp Display**: Shows when each log entry occurred
- **Hover Effects**: Interactive log entries with hover highlighting
- **Status Indicators**: Live connection status and entry count

### Web Interface Navigation
1. **Open browser** to the web interface URL
2. **Select filters** using the dropdown menus and text input
3. **Monitor in real-time** with auto-scroll enabled
4. **Search patterns** using the filter text box
5. **Focus on specific services** using the service dropdown
6. **Pause updates** when you need to review specific entries

---

## 📁 Log File Locations

All log files are stored in the `logs/` directory:

```
logs/
├── core_backend.log      # Core Backend service
├── openwebui.log        # OpenWebUI interface  
├── knowledge_fusion.log # Knowledge Fusion service
├── ollama.log          # Ollama LLM service
└── system.log          # System-wide logs
```

---

## 🛠️ Advanced Usage

### Integration with Platform Services

The log viewers automatically detect and monitor logs from:
- **Core Backend** (port 8001) - API and business logic
- **OpenWebUI** (port 3000) - Web interface
- **Knowledge Fusion** (port 8002) - AI integration service
- **Ollama** (port 11434) - Local LLM service
- **System** - Platform-wide system logs

### Real-time Monitoring Workflow

1. **Start the platform** using `./start_server_mode.sh`
2. **Open log monitoring**:
   - For quick checks: `./view_logs.sh --follow`
   - For detailed analysis: `python web_logs.py` then open browser
3. **Monitor startup** for any errors or warnings
4. **Filter specific issues** using the pattern search
5. **Debug problems** by focusing on specific services

### Troubleshooting Common Issues

#### Service Not Starting
```bash
# Check specific service logs
./view_logs.sh --service CoreBackend --errors
./view_logs.sh --service KnowledgeFusion --errors
```

#### Performance Issues
```bash
# Monitor all services for warnings
./view_logs.sh --warnings --follow
```

#### Connection Problems
```bash
# Search for connection-related logs
./view_logs.sh --grep "connection"
./view_logs.sh --grep "port"
```

---

## 🔧 Installation Requirements

### Shell Log Viewer
- **Requirements**: Bash shell (included in macOS/Linux)
- **Optional**: `multitail` for enhanced multiple file viewing
  ```bash
  # Install multitail for better following
  brew install multitail  # macOS
  apt-get install multitail  # Ubuntu/Debian
  ```

### Web Log Viewer
- **Requirements**: Python 3.6+ and Flask
  ```bash
  pip install flask
  ```

---

## 📝 Log Analysis Tips

### Identifying Issues
- **Red entries**: Usually errors or critical issues
- **Yellow entries**: Warnings that may need attention
- **Blue entries**: Informational messages
- **Timestamps**: Help correlate issues across services

### Common Log Patterns
- `ERROR` / `Exception` - Critical issues requiring attention
- `WARNING` / `WARN` - Potential issues to monitor
- `INFO` - Normal operational messages
- `DEBUG` - Detailed troubleshooting information
- `startup` / `shutdown` - Service lifecycle events
- `connection` / `port` - Network and connectivity issues

### Best Practices
1. **Monitor during startup** to catch initialization issues
2. **Use real-time following** during active debugging
3. **Filter by service** when troubleshooting specific components
4. **Search for patterns** when looking for specific issues
5. **Clear logs periodically** to manage disk space (use with caution)

---

## 🚀 Integration with Development

### During Development
```bash
# Follow logs while developing
./view_logs.sh --follow &

# Monitor specific service you're working on
./view_logs.sh --service KnowledgeFusion --follow
```

### For Production Monitoring
```bash
# Start web interface for team monitoring
python web_logs.py --host 0.0.0.0 --port 9000

# Set up log rotation and monitoring alerts based on error patterns
./view_logs.sh --errors | grep "CRITICAL"
```

### Debugging Workflow
1. **Reproduce the issue** while monitoring logs
2. **Identify the relevant service** where the error occurs
3. **Filter logs** to focus on the timeframe of the issue
4. **Search for error patterns** to understand the root cause
5. **Check related services** for cascading effects

---

This comprehensive logging system ensures you have full visibility into the Topology Knowledge platform's operation, making debugging and monitoring much more efficient!
