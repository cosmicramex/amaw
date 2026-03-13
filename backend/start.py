"""
Startup script for AMAW MVP Backend
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("🚀 Starting AMAW MVP Backend...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔧 Redoc Documentation: http://localhost:8000/redoc")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
