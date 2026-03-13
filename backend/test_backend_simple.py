"""
Simple test backend without API dependencies
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="AMAW MVP Backend - Simple Test",
    description="Simple test version without API dependencies",
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
        "message": "AMAW MVP Backend - Simple Test Mode",
        "status": "running",
        "database": "not connected",
        "ai": "mock mode"
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

@app.post("/api/ai/process")
async def mock_ai_process(request: dict):
    """Mock AI processing endpoint"""
    return {
        "success": True,
        "response": "This is a mock AI response. The backend is working, but you need to add your API keys to the .env file to enable real AI processing.",
        "content_type": "mock",
        "nodes_processed": 1,
        "processed_at": "2024-01-01T00:00:00"
    }

@app.get("/api/ai/health")
async def ai_health():
    """AI service health check"""
    return {
        "status": "mock",
        "service": "AI Processing",
        "message": "Mock mode - add API keys to .env for real processing"
    }

if __name__ == "__main__":
    print("Starting AMAW MVP Backend - Simple Test Mode...")
    print("API Documentation: http://localhost:8001/docs")
    print("Test Endpoints: http://localhost:8001/test/youtube")
    print("Mock AI Endpoint: http://localhost:8001/api/ai/process")
    
    uvicorn.run(
        "test_backend_simple:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
