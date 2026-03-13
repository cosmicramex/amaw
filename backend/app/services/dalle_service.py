import os
import logging
import openai
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DalleService:
    def __init__(self):
        """Initialize DALL-E service with API key"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables - using mock mode")
            self.mock_mode = True
        else:
            openai.api_key = api_key
            self.mock_mode = False
            logger.info("DALL-E 2 service initialized successfully")

    async def generate_image(self, prompt: str, size: str = "512x512") -> Dict[str, Any]:
        """
        Generate image using DALL-E 2
        
        Args:
            prompt: Text description of the desired image
            size: Image size (256x256, 512x512, or 1024x1024)
            
        Returns:
            Dict containing the image URL and metadata
        """
        try:
            if self.mock_mode:
                return {
                    "success": True,
                    "image_url": f"https://via.placeholder.com/{size}?text=Mock+DALL-E+Image",
                    "prompt": prompt,
                    "size": size,
                    "generated_at": self._get_timestamp()
                }
            
            response = await openai.Image.acreate(
                model="dall-e-2",
                prompt=prompt,
                n=1,
                size=size
            )
            
            return {
                "success": True,
                "image_url": response.data[0].url,
                "prompt": prompt,
                "size": size,
                "generated_at": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt
            }
    
    async def generate_variation(self, image_url: str) -> Dict[str, Any]:
        """
        Generate variation of an existing image
        
        Args:
            image_url: URL of the source image
            
        Returns:
            Dict containing the new image URL and metadata
        """
        try:
            if self.mock_mode:
                return {
                    "success": True,
                    "image_url": "https://via.placeholder.com/512x512?text=Mock+Image+Variation",
                    "source": image_url,
                    "generated_at": self._get_timestamp()
                }
            
            # In a real implementation, you'd download the image first
            # and then use the Image.create_variation endpoint
            
            # Mock implementation for now
            response = await openai.Image.acreate(
                model="dall-e-2",
                prompt="Create a variation of the provided image",
                n=1,
                size="512x512"
            )
            
            return {
                "success": True,
                "image_url": response.data[0].url,
                "source": image_url,
                "generated_at": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error generating image variation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "source": image_url
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

# Global instance
dalle_service = DalleService()
