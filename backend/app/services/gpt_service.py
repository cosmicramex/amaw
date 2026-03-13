import os
import json
import logging
from openai import AsyncOpenAI
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPTService:
    def __init__(self):
        """Initialize GPT service with API key"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables - using mock mode")
            self.mock_mode = True
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)
            self.mock_mode = False
            logger.info("GPT-4o mini service initialized successfully")

    async def process_content(self, content_type: str, content_data: Dict[str, Any], user_prompt: str) -> Dict[str, Any]:
        """
        Process different types of content using GPT-4o mini API
        
        Args:
            content_type: Type of content (youtube, document, code, text, image, website)
            content_data: The actual content data
            user_prompt: User's request/prompt
            
        Returns:
            Dict containing the AI response and metadata
        """
        try:
            if self.mock_mode:
                # Return mock response when API key is not available
                mock_responses = {
                    "youtube": f"I would analyze this YouTube video '{content_data.get('title', 'Unknown')}' and respond to: '{user_prompt}'. This is a mock response - add your OpenAI API key to enable real AI processing.",
                    "document": f"I would analyze this document '{content_data.get('name', 'Unknown')}' and respond to: '{user_prompt}'. This is a mock response - add your OpenAI API key to enable real AI processing.",
                    "code": f"I would analyze this {content_data.get('language', 'code')} code and respond to: '{user_prompt}'. This is a mock response - add your OpenAI API key to enable real AI processing.",
                    "text": f"I would analyze this text content and respond to: '{user_prompt}'. This is a mock response - add your OpenAI API key to enable real AI processing.",
                    "image": f"I would analyze this image '{content_data.get('name', 'Unknown')}' and respond to: '{user_prompt}'. This is a mock response - add your OpenAI API key to enable real AI processing.",
                    "website": f"I would analyze this website '{content_data.get('url', 'Unknown')}' and respond to: '{user_prompt}'. This is a mock response - add your OpenAI API key to enable real AI processing."
                }
                
                return {
                    "success": True,
                    "response": mock_responses.get(content_type, f"Mock response for {content_type}: {user_prompt}"),
                    "content_type": content_type,
                    "processed_at": self._get_timestamp()
                }
            
            # Build context-aware prompt based on content type
            system_prompt = self._build_system_prompt(content_type, content_data)
            full_prompt = f"{system_prompt}\n\nUser Request: {user_prompt}\n\nContent to Process:\n{self._format_content_data(content_type, content_data)}"
            
            # Generate response using GPT-4o mini
            response = await self._generate_response(full_prompt)
            
            return {
                "success": True,
                "response": response,
                "content_type": content_type,
                "processed_at": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error processing {content_type} content: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content_type": content_type
            }

    async def process_multiple_nodes(self, nodes_data: List[Dict[str, Any]], user_prompt: str) -> Dict[str, Any]:
        """
        Process multiple connected nodes together
        
        Args:
            nodes_data: List of node data with content
            user_prompt: User's request/prompt
            
        Returns:
            Dict containing the AI response
        """
        try:
            # Build comprehensive prompt for multiple nodes
            system_prompt = "You are an AI assistant that can analyze and process multiple types of content. The user has connected multiple nodes and wants you to process them together."
            
            content_summary = "Connected Content:\n"
            for i, node in enumerate(nodes_data, 1):
                content_summary += f"\n--- Node {i} ({node.get('type', 'unknown')}) ---\n"
                content_summary += self._format_content_data(node.get('type', 'unknown'), node.get('data', {}))
            
            full_prompt = f"{system_prompt}\n\nUser Request: {user_prompt}\n\n{content_summary}"
            
            # Generate response
            response = await self._generate_response(full_prompt)
            
            return {
                "success": True,
                "response": response,
                "nodes_processed": len(nodes_data),
                "processed_at": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error processing multiple nodes: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "nodes_processed": 0
            }

    def _build_system_prompt(self, content_type: str, content_data: Dict[str, Any]) -> str:
        """Build context-aware system prompt based on content type"""
        prompts = {
            "youtube": "You are an AI assistant specialized in analyzing YouTube videos. You can summarize videos, extract key insights, answer questions about the content, and provide detailed analysis.",
            "document": "You are an AI assistant specialized in document analysis. You can summarize documents, extract key information, answer questions about the content, and provide insights.",
            "code": "You are an AI assistant specialized in code analysis. You can review code, explain functionality, suggest improvements, debug issues, and provide programming insights.",
            "text": "You are an AI assistant that can analyze and process text content. You can summarize, extract key points, answer questions, and provide insights about the text.",
            "image": "You are an AI assistant specialized in image analysis. You can describe images, extract text from images, analyze visual content, and provide insights.",
            "website": "You are an AI assistant specialized in web content analysis. You can summarize web pages, extract key information, and provide insights about the content."
        }
        
        return prompts.get(content_type, "You are an AI assistant that can analyze and process various types of content.")

    def _format_content_data(self, content_type: str, content_data: Dict[str, Any]) -> str:
        """Format content data for AI processing"""
        if content_type == "youtube":
            return f"""
