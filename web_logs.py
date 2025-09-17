#!/usr/bin/env python3
"""
Topology Knowledge - Web-based Global Log Viewer
A simple web interface for viewing and monitoring all service logs
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
import threading
from flask import Flask, render_template_string, jsonify, request
import argparse

app = Flask(__name__)

# Configuration
PROJECT_ROOT = Path(__file__).parent
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log files to monitor
LOG_FILES = {
    "CoreBackend": LOGS_DIR / "core_backend.log",
    "OpenWebUI": LOGS_DIR / "openwebui.log", 
    "KnowledgeFusion": LOGS_DIR / "knowledge_fusion.log",
    "Ollama": LOGS_DIR / "ollama.log",
    "System": LOGS_DIR / "system.log"
}

# Service colors for web interface
SERVICE_COLORS = {
    "CoreBackend": "#2196F3",     # Blue
    "OpenWebUI": "#4CAF50",       # Green
    "KnowledgeFusion": "#9C27B0", # Purple
    "Ollama": "#00BCD4",          # Cyan
    "System": "#FF9800"           # Orange
}

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 Topology Knowledge - Global Log Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            background: #1e1e1e;
            color: #ffffff;
            line-height: 1.4;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            margin: 0;
            font-size: 24px;
            font-weight: 300;
        }
        
        .controls {
            background: #2d2d2d;
            padding: 15px;
            border-bottom: 1px solid #404040;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
        }
        
        .control-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .control-group label {
            font-size: 12px;
            color: #cccccc;
        }
        
        select, input[type="text"], button {
            background: #404040;
            border: 1px solid #555555;
            color: #ffffff;
            padding: 6px 12px;
            border-radius: 4px;
            font-family: inherit;
            font-size: 12px;
        }
        
        button {
            background: #4CAF50;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        button:hover {
            background: #45a049;
        }
        
        button.active {
            background: #2196F3;
        }
        
        .status {
            display: flex;
            gap: 20px;
            align-items: center;
            margin-left: auto;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 12px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4CAF50;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .log-container {
            height: calc(100vh - 140px);
            overflow-y: auto;
            padding: 15px;
            background: #1e1e1e;
        }
        
        .log-entry {
            margin-bottom: 2px;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 13px;
            word-wrap: break-word;
            border-left: 3px solid transparent;
        }
        
        .log-entry:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        .log-timestamp {
            color: #888888;
            margin-right: 8px;
        }
        
        .log-service {
            font-weight: bold;
            margin-right: 8px;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
        }
        
        .log-message {
            color: #ffffff;
        }
        
        .log-error {
            background: rgba(244, 67, 54, 0.1);
            border-left-color: #f44336;
        }
        
        .log-warning {
            background: rgba(255, 152, 0, 0.1);
            border-left-color: #ff9800;
        }
        
        .log-info {
            background: rgba(33, 150, 243, 0.1);
            border-left-color: #2196F3;
        }
        
        .service-stats {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .stat-card {
            background: #2d2d2d;
            padding: 10px 15px;
            border-radius: 6px;
            border-left: 4px solid;
            min-width: 120px;
        }
        
        .stat-title {
            font-size: 11px;
            color: #cccccc;
            margin-bottom: 4px;
        }
        
        .stat-value {
            font-size: 16px;
            font-weight: bold;
        }
        
        .auto-scroll-indicator {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(76, 175, 80, 0.9);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .auto-scroll-indicator.visible {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Topology Knowledge - Global Log Viewer</h1>
    </div>
    
    <div class="controls">
        <div class="control-group">
            <label>Service:</label>
            <select id="serviceFilter">
                <option value="">All Services</option>
                <option value="CoreBackend">Core Backend</option>
                <option value="OpenWebUI">OpenWebUI</option>
                <option value="KnowledgeFusion">Knowledge Fusion</option>
                <option value="Ollama">Ollama</option>
                <option value="System">System</option>
            </select>
        </div>
        
        <div class="control-group">
            <label>Level:</label>
            <select id="levelFilter">
                <option value="">All Levels</option>
                <option value="error">Errors Only</option>
                <option value="warning">Warnings & Errors</option>
                <option value="info">Info & Above</option>
            </select>
        </div>
        
        <div class="control-group">
            <label>Filter:</label>
            <input type="text" id="textFilter" placeholder="Search logs...">
        </div>
        
        <div class="control-group">
            <button id="autoScrollBtn" class="active">Auto Scroll</button>
            <button id="clearBtn">Clear</button>
            <button id="pauseBtn">Pause</button>
        </div>
        
        <div class="status">
            <div class="status-item">
                <div class="status-dot"></div>
                <span>Live</span>
            </div>
            <div class="status-item">
                <span id="logCount">0 entries</span>
            </div>
        </div>
    </div>
    
    <div class="log-container" id="logContainer">
        <div class="service-stats" id="serviceStats"></div>
        <div id="logEntries"></div>
    </div>
    
    <div class="auto-scroll-indicator" id="autoScrollIndicator">
        Auto-scrolling enabled
    </div>

    <script>
        class LogViewer {
            constructor() {
                this.logs = [];
                this.autoScroll = true;
                this.paused = false;
                this.filters = {
                    service: '',
                    level: '',
                    text: ''
                };
                this.serviceColors = {{ service_colors | safe }};
                this.lastLogTime = 0;
                
                this.initializeElements();
                this.bindEvents();
                this.startLogUpdates();
            }
            
            initializeElements() {
                this.serviceFilter = document.getElementById('serviceFilter');
                this.levelFilter = document.getElementById('levelFilter');
                this.textFilter = document.getElementById('textFilter');
                this.autoScrollBtn = document.getElementById('autoScrollBtn');
                this.clearBtn = document.getElementById('clearBtn');
                this.pauseBtn = document.getElementById('pauseBtn');
                this.logContainer = document.getElementById('logContainer');
                this.logEntries = document.getElementById('logEntries');
                this.logCount = document.getElementById('logCount');
                this.serviceStats = document.getElementById('serviceStats');
                this.autoScrollIndicator = document.getElementById('autoScrollIndicator');
            }
            
            bindEvents() {
                this.serviceFilter.addEventListener('change', () => {
                    this.filters.service = this.serviceFilter.value;
                    this.renderLogs();
                });
                
                this.levelFilter.addEventListener('change', () => {
                    this.filters.level = this.levelFilter.value;
                    this.renderLogs();
                });
                
                this.textFilter.addEventListener('input', () => {
                    this.filters.text = this.textFilter.value.toLowerCase();
                    this.renderLogs();
                });
                
                this.autoScrollBtn.addEventListener('click', () => {
                    this.autoScroll = !this.autoScroll;
                    this.autoScrollBtn.classList.toggle('active', this.autoScroll);
                    this.autoScrollBtn.textContent = this.autoScroll ? 'Auto Scroll' : 'Manual';
                    this.updateAutoScrollIndicator();
                });
                
                this.clearBtn.addEventListener('click', () => {
                    this.logs = [];
                    this.renderLogs();
                });
                
                this.pauseBtn.addEventListener('click', () => {
                    this.paused = !this.paused;
                    this.pauseBtn.textContent = this.paused ? 'Resume' : 'Pause';
                    this.pauseBtn.style.background = this.paused ? '#f44336' : '#4CAF50';
                });
                
                this.logContainer.addEventListener('scroll', () => {
                    const isAtBottom = this.logContainer.scrollTop + this.logContainer.clientHeight >= this.logContainer.scrollHeight - 5;
                    if (!isAtBottom && this.autoScroll) {
                        this.autoScroll = false;
                        this.autoScrollBtn.classList.remove('active');
                        this.autoScrollBtn.textContent = 'Manual';
                        this.updateAutoScrollIndicator();
                    }
                });
            }
            
            updateAutoScrollIndicator() {
                this.autoScrollIndicator.classList.toggle('visible', this.autoScroll);
            }
            
            async startLogUpdates() {
                while (true) {
                    if (!this.paused) {
                        await this.fetchLogs();
                    }
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
            }
            
            async fetchLogs() {
                try {
                    const response = await fetch(`/api/logs?since=${this.lastLogTime}`);
                    const data = await response.json();
                    
                    if (data.logs && data.logs.length > 0) {
                        this.logs.push(...data.logs);
                        this.lastLogTime = data.latest_time;
                        
                        // Keep only last 1000 logs to prevent memory issues
                        if (this.logs.length > 1000) {
                            this.logs = this.logs.slice(-1000);
                        }
                        
                        this.renderLogs();
                    }
                } catch (error) {
                    console.error('Failed to fetch logs:', error);
                }
            }
            
            filterLogs() {
                return this.logs.filter(log => {
                    if (this.filters.service && log.service !== this.filters.service) {
                        return false;
                    }
                    
                    if (this.filters.level) {
                        const logLevel = this.getLogLevel(log.message);
                        if (this.filters.level === 'error' && logLevel !== 'error') {
                            return false;
                        }
                        if (this.filters.level === 'warning' && !['error', 'warning'].includes(logLevel)) {
                            return false;
                        }
                    }
                    
                    if (this.filters.text && !log.message.toLowerCase().includes(this.filters.text)) {
                        return false;
                    }
                    
                    return true;
                });
            }
            
            getLogLevel(message) {
                const msg = message.toLowerCase();
                if (msg.includes('error') || msg.includes('exception') || msg.includes('failed') || msg.includes('fatal')) {
                    return 'error';
                }
                if (msg.includes('warn') || msg.includes('warning')) {
                    return 'warning';
                }
                return 'info';
            }
            
            renderLogs() {
                const filteredLogs = this.filterLogs();
                
                // Update stats
                this.renderServiceStats();
                
                // Update log count
                this.logCount.textContent = `${filteredLogs.length} entries`;
                
                // Render log entries
                this.logEntries.innerHTML = filteredLogs.map(log => {
                    const level = this.getLogLevel(log.message);
                    const color = this.serviceColors[log.service] || '#ffffff';
                    
                    return `
                        <div class="log-entry log-${level}">
                            <span class="log-timestamp">${new Date(log.timestamp * 1000).toLocaleTimeString()}</span>
                            <span class="log-service" style="background-color: ${color}; color: white;">
                                ${log.service}
                            </span>
                            <span class="log-message">${this.escapeHtml(log.message)}</span>
                        </div>
                    `;
                }).join('');
                
                // Auto scroll if enabled
                if (this.autoScroll) {
                    this.logContainer.scrollTop = this.logContainer.scrollHeight;
                }
            }
            
            renderServiceStats() {
                const stats = {};
                
                Object.keys(this.serviceColors).forEach(service => {
                    stats[service] = {
                        total: 0,
                        errors: 0,
                        warnings: 0
                    };
                });
                
                this.logs.forEach(log => {
                    if (stats[log.service]) {
                        stats[log.service].total++;
                        const level = this.getLogLevel(log.message);
                        if (level === 'error') stats[log.service].errors++;
                        if (level === 'warning') stats[log.service].warnings++;
                    }
                });
                
                this.serviceStats.innerHTML = Object.entries(stats).map(([service, data]) => {
                    const color = this.serviceColors[service];
                    return `
                        <div class="stat-card" style="border-left-color: ${color}">
                            <div class="stat-title">${service}</div>
                            <div class="stat-value" style="color: ${color}">
                                ${data.total} 
                                ${data.errors > 0 ? `<span style="color: #f44336">(${data.errors}E)</span>` : ''}
                                ${data.warnings > 0 ? `<span style="color: #ff9800">(${data.warnings}W)</span>` : ''}
                            </div>
                        </div>
                    `;
                }).join('');
            }
            
            escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
        }
        
        // Initialize the log viewer when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new LogViewer();
        });
    </script>
</body>
</html>
"""

