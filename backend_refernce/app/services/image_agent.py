import os
import base64
import io
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class ImageAgent:
    def __init__(self):
        """Initialize the Image Generation Agent with DALL-E 2 only"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.mock_mode = not bool(self.openai_api_key)
        
        if self.openai_api_key:
            logger.info("✅ DALL-E 2 Image Agent initialized successfully")
            logger.info("💰 Cost: ~$0.016-0.020 per image (cheapest option)")
            logger.info("⚡ Speed: Fastest processing times")
            logger.info("🎨 Quality: High-quality image generation")
        else:
            logger.warning("⚠️ No OpenAI API key found - using mock mode")
            logger.info("🔧 Add OPENAI_API_KEY to environment variables for real image generation")

    async def generate_image(self, prompt: str, style: str = "realistic") -> Dict[str, Any]:
        """
        Generate an image from text prompt using DALL-E 2
        
        Args:
            prompt: Text description for image generation
            style: Style preference (realistic, artistic, cartoon, etc.)
            
        Returns:
            Dict containing image data, metadata, and status
        """
        try:
            if self.mock_mode:
                logger.info("🎭 Using mock mode for image generation")
                return await self._generate_mock_image(prompt, style)
            
            # Enhanced prompt with style
            enhanced_prompt = self._enhance_prompt(prompt, style)
            logger.info(f"🎨 Generating image with DALL-E 2: {enhanced_prompt[:100]}...")
            
            result = await self._generate_dalle2(enhanced_prompt, style)
            
            if result["success"]:
                logger.info("✅ Image generated successfully with DALL-E 2")
                return result
            else:
                logger.warning("❌ DALL-E 2 failed, falling back to mock image")
                return await self._generate_mock_image(prompt, style)
            
        except Exception as e:
            logger.error(f"💥 Error in image generation: {str(e)}")
            return await self._generate_mock_image(prompt, style)

    async def _generate_dalle2(self, prompt: str, style: str) -> Dict[str, Any]:
        """Generate image using OpenAI DALL-E 2 (cheapest, fastest option)"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=self.openai_api_key)
            
            # DALL-E 2 parameters (cheapest option)
            response = await client.images.generate(
                model="dall-e-2",  # Using DALL-E 2 (cheapest at ~$0.016-0.020 per image)
                prompt=prompt,
                size="1024x1024",  # Standard resolution
                n=1
            )
            
            # Download image
            image_url = response.data[0].url
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status != 200:
                        raise Exception(f"Failed to download image: HTTP {resp.status}")
                    image_data = await resp.read()
            
            # Convert to PIL Image and resize to 1920x1080 for consistency
            image = Image.open(io.BytesIO(image_data))
            image_base64 = self._image_to_base64(image)
            
            return {
                "success": True,
                "image_data": image_base64,
                "filename": f"dalle2_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                "prompt": prompt,
                "style": style,
                "generated_at": self._get_timestamp(),
                "model": "dall-e-2",
                "provider": "openai",
                "cost_estimate": "$0.016-0.020",
                "resolution": "1920x1080"
            }
        except Exception as e:
            logger.error(f"💥 DALL-E 2 generation failed: {e}")
            return {"success": False, "error": str(e)}

    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance the prompt with style and quality keywords optimized for DALL-E 2"""
        style_keywords = {
            "realistic": "photorealistic, high quality, detailed, professional photography, sharp focus",
            "artistic": "artistic, creative, stylized, digital art, concept art, masterpiece",
            "cartoon": "cartoon style, animated, colorful, fun, illustration, Disney style",
            "minimalist": "minimalist, clean, simple, modern design, elegant",
            "vintage": "vintage style, retro, classic, aged look, nostalgic"
        }
        
        style_text = style_keywords.get(style, style_keywords["realistic"])
        # DALL-E 2 optimized prompt enhancement
        return f"{prompt}, {style_text}, 4k resolution, high detail, award winning"

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string in 1920x1080 resolution"""
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to 1920x1080 for consistency across the app
        target_width, target_height = 1920, 1080
        if image.width != target_width or image.height != target_height:
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Convert to base64 with optimized quality
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=90, optimize=True)
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8')

    async def _generate_mock_image(self, prompt: str, style: str) -> Dict[str, Any]:
        """Generate a mock image response for testing when no API key is available"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"mock_dalle2_{timestamp}.jpg"
        
        try:
            # Generate a professional-looking mock image
            image = self._create_mock_image(prompt, style)
            image_base64 = self._image_to_base64(image)
            
            return {
                "success": True,
                "image_data": image_base64,
                "filename": filename,
                "prompt": f"Mock DALL-E 2 image for: {prompt}",
                "style": style,
                "generated_at": self._get_timestamp(),
                "model": "dall-e-2-mock",
                "provider": "openai-mock",
                "cost_estimate": "$0.000 (mock mode)",
                "resolution": "1920x1080",
                "mock_mode": True
            }
        except Exception as e:
            logger.error(f"💥 Error creating mock image: {str(e)}")
            return {
                "success": True,
                "image_data": None,  # Fallback to no image
                "filename": filename,
                "prompt": f"Mock DALL-E 2 image for: {prompt}",
                "style": style,
                "generated_at": self._get_timestamp(),
                "model": "dall-e-2-mock",
                "provider": "openai-mock",
                "cost_estimate": "$0.000 (mock mode)",
                "resolution": "1920x1080",
                "mock_mode": True
            }

    def _create_mock_image(self, prompt: str, style: str) -> Image.Image:
        """Create a professional mock image for testing in 1920x1080 resolution"""
        width, height = 1920, 1080
        
        # Create a gradient background based on style
        style_colors = {
            "realistic": [(30, 50, 80), (60, 80, 120)],
            "artistic": [(80, 30, 80), (120, 60, 120)],
            "cartoon": [(255, 200, 100), (255, 150, 50)],
            "minimalist": [(240, 240, 245), (220, 220, 230)],
            "vintage": [(139, 115, 85), (160, 130, 100)]
        }
        
        colors = style_colors.get(style, style_colors["realistic"])
        
        # Create gradient
        image = Image.new('RGB', (width, height))
        for y in range(height):
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * y / height)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * y / height)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * y / height)
            for x in range(width):
                image.putpixel((x, y), (r, g, b))
        
        # Add text overlay
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(image)
        
        # Try to use a system font
        try:
            title_font = ImageFont.truetype("arial.ttf", 64)
            subtitle_font = ImageFont.truetype("arial.ttf", 32)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Main title
        title_text = "DALL-E 2 Mock Image"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        title_y = height // 2 - 100
        
        # Add shadow effect
        draw.text((title_x + 3, title_y + 3), title_text, fill=(0, 0, 0, 128), font=title_font)
        draw.text((title_x, title_y), title_text, fill=(255, 255, 255), font=title_font)
        
        # Prompt text
        prompt_text = f"Prompt: {prompt[:60]}{'...' if len(prompt) > 60 else ''}"
        prompt_bbox = draw.textbbox((0, 0), prompt_text, font=subtitle_font)
        prompt_width = prompt_bbox[2] - prompt_bbox[0]
        prompt_x = (width - prompt_width) // 2
        prompt_y = title_y + 100
        
        draw.text((prompt_x + 2, prompt_y + 2), prompt_text, fill=(0, 0, 0, 128), font=subtitle_font)
        draw.text((prompt_x, prompt_y), prompt_text, fill=(255, 255, 255), font=subtitle_font)
        
        # Style indicator
        style_text = f"Style: {style.title()}"
        style_bbox = draw.textbbox((0, 0), style_text, font=subtitle_font)
        style_width = style_bbox[2] - style_bbox[0]
        style_x = (width - style_width) // 2
        style_y = prompt_y + 60
        
        draw.text((style_x + 2, style_y + 2), style_text, fill=(0, 0, 0, 128), font=subtitle_font)
        draw.text((style_x, style_y), style_text, fill=(255, 255, 255), font=subtitle_font)
        
        # Add decorative border
        border_width = 8
        draw.rectangle([border_width, border_width, width-border_width, height-border_width], 
                      outline=(255, 255, 255), width=border_width)
        
        # Add corner decorations
        corner_size = 50
        for corner in [(50, 50), (width-50, 50), (50, height-50), (width-50, height-50)]:
            draw.ellipse([corner[0]-corner_size//2, corner[1]-corner_size//2, 
                         corner[0]+corner_size//2, corner[1]+corner_size//2], 
                        fill=(255, 255, 255, 200))
        
        return image

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()

    async def get_image_info(self, image_data: str) -> Dict[str, Any]:
        """Get information about generated image"""
        try:
            if not image_data:
                return {"error": "No image data provided"}
            
            # Decode base64 to get image info
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "size_bytes": len(image_bytes),
                "size_mb": round(len(image_bytes) / (1024 * 1024), 2)
            }
        except Exception as e:
            return {"error": str(e)}

# Global instance
image_agent = ImageAgent()