Video Title: {content_data.get('title', 'Unknown')}
Channel: {content_data.get('channel_title', 'Unknown')}
Description: {content_data.get('description', 'No description available')}
Duration: {content_data.get('duration', 'Unknown')}
Published: {content_data.get('published_at', 'Unknown')}
Video ID: {content_data.get('video_id', 'Unknown')}
"""
        
        elif content_type == "document":
            return f"""
Document Name: {content_data.get('name', 'Unknown')}
File Size: {content_data.get('size', 'Unknown')}
File Type: {content_data.get('type', 'Unknown')}
Content: {content_data.get('content', 'No content available')}
"""
        
        elif content_type == "code":
            return f"""
Language: {content_data.get('language', 'Unknown')}
Code:
{content_data.get('code', 'No code available')}
"""
        
        elif content_type == "text":
            return f"""
Text Content:
{content_data.get('text', 'No text available')}
"""
        
        elif content_type == "image":
            return f"""
Image Name: {content_data.get('name', 'Unknown')}
Image Size: {content_data.get('size', 'Unknown')}
Image Type: {content_data.get('type', 'Unknown')}
Description: {content_data.get('description', 'No description available')}
"""
        
        elif content_type == "website":
            return f"""
Website URL: {content_data.get('url', 'Unknown')}
Title: {content_data.get('title', 'Unknown')}
Content: {content_data.get('content', 'No content available')}
"""
        
        else:
            return f"Content Data: {json.dumps(content_data, indent=2)}"

    async def _generate_response(self, prompt: str) -> str:
        """Generate response using GPT-4o mini API"""
        try:
            if self.mock_mode:
                return "This is a mock AI response. Add your OpenAI API key to the .env file to enable real AI processing."
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating GPT response: {str(e)}")
            raise Exception(f"Failed to generate AI response: {str(e)}")

    async def generate_image(self, prompt: str) -> Dict[str, Any]:
        """Generate image using DALL-E 2"""
        try:
            if self.mock_mode:
                return {
                    "success": True,
                    "image_url": "https://via.placeholder.com/512x512?text=Mock+DALL-E+Image",
                    "prompt": prompt
                }
            
            response = await self.client.images.generate(
                model="dall-e-2",
                prompt=prompt,
                n=1,
                size="512x512"
            )
            
            return {
                "success": True,
                "image_url": response.data[0].url,
                "prompt": prompt
            }
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt
            }

    async def summarize_text(self, text: str) -> Dict[str, Any]:
        """Summarize text content"""
        try:
            if self.mock_mode:
                return {
                    "success": True,
                    "summary": f"Mock summary of the provided text. Add your OpenAI API key to enable real summarization.",
                    "original_length": len(text),
                    "summary_length": 50
                }
            
            prompt = f"Please provide a concise summary of the following text:\n\n{text}"
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that specializes in summarizing text."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            summary = response.choices[0].message.content
            
            return {
                "success": True,
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary)
            }
            
        except Exception as e:
            logger.error(f"Error summarizing text: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

# Global instance
gpt_service = GPTService()
