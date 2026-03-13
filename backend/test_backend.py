"""
Test backend without database dependencies
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv('.env')  # Look for .env in the backend directory

# Debug: Check if API key is loaded
gemini_key = os.getenv('GEMINI_API_KEY')
print(f"GEMINI_API_KEY loaded: {'Yes' if gemini_key else 'No'}")
if gemini_key:
    print(f"API Key length: {len(gemini_key)} characters")

from app.api import youtube_simple as youtube, ai

# Create FastAPI app
app = FastAPI(
    title="AMAW MVP Backend - Test",
    description="Test version without database",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "AMAW MVP Backend - Test Mode",
        "status": "running",
        "database": "not connected"
    }

@app.get("/test/youtube")
async def test_youtube():
    return {
        "message": "YouTube API test endpoint",
        "status": "ready"
    }

@app.get("/test/ai")
async def test_ai():
    return {
        "message": "AI API test endpoint", 
        "status": "ready"
    }

@app.get("/api/ai/health")
async def ai_health():
    """AI service health check"""
    try:
        # Test Gemini API connection
        from app.services.gemini_service import gemini_service
        if gemini_service.mock_mode:
            return {
                "status": "mock",
                "service": "AI Processing",
                "message": "Mock mode - API key not found or invalid"
            }
        else:
            test_response = await gemini_service._generate_response("Hello, this is a test.")
            return {
                "status": "healthy",
                "service": "AI Processing",
                "gemini_api": "connected",
                "test_response": test_response[:50] + "..." if len(test_response) > 50 else test_response
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "AI Processing",
            "error": str(e)
        }

# Include API routers
app.include_router(youtube.router)
app.include_router(ai.router)

if __name__ == "__main__":
    print("Starting AMAW MVP Backend - Test Mode...")
    print("API Documentation: http://localhost:8001/docs")
    print("Test Endpoints: http://localhost:8001/test/youtube")
    
    uvicorn.run(
        "test_backend:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
