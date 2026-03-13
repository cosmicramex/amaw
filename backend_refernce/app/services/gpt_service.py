"""
GPT-5 Nano service for AI processing
"""

import os
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

logger = logging.getLogger(__name__)

class GPTService:
    """Service for interacting with GPT-5 Nano API"""
    
    def __init__(self):
        """Initialize GPT service"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for GPT-5 Nano")
        
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-4o-mini"  # Using GPT-4o-mini (cheapest and fastest)
        self.max_tokens = 4000
        self.temperature = 0.7
        
        logger.info("GPT-4o-mini service initialized successfully")
    
    async def generate_response(self, messages: List[Dict[str, Any]], system_prompt: str = None) -> str:
        """Generate response using GPT-4o-mini"""
        try:
            # Prepare messages
            api_messages = []
            
            if system_prompt:
                api_messages.append({"role": "system", "content": system_prompt})
            
            for message in messages:
                if message.get('role') == 'user' and message.get('parts'):
                    # Handle LlamaIndex format
                    content = ""
                    for part in message['parts']:
                        if part.get('type') == 'text':
                            content += part.get('text', '')
                    api_messages.append({"role": "user", "content": content})
                elif message.get('role') == 'assistant' and message.get('parts'):
                    # Handle LlamaIndex format
                    content = ""
                    for part in message['parts']:
                        if part.get('type') == 'text':
                            content += part.get('text', '')
                    api_messages.append({"role": "assistant", "content": content})
                else:
                    # Handle standard format
                    api_messages.append({
                        "role": message.get('role', 'user'),
                        "content": message.get('content', '')
                    })
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": api_messages,
                    "max_completion_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "stream": False
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        error_text = await response.text()
                        logger.error(f"GPT-5 Nano API error: {response.status} - {error_text}")
                        raise Exception(f"API request failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error in GPT-5 Nano generation: {str(e)}")
            raise e
    
    async def process_content(self, content_data: Dict[str, Any], content_type: str, 
                           user_prompt: str, grounded_search_results: str = None) -> str:
        """Process content with GPT-5 Nano"""
        try:
            # Build system prompt based on content type
            system_prompt = self._build_system_prompt(content_type, content_data)
            
            # Build user message
            user_message = self._build_user_message(content_data, content_type, user_prompt, grounded_search_results)
            
            # Generate response
            response = await self.generate_response(
                messages=[{"role": "user", "content": user_message}],
                system_prompt=system_prompt
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing content with GPT-5 Nano: {str(e)}")
            raise e
    
    def _build_system_prompt(self, content_type: str, content_data: Dict[str, Any]) -> str:
        """Build system prompt based on content type"""
        
        if content_type == "youtube":
            return f"""You are an AI assistant specialized in analyzing YouTube videos.

CURRENT VIDEO CONTEXT:
- Video Title: {content_data.get('videoData', {}).get('title', content_data.get('title', 'Unknown'))}
- Channel: {content_data.get('videoData', {}).get('channel_title', content_data.get('channel_title', 'Unknown'))}
- Duration: {content_data.get('videoData', {}).get('duration', content_data.get('duration', 'Unknown'))}
- Published: {content_data.get('videoData', {}).get('published_at', content_data.get('published_at', 'Unknown'))}

Your task is to:
1. Analyze the video content based on the title, description, and any available metadata
2. Provide structured, well-organized responses with clear headings
3. When grounded search is enabled, integrate external information with video context
4. Use markdown formatting for better readability
5. Include proper citations [1], [2], etc. for external sources
6. Provide a "References" section at the end

Focus on the video's main topics, key insights, and how they relate to the user's request."""
        
        elif content_type == "document":
            return """You are an AI assistant specialized in analyzing documents.

Your task is to:
1. Extract key information from the document content
2. Provide structured, well-organized responses with clear headings
3. When grounded search is enabled, integrate external information with document content
4. Use markdown formatting for better readability
5. Include proper citations [1], [2], etc. for external sources
6. Provide a "References" section at the end

