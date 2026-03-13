"""
Grounded Search API endpoints
Provides web search capabilities with citation handling
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio

from app.services.grounded_search_service import grounded_search_service

router = APIRouter(tags=["grounded-search"])


class GroundedSearchRequest(BaseModel):
    """Request model for grounded search"""
    query: str
    youtube_context: Optional[Dict[str, Any]] = None
    num_results: int = 5


class GroundedSearchResponse(BaseModel):
    """Response model for grounded search"""
    success: bool
    query: str
    enhanced_query: Optional[str] = None
    ai_response: Optional[str] = None
    citations: Optional[List[str]] = None
    sources: Optional[List[Dict[str, Any]]] = None
    search_results: Optional[List[Dict[str, Any]]] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None


@router.post("/search", response_model=GroundedSearchResponse)
async def perform_grounded_search(request: GroundedSearchRequest):
    """
    Perform a grounded search with citation handling
    
    This endpoint:
    1. Enhances the user query with YouTube video context
    2. Performs web search using Google Custom Search API
    3. Processes results with OpenAI to generate a comprehensive response
    4. Returns structured response with proper citations and references
    """
    try:
        # Validate request
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if request.num_results < 1 or request.num_results > 10:
            raise HTTPException(status_code=400, detail="Number of results must be between 1 and 10")
        
        # Perform grounded search
        result = await grounded_search_service.perform_grounded_search(
            query=request.query,
            youtube_context=request.youtube_context,
            num_results=request.num_results
        )
        
        return GroundedSearchResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in grounded search endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for grounded search service"""
    try:
        # Check if Google Search API is configured
        has_search_api = grounded_search_service.search_service is not None
        
        return {
            "status": "healthy",
            "google_search_configured": has_search_api,
            "gpt_service_available": grounded_search_service.gpt_service is not None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/test-search")
async def test_grounded_search():
    """Test endpoint for grounded search functionality"""
    try:
        # Test with a simple query
        test_query = "artificial intelligence trends 2024"
        test_youtube_context = {
            "title": "AI Revolution 2024",
            "channel": "TechChannel",
            "description": "Exploring the latest trends in artificial intelligence"
        }
        
        result = await grounded_search_service.perform_grounded_search(
            query=test_query,
            youtube_context=test_youtube_context,
            num_results=3
        )
        
        return {
            "test_status": "success",
            "result": result
        }
        
    except Exception as e:
        return {
            "test_status": "failed",
            "error": str(e)
        }
