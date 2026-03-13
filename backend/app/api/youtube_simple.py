"""
Simplified YouTube API endpoints for test backend
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.youtube_service import youtube_service
from datetime import datetime

router = APIRouter(prefix="/api/youtube", tags=["YouTube"])

class YouTubeURLRequest(BaseModel):
    """Request model for YouTube URL processing"""
    url: str

class YouTubeResponse(BaseModel):
    """Response model for YouTube processing"""
    success: bool
    data: Dict[str, Any] = None
    error: str = None

@router.post("/extract", response_model=YouTubeResponse)
async def extract_youtube_content(request: YouTubeURLRequest):
    """Extract content from YouTube URL"""
    try:
        result = await youtube_service.process_youtube_url(request.url)
        return YouTubeResponse(
            success=True,
            data=result
        )
    except Exception as e:
        return YouTubeResponse(
            success=False,
            error=str(e)
        )

@router.get("/video/{video_id}")
async def get_video_info(video_id: str):
    """Get video information by ID"""
    try:
        video_data = await youtube_service.get_video_info(video_id)
        return {
            "success": True,
            "data": video_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate")
async def validate_youtube_url(request: YouTubeURLRequest):
    """Validate YouTube URL"""
    try:
        video_id = youtube_service.extract_video_id(request.url)
        if video_id:
            return {
                "success": True,
                "video_id": video_id,
                "valid": True
            }
        else:
            return {
                "success": False,
                "valid": False,
                "error": "Invalid YouTube URL"
            }
    except Exception as e:
        return {
            "success": False,
            "valid": False,
            "error": str(e)
        }
