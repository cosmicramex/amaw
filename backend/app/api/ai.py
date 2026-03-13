from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from ..services.gpt_service import gpt_service
from ..services.dalle_service import dalle_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["AI Processing"])

class NodeData(BaseModel):
    """Model for node data"""
    id: str
    type: str
    data: Dict[str, Any]

class ProcessRequest(BaseModel):
    """Model for AI processing request"""
    user_prompt: str
    nodes: List[NodeData]
    search_context: Optional[List[Dict[str, Any]]] = []

class SearchRequest(BaseModel):
    """Model for grounded search request"""
    query: str
    context: List[NodeData]

class MultiGenRequest(BaseModel):
    """Model for multi-generation request"""
    prompt: str
    nodes: List[NodeData]
    count: int = 3

class VerifyRequest(BaseModel):
    """Model for verification request"""
    response: str
    context: List[NodeData]
    original_prompt: str
    
class ImageRequest(BaseModel):
    """Model for image generation request"""
    prompt: str
    size: str = "512x512"
    
class SummarizeRequest(BaseModel):
    """Model for text summarization request"""
    text: str

class ProcessResponse(BaseModel):
    """Model for AI processing response"""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    content_type: Optional[str] = None
    nodes_processed: Optional[int] = None
    processed_at: Optional[str] = None

@router.post("/process", response_model=ProcessResponse)
async def process_content(request: ProcessRequest):
    """
    Process connected nodes with AI
    
    Args:
        request: Contains user prompt and list of connected nodes
        
    Returns:
        AI response based on the connected content
    """
    try:
        logger.info(f"Processing {len(request.nodes)} nodes with prompt: {request.user_prompt}")
        
        if not request.nodes:
            raise HTTPException(status_code=400, detail="No nodes provided for processing")
        
        if len(request.nodes) == 1:
            # Single node processing
            node = request.nodes[0]
            result = await gpt_service.process_content(
                content_type=node.type,
                content_data=node.data,
                user_prompt=request.user_prompt
            )
        else:
            # Multiple nodes processing
            nodes_data = [{"type": node.type, "data": node.data} for node in request.nodes]
            result = await gpt_service.process_multiple_nodes(
                nodes_data=nodes_data,
                user_prompt=request.user_prompt
            )
        
        if result["success"]:
            return ProcessResponse(
                success=True,
                response=result["response"],
                content_type=result.get("content_type"),
                nodes_processed=result.get("nodes_processed", 1),
                processed_at=result.get("processed_at")
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI processing endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/process-single", response_model=ProcessResponse)
async def process_single_node(node_type: str, user_prompt: str, node_data: Dict[str, Any]):
    """
    Process a single node with AI
    
    Args:
        node_type: Type of the node (youtube, document, code, etc.)
        user_prompt: User's request/prompt
        node_data: The node's data content
        
    Returns:
        AI response for the single node
    """
    try:
        logger.info(f"Processing single {node_type} node with prompt: {user_prompt}")
        
        result = await gemini_service.process_content(
            content_type=node_type,
            content_data=node_data,
            user_prompt=user_prompt
        )
        
        if result["success"]:
            return ProcessResponse(
                success=True,
                response=result["response"],
                content_type=result.get("content_type"),
                nodes_processed=1,
                processed_at=result.get("processed_at")
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in single node processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint for AI service"""
    try:
        # Test GPT API connection
        test_response = await gpt_service._generate_response("Hello, this is a test.")
        return {
            "status": "healthy",
            "service": "AI Processing",
            "openai_api": "connected",
            "test_response": test_response[:50] + "..." if len(test_response) > 50 else test_response
        }
    except Exception as e:
        logger.error(f"AI service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "AI Processing",
            "error": str(e)
        }

@router.post("/generate-image")
async def generate_image(request: ImageRequest):
    """
    Generate image using DALL-E 2
    
    Args:
        request: Contains prompt and optional size
        
    Returns:
        Generated image URL
    """
    try:
        logger.info(f"Generating image for prompt: {request.prompt}")
        
        result = await dalle_service.generate_image(
            prompt=request.prompt,
            size=request.size
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Image generation failed"))
        
        return {
            "success": True,
            "image_url": result["image_url"],
            "prompt": request.prompt,
            "size": request.size
        }
        
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image generation error: {str(e)}")

@router.post("/summarize")
async def summarize_text(request: SummarizeRequest):
    """
    Summarize text content
    
    Args:
        request: Contains text to summarize
        
    Returns:
        Summarized text
    """
    try:
        logger.info("Summarizing text content")
        
        result = await gpt_service.summarize_text(request.text)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Summarization failed"))
        
        return {
            "success": True,
            "summary": result["summary"],
            "original_length": result["original_length"],
            "summary_length": result["summary_length"]
        }
        
    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")

@router.post("/search")
async def grounded_search(request: SearchRequest):
    """
    Perform grounded search with context
    
    Args:
        request: Contains search query and context nodes
        
    Returns:
        Search results with relevant information
    """
    try:
        logger.info(f"Performing grounded search for: {request.query}")
        
        # Mock search functionality for now
        return {
            "success": True,
            "results": [
                {
                    "title": f"Search result for: {request.query}",
                    "url": "https://example.com/result1",
                    "snippet": f"This is a search result for '{request.query}' based on the connected nodes."
                },
                {
                    "title": "Additional information",
                    "url": "https://example.com/result2",
                    "snippet": "More contextual information related to your query."
                }
            ],
            "query": request.query
        }
        
    except Exception as e:
        logger.error(f"Error in grounded search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.post("/multi-gen")
async def multi_generation(request: MultiGenRequest):
    """
    Generate multiple response variations
    
    Args:
        request: Contains prompt, nodes, and count
        
    Returns:
        Multiple AI response variations
    """
    try:
        logger.info(f"Generating {request.count} response variations")
        
        # Mock multiple response generation
        responses = []
        for i in range(request.count):
            responses.append(f"Response variation {i+1} for prompt: {request.prompt}")
        
        return {
            "success": True,
            "responses": responses,
            "count": len(responses)
        }
        
    except Exception as e:
        logger.error(f"Error in multi-generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Multi-generation error: {str(e)}")

@router.post("/verify")
async def verify_response(request: VerifyRequest):
    """
    Cross-check and verify AI response
    
    Args:
        request: Contains response, context, and original prompt
        
    Returns:
        Verification result with confidence score
    """
    try:
        logger.info("Verifying AI response")
        
        # Mock verification functionality
        return {
            "success": True,
            "verified": True,
            "confidence": 0.85,
            "feedback": "The response appears to be accurate based on the provided context.",
            "issues": []
        }
        
    except Exception as e:
        logger.error(f"Error in verification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")