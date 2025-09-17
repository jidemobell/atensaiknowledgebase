#!/usr/bin/env python3
"""
Knowledge Fusion Web Server Startup Script
Runs the Knowledge Fusion web server on port 8002
"""

import uvicorn
import sys
import os

# Add the enhanced_backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'enhanced_backend'))

from main_novel_architecture import app

if __name__ == "__main__":
    print("🚀 Starting Knowledge Fusion Web Server on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
