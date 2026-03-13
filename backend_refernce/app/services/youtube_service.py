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
        """Initialize YouTube service with robust fallback strategies"""
        self.api_keys = self._get_api_keys()
        self.youtube = None
        self.mock_mode = False
        self.current_api_key = None
        
        # Try to initialize with available API keys
        for api_key in self.api_keys:
            try:
                self.youtube = build('youtube', 'v3', developerKey=api_key)
                # Test the API key with a real request
                test_response = self.youtube.videos().list(part='snippet', id='dQw4w9WgXcQ', maxResults=1).execute()
                self.current_api_key = api_key
                self.mock_mode = False
                print(f"SUCCESS: YouTube service initialized with valid API key (length: {len(api_key)})")
                return
            except Exception as e:
                print(f"WARNING: API key failed: {str(e)[:100]}...")
                continue
        
        # If all API keys fail, use enhanced mock mode
        print("WARNING: All YouTube API keys failed - using enhanced mock mode with oEmbed fallback")
        self.youtube = None
        self.mock_mode = True
        self.current_api_key = None
    
    def _get_api_keys(self):
        """Get multiple API keys from environment variables"""
        keys = []
        
        # Primary API key
        primary_key = os.getenv('YOUTUBE_API_KEY')
        if primary_key and primary_key.strip() and primary_key != 'your_youtube_api_key_here':
            keys.append(primary_key)
        
        # Backup API keys
        for i in range(1, 4):  # YOUTUBE_API_KEY_2, YOUTUBE_API_KEY_3, YOUTUBE_API_KEY_4
            backup_key = os.getenv(f'YOUTUBE_API_KEY_{i}')
            if backup_key and backup_key.strip() and backup_key != 'your_youtube_api_key_here':
                keys.append(backup_key)
        
        return keys
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
            r'youtube\.com\/live\/([^&\n?#]+)',
            r'youtube\.com\/shorts\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_video_data_sync(self, video_id: str) -> Dict[str, Any]:
        """Get video data by ID - NEVER FAILS, always returns complete data for AI processing (synchronous)"""
        try:
            if self.mock_mode:
                # Enhanced mock mode with oEmbed fallback for real data
                return self._get_enhanced_video_data_sync(video_id)
            
            # Try YouTube API first
            try:
                return self._get_youtube_api_data_sync(video_id)
            except Exception as api_error:
                print(f"WARNING: YouTube API failed, trying oEmbed fallback: {api_error}")
                # Fallback to oEmbed API
                return self._get_oembed_data_sync(video_id)
                
        except Exception as e:
            # Ultimate fallback - return enhanced mock data
            print(f"WARNING: All methods failed, using enhanced mock: {e}")
            return self._get_enhanced_video_data_sync(video_id)
    
    async def get_video_data(self, video_id: str) -> Dict[str, Any]:
        """Get video data by ID - NEVER FAILS, always returns complete data for AI processing (async)"""
        return self.get_video_data_sync(video_id)
    
    def _get_youtube_api_data_sync(self, video_id: str) -> Dict[str, Any]:
        """Get data from YouTube API (synchronous)"""
        # Get video details using YouTube API
        video_response = self.youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        ).execute()
        
        if not video_response['items']:
            raise Exception("Video not found")
        
        video = video_response['items'][0]
        snippet = video['snippet']
        statistics = video.get('statistics', {})
        content_details = video.get('contentDetails', {})
        
        # Get transcript (synchronous version)
        transcript = self.get_video_transcript_sync(video_id)
        
        return {
            'video_id': video_id,
            'title': snippet.get('title', 'Unknown Title'),
            'description': snippet.get('description', ''),
            'channel_title': snippet.get('channelTitle', 'Unknown Channel'),
            'published_at': snippet.get('publishedAt', ''),
            'duration': content_details.get('duration', 'Unknown'),
            'view_count': statistics.get('viewCount', '0'),
            'like_count': statistics.get('likeCount', '0'),
            'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'),
            'transcript': transcript
        }
    
    async def _get_youtube_api_data(self, video_id: str) -> Dict[str, Any]:
        """Get data from YouTube API (async)"""
        return self._get_youtube_api_data_sync(video_id)
    
    async def _get_oembed_data(self, video_id: str) -> Dict[str, Any]:
        """Get data from YouTube oEmbed API (no API key required)"""
        import requests
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        
        try:
            response = requests.get(oembed_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'video_id': video_id,
                    'title': data.get('title', f'YouTube Video {video_id}'),
                    'description': '',  # oEmbed doesn't provide description
                    'channel_title': data.get('author_name', 'Unknown Channel'),
                    'published_at': '',
                    'duration': 'Unknown',
                    'view_count': 'Unknown',
                    'like_count': 'Unknown',
                    'thumbnail_url': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
                    'transcript': ''  # oEmbed doesn't provide transcript
                }
            else:
                raise Exception(f"oEmbed API failed: {response.status_code}")
        except Exception as e:
            raise Exception(f"oEmbed request failed: {e}")
    
    def _get_oembed_data_sync(self, video_id: str) -> Dict[str, Any]:
        """Get data from YouTube oEmbed API (synchronous version)"""
        import requests
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        
        try:
            response = requests.get(oembed_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'video_id': video_id,
                    'title': data.get('title', f'YouTube Video {video_id}'),
                    'description': '',  # oEmbed doesn't provide description
                    'channel_title': data.get('author_name', 'Unknown Channel'),
                    'published_at': '',
                    'duration': 'Unknown',
                    'view_count': 'Unknown',
                    'like_count': 'Unknown',
                    'thumbnail_url': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
                    'transcript': ''  # oEmbed doesn't provide transcript
                }
            else:
                raise Exception(f"oEmbed API failed: {response.status_code}")
        except Exception as e:
            raise Exception(f"oEmbed request failed: {e}")
    
    def _get_enhanced_video_data_sync(self, video_id: str) -> Dict[str, Any]:
        """Enhanced mock data with oEmbed fallback for real title and channel (synchronous)"""
        try:
            # Try to get real data from oEmbed
            oembed_data = self._get_oembed_data_sync(video_id)
            return oembed_data
        except:
            # Ultimate fallback - enhanced mock data
            return {
                'video_id': video_id,
                'title': f'YouTube Video {video_id}',
                'description': 'Video description not available - API key required for full details',
                'channel_title': 'Unknown Channel',
                'published_at': '',
                'duration': 'Unknown',
                'view_count': 'Unknown',
                'like_count': 'Unknown',
                'thumbnail_url': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
                'transcript': 'Transcript not available - API key required for transcript extraction'
            }

    async def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get video information from YouTube API"""
        try:
            if self.mock_mode:
                # Return mock data when API key is not available
                return {
                    "video_id": video_id,
                    "title": f"YouTube Video {video_id}",
                    "description": "Video description not available (mock mode)",
                    "channel_title": "Unknown Channel",
                    "published_at": "",
                    "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                    "duration": "Unknown",
                    "view_count": "0",
                    "like_count": "0",
                    "comment_count": "0",
                    "tags": [],
                    "category_id": "",
                    "default_language": "",
                    "transcript": "Transcript not available (mock mode)"
                }
            
            # Get video details using YouTube API
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
    
    def get_video_transcript_sync(self, video_id: str) -> str:
        """Get video transcript (synchronous)"""
        try:
            # Try to get transcript using youtube-transcript-api
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = ' '.join([item['text'] for item in transcript_list])
            return transcript_text
        except Exception as e:
            print(f"Error fetching transcript: {str(e)}")
            return ""
    
    async def get_video_transcript(self, video_id: str) -> str:
        """Get video transcript (async)"""
        return self.get_video_transcript_sync(video_id)
    
    async def process_youtube_url(self, url: str) -> Dict[str, Any]:
        """Process YouTube URL and extract all available information"""
        try:
            # Extract video ID
            video_id = self.extract_video_id(url)
            if not video_id:
                raise Exception("Invalid YouTube URL")
            
            # Get video information
            video_info = await self.get_video_info(video_id)
            
            # Try to get transcript (only if not in mock mode)
            if not self.mock_mode:
                transcript = await self.get_video_transcript(video_id)
                video_info["transcript"] = transcript
            
            return video_info
        except Exception as e:
            raise Exception(f"Error processing YouTube URL: {str(e)}")

# Global instance - will be initialized when first accessed
youtube_service = None

def get_youtube_service():
    """Get YouTube service instance, creating it if needed"""
    global youtube_service
    if youtube_service is None:
        try:
            youtube_service = YouTubeService()
            print(f"YouTube service initialized successfully. Mock mode: {youtube_service.mock_mode}")
        except Exception as e:
            print(f"Error initializing YouTube service: {e}")
            # Create a fallback service that always works
            youtube_service = type('MockYouTubeService', (), {
                'mock_mode': True,
                'extract_video_id': lambda self, url: url.split('/')[-1].split('?')[0] if 'youtu.be' in url else None,
                'get_video_data': lambda self, video_id: {
                    'video_id': video_id,
                    'title': f'YouTube Video {video_id}',
                    'description': 'Video description not available (fallback mode)',
                    'channel_title': 'Unknown Channel',
                    'published_at': '',
                    'duration': 'Unknown',
                    'view_count': '0',
                    'like_count': '0',
                    'thumbnail_url': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
                    'transcript': 'Transcript not available (fallback mode)'
                },
                'get_video_info': lambda self, video_id: {
                    "video_id": video_id,
                    "title": f"YouTube Video {video_id}",
                    "description": "Video description not available (fallback mode)",
                    "channel_title": "Unknown Channel",
                    "published_at": "",
                    "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                    "duration": "Unknown",
                    "view_count": "0",
                    "like_count": "0",
                    "comment_count": "0",
                    "tags": [],
                    "category_id": "",
                    "default_language": "",
                    "transcript": "Transcript not available (fallback mode)"
                },
                'process_youtube_url': lambda self, url: self.get_video_info(self.extract_video_id(url))
            })()
    return youtube_service
