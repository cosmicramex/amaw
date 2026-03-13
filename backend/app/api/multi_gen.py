from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
from datetime import datetime

from app.services.gpt_service import GPTService
from app.services.grounded_search_service import GroundedSearchService
from app.services.image_agent import image_agent
from app.services.pdf_agent import pdf_agent

router = APIRouter()

class MultiGenRequest(BaseModel):
    user_prompt: str
    ai_response: str
    search_context: List[Dict[str, Any]] = []
    connected_nodes: List[Dict[str, Any]] = []
    modalities: List[str] = ["pdf", "image"]

class MultiGenResponse(BaseModel):
    success: bool
    pdf_content: Optional[str] = None
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None
    error: Optional[str] = None

@router.post("/generate", response_model=MultiGenResponse)
async def generate_multi_gen_content(request: MultiGenRequest):
    """
    Generate enterprise-grade PDF content and DALL-E image based on AI response and context
    """
    try:
        gpt_service = GPTService()
        grounded_search_service = GroundedSearchService()
        
        results = {
            "success": True,
            "pdf_content": None,
            "image_prompt": None,
            "image_url": None
        }
        
        # Generate enterprise-grade PDF content
        if "pdf" in request.modalities:
            pdf_result = await generate_enterprise_pdf(
                gpt_service,
                request.user_prompt,
                request.ai_response,
                request.search_context,
                request.connected_nodes
            )
            results["pdf_content"] = pdf_result.get("content", "")
        
        # Generate DALL-E image
        if "image" in request.modalities:
            image_result = await generate_dalle_image(
                gpt_service,
                request.user_prompt,
                request.ai_response,
                request.search_context,
                request.connected_nodes
            )
            results["image_prompt"] = image_result.get("prompt", "")
            results["image_url"] = image_result.get("image_data", "")
        
        return MultiGenResponse(**results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-gen generation failed: {str(e)}")

async def generate_enterprise_pdf(
    gpt_service: GPTService,
    user_prompt: str,
    ai_response: str,
    search_context: List[Dict[str, Any]],
    connected_nodes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate enterprise-grade research analysis report
    """
    
    # Prepare context data
    youtube_context = ""
    search_context_text = ""
    
    # Extract YouTube node data
    for node in connected_nodes:
        if node.get("type") == "youtube":
            youtube_data = node.get("data", {})
            youtube_context += f"Video Title: {youtube_data.get('title', 'N/A')}\n"
            youtube_context += f"Video Description: {youtube_data.get('description', 'N/A')}\n"
            youtube_context += f"Video URL: {youtube_data.get('url', 'N/A')}\n"
            youtube_context += f"Channel: {youtube_data.get('channel_title', 'N/A')}\n"
            youtube_context += f"Duration: {youtube_data.get('duration', 'N/A')}\n"
            youtube_context += f"Published: {youtube_data.get('published_at', 'N/A')}\n"
            youtube_context += f"Video ID: {youtube_data.get('video_id', 'N/A')}\n\n"
    
    # Extract search context
    if search_context:
        search_context_text = "## Grounded Search Results\n\n"
        for i, result in enumerate(search_context[:5], 1):  # Limit to top 5 results
            search_context_text += f"{i}. **{result.get('title', 'N/A')}**\n"
            search_context_text += f"   - URL: {result.get('link', 'N/A')}\n"
            search_context_text += f"   - Snippet: {result.get('snippet', 'N/A')}\n\n"
    
    # Create optimized PDF prompt for faster generation
    pdf_prompt = f"""
Create a concise research analysis report based on:

## User Query
{user_prompt}

## AI Analysis
{ai_response}

## YouTube Context
{youtube_context}

{search_context_text}

## Report Structure
Generate a professional report with:

1. **Executive Summary** - Key findings (2-3 sentences)
2. **Key Findings** - Main insights from YouTube content
3. **Analysis** - Detailed examination of the research
4. **Recommendations** - Actionable next steps
5. **References** - Sources and citations

Keep it concise (400-600 words), well-structured with clear headings and bullet points. Focus on actionable insights relevant to the YouTube content.
"""

    try:
        pdf_content = await gpt_service._generate_response(pdf_prompt)
        
        # Generate actual PDF using pdf_agent
        pdf_result = await pdf_agent.generate_pdf(
            content=pdf_content,
            title=f"Research Analysis: {user_prompt[:50]}...",
            include_images=[]
        )
        
        if pdf_result.get("success"):
            return {
                "success": True,
                "content": pdf_content,
                "pdf_data": pdf_result.get("pdf_data", ""),
                "filename": pdf_result.get("filename", "research_report.pdf")
            }
        else:
            # Fallback to content only
            return {
                "success": True,
                "content": pdf_content,
                "pdf_data": "",
                "filename": "research_report.txt"
            }
            
    except Exception as e:
        # Fallback to basic formatting
        fallback_content = f"""
# Research Analysis Report

## Executive Summary
{ai_response}

## Methodology
Analysis based on AI processing of user query with contextual data from connected nodes.

## Key Findings
{ai_response}

## Data Sources
- User Query: {user_prompt}
- YouTube Context: {youtube_context}
- Search Results: {len(search_context)} sources analyzed

## Recommendations
Based on the analysis, consider the following recommendations:
1. Review the findings in detail
2. Validate insights with additional research
3. Implement actionable next steps

## References
- AI Analysis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Data Sources: {len(connected_nodes)} connected nodes
- Search Results: {len(search_context)} sources
"""
        
        return {
            "success": True,
            "content": fallback_content,
            "pdf_data": "",
            "filename": "research_report.txt"
        }

async def generate_dalle_image(
    gpt_service: GPTService,
    user_prompt: str,
    ai_response: str,
    search_context: List[Dict[str, Any]],
    connected_nodes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate detailed prompt for DALL-E and create HD image using image_agent
    """
    
    # Create detailed image prompt
    image_prompt_text = f"""
Create a detailed, high-quality image prompt for DALL-E based on this research analysis:

User Query: {user_prompt}
AI Response: {ai_response}

The image should be:
- High-definition and professional
- Visually representing the research topic
- Contextually relevant to the analysis
- Suitable for a research report or presentation
- Professional and enterprise-grade quality

Generate a detailed, descriptive prompt that DALL-E can use to create a high-quality image.
"""
    
    try:
        # Get detailed image prompt from GPT
        image_prompt = await gpt_service.generate_text(image_prompt_text)
        
        # Generate image using DALL-E 2 via image_agent
        image_result = await image_agent.generate_image(image_prompt, style="realistic")
        
        if image_result.get("success"):
            return {
                "success": True,
                "prompt": image_prompt,
                "image_data": f"data:image/jpeg;base64,{image_result['image_data']}",
                "filename": image_result.get("filename", "generated_image.jpg")
            }
        else:
            raise Exception("Image generation failed")
        
    except Exception as e:
        # Fallback image prompt
        fallback_prompt = f"Professional research analysis visualization for: {user_prompt[:100]}"
        try:
            image_result = await image_agent.generate_image(fallback_prompt, style="realistic")
            if image_result.get("success"):
                return {
                    "success": True,
                    "prompt": fallback_prompt,
                    "image_data": f"data:image/jpeg;base64,{image_result['image_data']}",
                    "filename": image_result.get("filename", "fallback_image.jpg")
                }
        except:
            pass
        
        # Return placeholder
        return {
            "success": False,
            "prompt": fallback_prompt,
            "image_data": "https://via.placeholder.com/1024x1024?text=Image+Generation+Failed",
            "filename": "placeholder.jpg"
        }

@router.post("/generate-pdf")
async def generate_pdf_download(request: MultiGenRequest):
    """
    Generate and download actual PDF file
    """
    try:
        # Use the existing GPT service instance
        from app.services.gpt_service import gpt_service
        
        # Generate enterprise-grade PDF content
        pdf_result = await generate_enterprise_pdf(
            gpt_service,
            request.user_prompt,
            request.ai_response,
            request.search_context,
            request.connected_nodes
        )
        
        if pdf_result.get("success") and pdf_result.get("pdf_data"):
            from fastapi.responses import Response
            import base64
            
            # Decode base64 PDF data
            pdf_bytes = base64.b64decode(pdf_result["pdf_data"])
            
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={pdf_result.get('filename', 'research_report.pdf')}"
                }
            )
        else:
            raise HTTPException(status_code=500, detail="PDF generation failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF download failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check for multi-gen service"""
    return {"status": "healthy", "service": "multi-gen"}
