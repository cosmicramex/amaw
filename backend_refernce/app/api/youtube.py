"""
YouTube API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any
from app.database.connection import get_db
from app.services.youtube_service import get_youtube_service
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

@router.get("/video/{video_id}", response_model=YouTubeResponse)
async def get_youtube_video(video_id: str):
    """Get YouTube video data by ID"""
    try:
        # Process YouTube video ID
        service = get_youtube_service()
        video_data = await service.get_video_data(video_id)
        
        return YouTubeResponse(
            success=True,
            data=video_data,
            message="Video data retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get video data: {str(e)}")

@router.post("/extract", response_model=YouTubeResponse)
async def extract_youtube_content(
    request: YouTubeURLRequest,
    db: Session = Depends(get_db)
):
    """Extract content from YouTube URL"""
    try:
        # Process YouTube URL
        service = get_youtube_service()
        video_data = await service.process_youtube_url(request.url)
        
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
        print(f"API endpoint called with video_id: {video_id}")
        service = get_youtube_service()
        print(f"Service obtained: {service}")
        print(f"Service type: {type(service)}")
        print(f"Service has get_video_data: {hasattr(service, 'get_video_data')}")
        video_data = await service.get_video_data(video_id)  # Use get_video_data instead
        print(f"Video data obtained: {video_data}")
        return {
            "success": True,
            "data": video_data
        }
    except Exception as e:
        print(f"Error in API endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate")
async def validate_youtube_url(request: dict):
    """Validate YouTube URL"""
    try:
        url = request.get("url", "")
        service = get_youtube_service()
        video_id = service.extract_video_id(url)
        
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
