"""
YouTube API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any
from app.database.connection import get_db
from app.services.youtube_service import youtube_service
from app.models.database import Content, Node
from datetime import datetime

router = APIRouter()

class YouTubeURLRequest(BaseModel):
    """Request model for YouTube URL processing"""
    url: str
    node_id: str

class YouTubeResponse(BaseModel):
    """Response model for YouTube content"""
    success: bool
    data: Dict[str, Any]
    message: str

@router.post("/extract", response_model=YouTubeResponse)
async def extract_youtube_content(
    request: YouTubeURLRequest,
    db: Session = Depends(get_db)
):
    """Extract content from YouTube URL"""
    try:
        # Process YouTube URL
        video_data = await youtube_service.process_youtube_url(request.url)
        
        # Save content to database
        content = Content(
            node_id=request.node_id,
            source_url=request.url,
            platform="youtube",
            title=video_data["title"],
            description=video_data["description"],
            thumbnail_url=video_data["thumbnail_url"],
            metadata=video_data,
            content_text=video_data["transcript"]
        )
        
        db.add(content)
        db.commit()
        db.refresh(content)
        
        return YouTubeResponse(
            success=True,
            data=video_data,
            message="YouTube content extracted successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
async def validate_youtube_url(request: dict):
    """Validate YouTube URL"""
    try:
        url = request.get("url", "")
        video_id = youtube_service.extract_video_id(url)
        
        if video_id:
            return {
                "success": True,
                "valid": True,
                "video_id": video_id
            }
        else:
            return {
                "success": True,
                "valid": False,
                "message": "Invalid YouTube URL"
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