Focus on the document's main topics, key insights, and how they relate to the user's request."""
        
        elif content_type == "image":
            return """You are an AI assistant specialized in analyzing images.

Your task is to:
1. Describe the image content in detail
2. Identify objects, people, text, and visual elements
3. Provide insights about the image's context and meaning
4. When grounded search is enabled, integrate external information with image analysis
5. Use markdown formatting for better readability
6. Include proper citations [1], [2], etc. for external sources
7. Provide a "References" section at the end

Focus on providing comprehensive visual analysis and relevant context."""
        
        else:
            return """You are an AI assistant specialized in processing various types of content.

Your task is to:
1. Analyze the provided content thoroughly
2. Provide structured, well-organized responses with clear headings
3. When grounded search is enabled, integrate external information with content analysis
4. Use markdown formatting for better readability
5. Include proper citations [1], [2], etc. for external sources
6. Provide a "References" section at the end

Focus on the content's main topics, key insights, and how they relate to the user's request."""
    
    def _build_user_message(self, content_data: Dict[str, Any], content_type: str, 
                          user_prompt: str, grounded_search_results: str = None) -> str:
        """Build user message with content and search results"""
        
        message = f"User Request: {user_prompt}\n\n"
        
        # Add content-specific information
        if content_type == "youtube":
            # Extract video data from the nested structure
            video_data = content_data.get('videoData', content_data)
            
            message += f"""## YouTube Video Analysis

**Video Details:**
- **Title:** {video_data.get('title', 'Unknown')}
- **Channel:** {video_data.get('channel_title', 'Unknown')}
- **Duration:** {video_data.get('duration', 'Unknown')}
- **Published:** {video_data.get('published_at', 'Unknown')}
- **Video ID:** {video_data.get('video_id', 'Unknown')}

**Description:**
{video_data.get('description', 'No description available')[:500]}{'...' if len(video_data.get('description', '')) > 500 else ''}

**Transcript:**
{video_data.get('transcript', 'No transcript available')[:1000]}{'...' if len(video_data.get('transcript', '')) > 1000 else ''}

**Analysis Context:**
This video appears to be about: {video_data.get('title', 'Unknown')}. Based on the title and description, the main topics likely include: [Analyze based on title and description keywords].

Please provide a comprehensive analysis that:
1. Summarizes the key points of this video
2. Identifies the main topics and themes
3. Extracts actionable insights
4. Relates the content to the user's specific request
"""
        
        elif content_type == "document":
            message += f"""## Document Analysis

**Document Content:**
{content_data.get('content', 'No content available')[:1000]}{'...' if len(content_data.get('content', '')) > 1000 else ''}

Please provide a comprehensive analysis that:
1. Summarizes the key points of this document
2. Identifies the main topics and themes
3. Extracts actionable insights
4. Relates the content to the user's specific request
"""
        
        elif content_type == "image":
            message += f"""## Image Analysis

**Image Details:**
- **Filename:** {content_data.get('filename', 'Unknown')}
- **Size:** {content_data.get('size', 'Unknown')}
- **Format:** {content_data.get('format', 'Unknown')}

**Image Description:**
{content_data.get('description', 'No description available')}

