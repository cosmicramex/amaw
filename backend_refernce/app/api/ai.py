from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from ..services.gemini_service import gemini_service
from ..services.gpt_service import gpt_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI Processing"])

class NodeData(BaseModel):
    """Model for node data"""
    id: str
    type: str
    data: Dict[str, Any]

class ProcessRequest(BaseModel):
    """Model for AI processing request"""
    user_prompt: str
    nodes: List[NodeData]
    grounded_search: Optional[bool] = False
    multi_gen: Optional[bool] = False

class ProcessResponse(BaseModel):
    """Model for AI processing response"""
    success: bool
    response: Optional[str] = None
    text: Optional[str] = None
    outputs: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    content_type: Optional[str] = None
    nodes_processed: Optional[int] = None
    processed_at: Optional[str] = None

@router.post("/process", response_model=ProcessResponse)
async def process_content(request: ProcessRequest):
    """
    Process connected nodes with AI
    
    Args:
        request: Contains user prompt, connected nodes, and feature toggles
        
    Returns:
        AI response based on the connected content and enabled features
    """
    try:
        logger.info(f"Processing {len(request.nodes)} nodes with prompt: {request.user_prompt}")
        logger.info(f"Grounded Search: {request.grounded_search}, Multi-Gen: {request.multi_gen}")
        
        if not request.nodes:
            raise HTTPException(status_code=400, detail="No nodes provided for processing")
        
        # Use GPT-5 Nano service for all processing
        service = gpt_service
        logger.info("Using GPT-5 Nano model for processing")
        
        # Process with enhanced features
        if request.multi_gen:
            # Multi-modal output generation
            result = await service.process_with_multi_gen(
                nodes=request.nodes,
                user_prompt=request.user_prompt,
                grounded_search=request.grounded_search
            )
        else:
            # Regular text processing
            if len(request.nodes) == 1:
                # Single node processing
                node = request.nodes[0]
                result = await service.process_single_node(
                    node=node,
                    user_prompt=request.user_prompt,
                    grounded_search=request.grounded_search
                )
            else:
                # Multiple nodes processing
                result = await service.process_with_multi_gen(
                    nodes=request.nodes,
                    user_prompt=request.user_prompt,
                    grounded_search=request.grounded_search
                )
        
        if result["success"]:
            # Handle both single node and multi-gen responses
            response_text = result.get("response") or result.get("text")
            if not response_text and result.get("responses"):
                # Multi-gen response format
                responses = result.get("responses", [])
                if responses:
                    response_text = responses[0].get("response", "")
            
            return ProcessResponse(
                success=True,
                response=response_text,
                text=response_text,
                outputs=result.get("outputs"),
                content_type=result.get("content_type"),
                nodes_processed=result.get("nodes_processed", len(result.get("responses", [1]))),
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
        # Test Gemini API connection
        test_response = await gemini_service._generate_response("Hello, this is a test.")
        return {
            "status": "healthy",
            "service": "AI Processing",
            "gemini_api": "connected",
            "test_response": test_response[:50] + "..." if len(test_response) > 50 else test_response
        }
    except Exception as e:
        logger.error(f"AI service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "AI Processing",
            "error": str(e)
        }