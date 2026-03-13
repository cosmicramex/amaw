"""
YouTube Data API service for content extraction
"""

from googleapiclient.discovery import build
import re
from typing import Dict, Any, Optional
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

class YouTubeService:
    """Service for interacting with YouTube Data API"""
    
    def __init__(self):
        """Initialize YouTube service"""
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY is required")
        
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get video information from YouTube API"""
        try:
            # Get video details
            video_response = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()
            
            if not video_response['items']:
                raise Exception("Video not found")
            
            video = video_response['items'][0]
            snippet = video['snippet']
            statistics = video['statistics']
            content_details = video['contentDetails']
            
            # Extract video information
            video_info = {
                "video_id": video_id,
                "title": snippet['title'],
                "description": snippet['description'],
                "channel_title": snippet['channelTitle'],
                "published_at": snippet['publishedAt'],
                "thumbnail_url": snippet['thumbnails']['high']['url'],
                "duration": content_details['duration'],
                "view_count": statistics.get('viewCount', '0'),
                "like_count": statistics.get('likeCount', '0'),
                "comment_count": statistics.get('commentCount', '0'),
                "tags": snippet.get('tags', []),
                "category_id": snippet.get('categoryId', ''),
                "default_language": snippet.get('defaultLanguage', ''),
                "transcript": ""  # Will be populated separately if available
            }
            
            return video_info
        except Exception as e:
            raise Exception(f"Error fetching video info: {str(e)}")
    
    async def get_video_transcript(self, video_id: str) -> str:
        """Get video transcript (if available)"""
        try:
            # Try to get transcript using youtube-transcript-api
            # This is a fallback method since YouTube API doesn't provide transcripts directly
            transcript_url = f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(transcript_url)
                if response.status_code == 200:
                    # Parse transcript XML and extract text
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response.text)
                    transcript_text = ""
                    for elem in root.iter():
                        if elem.text:
                            transcript_text += elem.text + " "
                    return transcript_text.strip()
                else:
                    return ""
        except Exception as e:
            print(f"Error fetching transcript: {str(e)}")
            return ""
    
    async def process_youtube_url(self, url: str) -> Dict[str, Any]:
        """Process YouTube URL and extract all available information"""
        try:
            # Extract video ID
            video_id = self.extract_video_id(url)
            if not video_id:
                raise Exception("Invalid YouTube URL")
            
            # Get video information
            video_info = await self.get_video_info(video_id)
            
            # Try to get transcript
            transcript = await self.get_video_transcript(video_id)
            video_info["transcript"] = transcript
            
            return video_info
        except Exception as e:
            raise Exception(f"Error processing YouTube URL: {str(e)}")

# Global instance
youtube_service = YouTubeService()