def get_log_level(message):
    """Determine log level from message content"""
    msg = message.lower()
    if any(keyword in msg for keyword in ['error', 'exception', 'failed', 'fatal']):
        return 'error'
    elif any(keyword in msg for keyword in ['warn', 'warning']):
        return 'warning'
    else:
        return 'info'

def read_log_file(file_path, since_time=0):
    """Read log entries from a file since given timestamp"""
    logs = []
    
    if not file_path.exists():
        return logs
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Use file modification time as timestamp approximation
                timestamp = file_path.stat().st_mtime
                
                if timestamp > since_time:
                    logs.append({
                        'timestamp': timestamp,
                        'message': line,
                        'level': get_log_level(line)
                    })
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return logs

@app.route('/')
def index():
    """Main log viewer page"""
    return render_template_string(HTML_TEMPLATE, service_colors=json.dumps(SERVICE_COLORS))

@app.route('/api/logs')
def api_logs():
    """API endpoint to fetch logs"""
    since_time = float(request.args.get('since', 0))
    
    all_logs = []
    latest_time = since_time
    
    for service, log_file in LOG_FILES.items():
        service_logs = read_log_file(log_file, since_time)
        
        # Add service information to each log entry
        for log in service_logs:
            log['service'] = service
            all_logs.append(log)
            latest_time = max(latest_time, log['timestamp'])
    
    # Sort logs by timestamp
    all_logs.sort(key=lambda x: x['timestamp'])
    
    return jsonify({
        'logs': all_logs,
        'latest_time': latest_time,
        'total_count': len(all_logs)
    })

@app.route('/api/stats')
def api_stats():
    """API endpoint for log statistics"""
    stats = {}
    
    for service, log_file in LOG_FILES.items():
        if log_file.exists():
            stats[service] = {
                'size': log_file.stat().st_size,
                'lines': sum(1 for _ in open(log_file, 'r', encoding='utf-8', errors='ignore')),
                'modified': log_file.stat().st_mtime
            }
        else:
            stats[service] = {
                'size': 0,
                'lines': 0,
                'modified': 0
            }
    
    return jsonify(stats)

def main():
    parser = argparse.ArgumentParser(description='Topology Knowledge Web Log Viewer')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=9000, help='Port to bind to (default: 9000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print(f"🔍 Starting Topology Knowledge Web Log Viewer")
    print(f"📱 Access at: http://{args.host}:{args.port}")
    print(f"📁 Monitoring logs in: {LOGS_DIR}")
    print(f"🔄 Press Ctrl+C to stop")
    
    try:
        app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Log viewer stopped")

if __name__ == '__main__':
    main()
