#!/usr/bin/env python3
"""
Restart the AMAW Backend Server
This script stops any running server and starts a fresh one.
"""

import subprocess
import sys
import time
import os
import signal
import psutil

def kill_existing_servers():
    """Kill any existing Python processes running on port 8001"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'main.py' in cmdline or 'uvicorn' in cmdline:
                        print(f"Killing existing server process: {proc.info['pid']}")
                        proc.kill()
                        time.sleep(1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"Error killing processes: {e}")

def start_server():
    """Start the FastAPI server"""
    try:
        print("Starting AMAW Backend Server...")
        print("Server will be available at: http://localhost:8001")
        print("API Documentation: http://localhost:8001/docs")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8001", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    print("🔄 Restarting AMAW Backend Server")
    print("=" * 50)
    
    # Kill existing servers
    kill_existing_servers()
    
    # Wait a moment
    time.sleep(2)
    
    # Start new server
    start_server()