Please provide a comprehensive analysis that:
1. Describes the visual content in detail
2. Identifies objects, people, text, and visual elements
3. Provides insights about the image's context and meaning
4. Relates the analysis to the user's specific request
"""
        
        # Add grounded search results if available
        if grounded_search_results:
            message += f"\n\n## External Search Results\n\n{grounded_search_results}\n\n"
            message += "Please integrate these search results with your analysis and provide proper citations."
        
        return message
    
    async def process_with_multi_gen(self, nodes: List[Dict[str, Any]], user_prompt: str, 
                                   grounded_search: bool = False) -> Dict[str, Any]:
        """Process nodes with multi-modal generation"""
        try:
            # Get grounded search results if enabled
            grounded_search_results = None
            if grounded_search:
                from ..services.google_search_service import google_search_service
                grounded_search_results = await google_search_service.search_and_format(user_prompt)
            
            # Process each node
            responses = []
            for node in nodes:
                content_data = node.data if hasattr(node, 'data') else {}
                content_type = node.type if hasattr(node, 'type') else 'text'
                
                # Map frontend node types to backend content types
                type_mapping = {
                    'youtubeNode': 'youtube',
                    'documentNode': 'document', 
                    'imageNode': 'image',
                    'websiteNode': 'website',
                    'textNode': 'text',
                    'codeNode': 'code'
                }
                content_type = type_mapping.get(content_type, content_type)
                
                # Generate response for this node
                response = await self.process_content(
                    content_data=content_data,
                    content_type=content_type,
                    user_prompt=user_prompt,
                    grounded_search_results=grounded_search_results
                )
                
                responses.append({
                    'node_id': node.id if hasattr(node, 'id') else 'unknown',
                    'node_type': content_type,
                    'response': response
                })
            
            # Generate both image and PDF if multi-gen is enabled
            outputs = {}
            if len(responses) > 0:
                # Combine all responses for context
                combined_content = "\n\n".join([r['response'] for r in responses])
                
                # Generate image based on the combined AI analysis (not just user prompt)
                from ..services.image_agent import image_agent
                # Create contextual image prompt from AI analysis
                image_prompt = f"Create a visual representation of: {combined_content[:200]}... Style: professional, informative"
                image_result = await image_agent.generate_image(
                    prompt=image_prompt,
                    style="realistic"
                )
                
                if image_result.get('success'):
                    outputs['image'] = image_result
                
                # Generate PDF report with the analysis
                from ..services.pdf_agent import pdf_agent
                pdf_title = f"AI Analysis Report: {user_prompt[:50]}..."
                pdf_result = await pdf_agent.generate_pdf(
                    content=combined_content,
                    title=pdf_title,
                    include_images=[image_result] if image_result.get('success') else None
                )
                
                if pdf_result.get('success'):
                    outputs['pdf'] = pdf_result
            
            return {
                'success': True,
                'responses': responses,
                'outputs': outputs,
                'grounded_search_results': grounded_search_results
            }
            
        except Exception as e:
            logger.error(f"Error in multi-gen processing: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "responses": [],
                "outputs": {},
                "processed_at": datetime.now().isoformat()
            }
    
    async def process_single_node(self, node: Dict[str, Any], user_prompt: str, 
                                grounded_search: bool = False) -> str:
        """Process a single node"""
        try:
            # Get grounded search results if enabled
            grounded_search_results = None
            if grounded_search:
                from ..services.google_search_service import google_search_service
                grounded_search_results = await google_search_service.search_and_format(user_prompt)
            
            content_data = node.data if hasattr(node, 'data') else {}
            content_type = node.type if hasattr(node, 'type') else 'text'
            
            # Map frontend node types to backend content types
            type_mapping = {
                'youtubeNode': 'youtube',
                'documentNode': 'document', 
                'imageNode': 'image',
                'websiteNode': 'website',
                'textNode': 'text',
                'codeNode': 'code'
            }
            content_type = type_mapping.get(content_type, content_type)
            
            # Generate response
            response = await self.process_content(
                content_data=content_data,
                content_type=content_type,
                user_prompt=user_prompt,
                grounded_search_results=grounded_search_results
            )
            
            # Return formatted response
            return {
                "success": True,
                "response": response,
                "text": response,
                "content_type": content_type,
                "nodes_processed": 1,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing single node: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content_type": "error",
                "nodes_processed": 0,
                "processed_at": datetime.now().isoformat()
            }

# Create global instance
gpt_service = GPTService()
