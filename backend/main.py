"""
AMAW MVP Backend - FastAPI Application
Agentic Multimodal AI Workspace
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from app.api import youtube, ai, nodes, grounded_search, multi_gen

# Create FastAPI app
app = FastAPI(
    title="AMAW MVP Backend",
    description="Agentic Multimodal AI Workspace - Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(youtube.router, prefix="/api/youtube", tags=["YouTube"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(nodes.router, prefix="/api/nodes", tags=["Nodes"])
app.include_router(grounded_search.router, prefix="/api/grounded-search", tags=["Grounded Search"])
app.include_router(multi_gen.router, prefix="/api/multi-gen", tags=["Multi-Gen"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AMAW MVP Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AMAW MVP Backend"}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
