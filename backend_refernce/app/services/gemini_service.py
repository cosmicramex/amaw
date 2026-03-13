import os
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from app.services.image_agent import image_agent
from app.services.pdf_agent import pdf_agent
from app.services.google_search_service import google_search_service

# Load environment variables
load_dotenv('.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        """Initialize Gemini service with API key"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables - using mock mode")
            self.model = None
            self.mock_mode = True
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.mock_mode = False
            logger.info("Gemini service initialized successfully")

    async def process_content(self, content_type: str, content_data: Dict[str, Any], user_prompt: str, grounded_search: bool = False) -> Dict[str, Any]:
        """
        Process different types of content using Gemini API
        
        Args:
            content_type: Type of content (youtube, document, code, text, image, website)
            content_data: The actual content data
            user_prompt: User's request/prompt
            grounded_search: Whether to perform web search for additional context
            
        Returns:
            Dict containing the AI response and metadata
        """
        try:
            if self.mock_mode:
                # Return mock response when API key is not available
                mock_responses = {
                    "youtube": f"I would analyze this YouTube video '{content_data.get('title', 'Unknown')}' and respond to: '{user_prompt}'. This is a mock response - add your Gemini API key to enable real AI processing.",
                    "document": f"I would analyze this document '{content_data.get('name', 'Unknown')}' and respond to: '{user_prompt}'. This is a mock response - add your Gemini API key to enable real AI processing.",
                    "code": f"I would analyze this {content_data.get('language', 'code')} code and respond to: '{user_prompt}'. This is a mock response - add your Gemini API key to enable real AI processing.",
                    "text": f"I would analyze this text content and respond to: '{user_prompt}'. This is a mock response - add your Gemini API key to enable real AI processing.",
                    "image": f"I would analyze this image '{content_data.get('name', 'Unknown')}' and respond to: '{user_prompt}'. This is a mock response - add your Gemini API key to enable real AI processing.",
                    "website": f"I would analyze this website '{content_data.get('url', 'Unknown')}' and respond to: '{user_prompt}'. This is a mock response - add your Gemini API key to enable real AI processing."
                }
                
                return {
                    "success": True,
                    "response": mock_responses.get(content_type, f"Mock response for {content_type}: {user_prompt}"),
                    "content_type": content_type,
                    "processed_at": self._get_timestamp()
                }
            
            # Build context-aware prompt based on content type
            system_prompt = self._build_system_prompt(content_type, content_data)
            search_context = ""
            
            if grounded_search:
                search_context = await self._perform_grounded_search(user_prompt, content_type)
            
            # Enhanced prompt for structured responses with citations
            enhanced_system_prompt = f"""{system_prompt}

IMPORTANT: When providing responses, especially with grounded search enabled:
1. Structure your response clearly with headings and bullet points
2. Include proper citations using [1], [2], etc. format
3. Provide a "References" section at the end with full URLs
4. Be factual and cite sources when making claims
5. Use markdown formatting for better readability
6. If using web search results, integrate them naturally into your response"""
            
            search_context_part = f"Web Search Context:\n{search_context}" if search_context else ""
            full_prompt = f"{enhanced_system_prompt}\n\nUser Request: {user_prompt}\n\nContent to Process:\n{self._format_content_data(content_type, content_data)}\n\n{search_context_part}"
            
            # Generate response using Gemini
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

    async def process_multiple_nodes(self, nodes_data: List[Dict[str, Any]], user_prompt: str, grounded_search: bool = False) -> Dict[str, Any]:
        """
        Process multiple connected nodes together
        
        Args:
            nodes_data: List of node data with content
            user_prompt: User's request/prompt
            grounded_search: Whether to perform web search for additional context
            
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
            
            search_context = ""
            if grounded_search:
                search_context = await self._perform_grounded_search(user_prompt, "multi_modal")
            
            full_prompt = f"{system_prompt}\n\nUser Request: {user_prompt}\n\n{content_summary}\n\n{f'Additional web context: {search_context}' if search_context else ''}"
            
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

    async def process_with_multi_gen(self, nodes: List[Dict], user_prompt: str, grounded_search: bool = False) -> Dict[str, Any]:
        """Process with multi-modal generation for multiple output formats"""
        try:
            if self.mock_mode:
                return self._mock_multi_modal_response(user_prompt)
            
            # Build context from all nodes
            context = self._build_multi_node_context(nodes)
            search_context = ""
            
            if grounded_search:
                search_context = await self._perform_grounded_search(user_prompt, "multi_modal")
            
            # Generate multi-modal outputs
            outputs = await self._generate_multi_modal_outputs(
                context=context,
                user_prompt=user_prompt,
                search_context=search_context,
                nodes=nodes
            )
            
            return {
                "success": True,
                "text": outputs.get("text", "Generated multi-modal content!"),
                "outputs": outputs,
                "content_type": "multi_modal",
                "nodes_processed": len(nodes),
                "processed_at": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error in multi-modal generation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "text": "Error generating multi-modal content",
                "outputs": self._mock_multi_modal_response(user_prompt)["outputs"]
            }

    async def _generate_multi_modal_outputs(self, context: str, user_prompt: str, search_context: str, nodes: List[Dict]) -> Dict:
        """Generate multiple output modalities"""
        outputs = {}
        
        # 1. Text Analysis
        text_prompt = f"""
        {context}
        
        {f"Web context: {search_context}" if search_context else ""}
        
        User Request: {user_prompt}
        
        Provide a comprehensive text analysis and summary.
        """
        outputs["text"] = await self._generate_response(text_prompt)
        
        # 2. Image Generation using Image Agent
        image_prompt = f"""
        Create a visual representation for: {user_prompt}
        
        Based on this content: {context[:500]}
        
        Generate a detailed image description that captures the key concepts and visual elements.
        Be specific about colors, composition, style, and key elements.
        """
        image_prompt_text = await self._generate_response(image_prompt)
        
        # Use Image Agent to generate actual image
        try:
            image_result = await image_agent.generate_image(image_prompt_text, style="realistic")
            
            if image_result["success"]:
                outputs["image"] = {
                    "prompt": image_prompt_text,
                    "image_data": image_result["image_data"],
                    "filename": image_result["filename"],
                    "generated": True,
                    "model": image_result["model"],
                    "mock_mode": image_result.get("mock_mode", False)
                }
            else:
                # Fallback to text prompt if image generation fails
                outputs["image"] = {
                    "prompt": image_prompt_text,
                    "generated": False,
                    "error": image_result.get("error", "Image generation failed"),
                    "fallback": True
                }
        except Exception as e:
            logger.error(f"Image generation error: {str(e)}")
            # Fallback to text prompt if image generation fails
            outputs["image"] = {
                "prompt": image_prompt_text,
                "generated": False,
                "error": str(e),
                "fallback": True
            }
        
        # 3. Code Generation
        code_prompt = f"""
        Generate Python code to analyze or process this content: {user_prompt}
        
        Content context: {context[:500]}
        
        Provide working Python code with proper imports and comments.
        """
        code_response = await self._generate_response(code_prompt)
        outputs["code"] = {
            "language": "python",
            "content": code_response,
            "filename": f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        }
        
        # 4. PDF Generation using PDF Agent with structured format
        pdf_prompt = f"""
        Create a comprehensive, professional report for: {user_prompt}
        
        Content to analyze: {context}
        
        IMPORTANT: You are a professional AI assistant capable of generating comprehensive reports. Do NOT include any disclaimers about being unable to create content. Generate the actual report content directly.
        
        STRUCTURE REQUIREMENTS:
        Follow this exact format and structure:
        
        # [Main Title]
        
        ## Executive Summary
        [2-3 paragraphs providing overview]
        
        ## Key Findings
        - [Bullet point 1]
        - [Bullet point 2]
        - [Bullet point 3]
        
        ## Detailed Analysis
        ### [Subsection 1]
        [Detailed analysis with data points]
        
        ### [Subsection 2]
        [More detailed analysis]
        
        ## Recommendations
        1. [Numbered recommendation 1]
        2. [Numbered recommendation 2]
        3. [Numbered recommendation 3]
        
        ## Conclusion
        [1-2 paragraphs summarizing key points]
        
        FORMATTING RULES:
        - Use markdown headers (##, ###) for sections
        - Use bullet points (-) for lists
        - Use numbered lists (1., 2., 3.) for recommendations
        - Use **bold** for emphasis on important data points
        - Keep paragraphs under 150 words
        - Include specific data points and statistics where relevant
        - Use professional, clear language
        - Ensure proper grammar and spelling
        - NEVER include disclaimers about inability to create content
        
        Generate the complete report following this exact structure.
        """
        pdf_content = await self._generate_response(pdf_prompt)
        
        # Use PDF Agent to generate actual PDF
        pdf_title = f"Report: {user_prompt[:50]}..."
        pdf_result = await pdf_agent.generate_pdf(
            content=pdf_content,
            title=pdf_title,
            include_images=[outputs.get("image")] if outputs.get("image", {}).get("image_data") else None
        )
        
        if pdf_result["success"]:
            outputs["pdf"] = {
                "content": pdf_content,
                "pdf_data": pdf_result["pdf_data"],
                "filename": pdf_result["filename"],
                "title": pdf_result["title"],
                "generated": True,
                "file_size": pdf_result["file_size"],
                "mock_mode": pdf_result.get("mock_mode", False)
            }
        else:
            # Fallback to text content if PDF generation fails
            outputs["pdf"] = {
                "content": pdf_content,
                "generated": False,
                "error": pdf_result.get("error", "PDF generation failed"),
                "fallback": True
            }
        
        return outputs

    async def _perform_grounded_search(self, query: str, content_type: str) -> str:
        """Perform grounded search for additional context using Google Search API"""
        try:
            logger.info(f"Performing grounded search for: {query}")
            
            # Use Google Search service to get web results
            search_results = await google_search_service.search_and_format(query, num_results=5)
            
            if search_results:
                logger.info(f"Found {len(search_results.split('Search Results')) - 1} search results")
                return search_results
            else:
                logger.warning("No search results found")
                return f"Web search for '{query}' returned no results."
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Web search error: {str(e)}"

    def _build_multi_node_context(self, nodes: List[Dict]) -> str:
        """Build context from multiple nodes"""
        context_parts = []
        
        for node in nodes:
            # Handle both NodeData objects and dictionaries
            if hasattr(node, 'type'):
                # NodeData object
                node_type = node.type
                node_data = node.data
            else:
                # Dictionary
                node_type = node.get("type", "unknown")
                node_data = node.get("data", {})
            
            if node_type == "youtube":
                context_parts.append(f"YouTube Video: {node_data.get('title', 'Unknown')} - {node_data.get('description', 'No description')}")
            elif node_type == "document":
                context_parts.append(f"Document: {node_data.get('name', 'Unknown file')} - {node_data.get('content', 'No content')}")
            elif node_type == "code":
                context_parts.append(f"Code ({node_data.get('language', 'unknown')}): {node_data.get('code', 'No code')}")
            elif node_type == "website":
                context_parts.append(f"Website: {node_data.get('url', 'Unknown URL')} - {node_data.get('content', 'No content')}")
            elif node_type == "image":
                context_parts.append(f"Image: {node_data.get('name', 'Unknown image')} - {node_data.get('description', 'No description')}")
            elif node_type == "text":
                context_parts.append(f"Text: {node_data.get('text', 'No text')}")
        
        return "\n\n".join(context_parts)

    def _build_system_prompt(self, content_type: str, content_data: Dict[str, Any]) -> str:
        """Build context-aware system prompt based on content type"""
        prompts = {
            "youtube": f"""You are an AI assistant specialized in analyzing YouTube videos. 

CURRENT VIDEO CONTEXT:
- Video Title: {content_data.get('title', 'Unknown')}
- Channel: {content_data.get('channel_title', 'Unknown')}
- Duration: {content_data.get('duration', 'Unknown')}
- Published: {content_data.get('published_at', 'Unknown')}

Your task is to:
1. Analyze the video content based on the title, description, and any available metadata
2. Provide structured, well-organized responses with clear headings
3. When grounded search is enabled, integrate external information with video context
4. Use markdown formatting for better readability
5. Include proper citations [1], [2], etc. for external sources
6. Provide a "References" section at the end

Focus on the video's main topics, key insights, and how they relate to the user's request.""",
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
            description = content_data.get('description', 'No description available')
            # Truncate long descriptions for better processing
            if len(description) > 500:
                description = description[:500] + "..."
            
            return f"""
## YouTube Video Analysis

**Video Details:**
- **Title:** {content_data.get('title', 'Unknown')}
- **Channel:** {content_data.get('channel_title', 'Unknown')}
- **Duration:** {content_data.get('duration', 'Unknown')}
- **Published:** {content_data.get('published_at', 'Unknown')}
- **Video ID:** {content_data.get('video_id', 'Unknown')}

**Description:**
{description}

**Analysis Context:**
This video appears to be about: {content_data.get('title', 'Unknown')}. Based on the title and description, the main topics likely include: [Analyze based on title and description keywords].

Please provide a comprehensive analysis that:
1. Summarizes the key points of this video
2. Identifies the main topics and themes
3. Extracts actionable insights
4. Relates the content to the user's specific request
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
        """Generate response using Gemini API"""
        try:
            if self.mock_mode:
                return "This is a mock AI response. Add your Gemini API key to the .env file to enable real AI processing."
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            raise Exception(f"Failed to generate AI response: {str(e)}")

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()

    def _mock_multi_modal_response(self, user_prompt: str) -> Dict:
        """Mock multi-modal response for testing"""
        return {
            "success": True,
            "text": f"Mock multi-modal analysis for: {user_prompt}",
            "outputs": {
                "text": f"Mock text analysis for: {user_prompt}",
                "image": {
                    "prompt": f"Mock image prompt for: {user_prompt}",
                    "generated": True,
                    "url": "mock_image.png"
                },
                "code": {
                    "language": "python",
                    "content": f"# Mock code for: {user_prompt}\nprint('Hello World')",
                    "filename": "mock_analysis.py"
                },
                "pdf": {
                    "content": f"Mock PDF content for: {user_prompt}",
                    "summary": f"Mock report summary for: {user_prompt}",
                    "filename": "mock_report.pdf"
                }
            },
            "content_type": "multi_modal",
            "nodes_processed": 1,
            "processed_at": self._get_timestamp()
        }

# Global instance
gemini_service = GeminiService()