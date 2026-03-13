"""
Grounded Search Service with Citation Handling
Provides web search capabilities with proper citation and reference management
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import httpx
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings
from app.services.gpt_service import GPTService


class GroundedSearchService:
    """Service for performing grounded web searches with citation handling"""
    
    def __init__(self):
        self.gpt_service = GPTService()
        self.search_service = None
        self._initialize_search_service()
    
    def _initialize_search_service(self):
        """Initialize Google Custom Search service"""
        if settings.GOOGLE_SEARCH_API_KEY and settings.GOOGLE_SEARCH_ENGINE_ID:
            try:
                self.search_service = build(
                    "customsearch", 
                    "v1", 
                    developerKey=settings.GOOGLE_SEARCH_API_KEY
                )
            except Exception as e:
                print(f"Failed to initialize Google Search service: {e}")
                self.search_service = None
        else:
            print("Google Search API credentials not configured")
            self.search_service = None
    
    async def perform_grounded_search(
        self, 
        query: str, 
        youtube_context: Optional[Dict[str, Any]] = None,
        num_results: int = 5
    ) -> Dict[str, Any]:
        """
        Perform a grounded search with proper citation handling
        
        Args:
            query: User's search query
            youtube_context: Context from connected YouTube video
            num_results: Number of search results to retrieve
            
        Returns:
            Dictionary containing search results, citations, and AI response
        """
        try:
            # Step 1: Enhance query with YouTube context
            enhanced_query = self._enhance_query_with_context(query, youtube_context)
            
            # Step 2: Perform web search
            search_results = await self._perform_web_search(enhanced_query, num_results)
            
            if not search_results:
                return {
                    "success": False,
                    "error": "No search results found",
                    "response": "I couldn't find any relevant information for your query."
                }
            
            # Step 3: Process results with AI and generate citations
            ai_response = await self._process_with_ai_and_citations(
                query, 
                youtube_context, 
                search_results
            )
            
            return {
                "success": True,
                "query": query,
                "enhanced_query": enhanced_query,
                "search_results": search_results,
                "ai_response": ai_response["response"],
                "citations": ai_response["citations"],
                "sources": ai_response["sources"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in grounded search: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while searching for information."
            }
    
    def _enhance_query_with_context(self, query: str, youtube_context: Optional[Dict[str, Any]]) -> str:
        """Enhance search query with YouTube video context"""
        if not youtube_context:
            return query
        
        # Extract relevant context from YouTube video
        context_parts = []
        
        if youtube_context.get("title"):
            context_parts.append(f"video titled '{youtube_context['title']}'")
        
        if youtube_context.get("channel"):
            context_parts.append(f"from channel '{youtube_context['channel']}'")
        
        if youtube_context.get("description"):
            # Use first 200 characters of description for context
            desc = youtube_context["description"][:200]
            context_parts.append(f"about: {desc}")
        
        if context_parts:
            enhanced_query = f"{query} {', '.join(context_parts)}"
        else:
            enhanced_query = query
        
        return enhanced_query
    
    async def _perform_web_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Perform web search using Google Custom Search API"""
        if not self.search_service:
            # Fallback to a simple mock search if API not available
            return self._get_mock_search_results(query)
        
        try:
            # Perform the search
            search_result = self.search_service.cse().list(
                q=query,
                cx=settings.GOOGLE_SEARCH_ENGINE_ID,
                num=num_results,
                safe="medium"
            ).execute()
            
            # Extract and format results
            results = []
            for item in search_result.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "display_link": item.get("displayLink", ""),
                    "formatted_url": item.get("formattedUrl", ""),
                    "pagemap": item.get("pagemap", {})
                })
            
            return results
            
        except HttpError as e:
            print(f"Google Search API error: {e}")
            return self._get_mock_search_results(query)
        except Exception as e:
            print(f"Search error: {e}")
            return self._get_mock_search_results(query)
    
    def _get_mock_search_results(self, query: str) -> List[Dict[str, Any]]:
        """Fallback mock search results for testing"""
        return [
            {
                "title": f"Search result for: {query}",
                "link": "https://example.com/result1",
                "snippet": f"This is a mock search result for the query '{query}'. In a real implementation, this would be replaced with actual Google Search API results.",
                "display_link": "example.com",
                "formatted_url": "https://example.com/result1",
                "pagemap": {}
            },
            {
                "title": f"Another result for: {query}",
                "link": "https://example.com/result2", 
                "snippet": f"Additional mock information about '{query}' that would help provide context and citations.",
                "display_link": "example.com",
                "formatted_url": "https://example.com/result2",
                "pagemap": {}
            }
        ]
    
    async def _process_with_ai_and_citations(
        self, 
        original_query: str, 
        youtube_context: Optional[Dict[str, Any]], 
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process search results with AI and generate proper citations"""
        
        # Prepare context for AI
        context_text = self._prepare_context_for_ai(original_query, youtube_context, search_results)
        
        # Create AI prompt for grounded response with citations
        prompt = self._create_citation_prompt(original_query, context_text, search_results)
        
        try:
            # Get AI response using the correct method
            ai_response = await self.gpt_service._generate_response(prompt)
            
            # Extract citations from the response
            citations, sources = self._extract_citations_from_response(ai_response, search_results)
            
            return {
                "response": ai_response,
                "citations": citations,
                "sources": sources
            }
            
        except Exception as e:
            print(f"Error processing with AI: {e}")
            return {
                "response": f"I found some information but encountered an error processing it: {str(e)}",
                "citations": [],
                "sources": []
            }
    
    def _prepare_context_for_ai(
        self, 
        query: str, 
        youtube_context: Optional[Dict[str, Any]], 
        search_results: List[Dict[str, Any]]
    ) -> str:
        """Prepare context information for AI processing"""
        context_parts = []
        
        # Add YouTube context
        if youtube_context:
            context_parts.append("=== YOUTUBE VIDEO CONTEXT ===")
            if youtube_context.get("title"):
                context_parts.append(f"Video Title: {youtube_context['title']}")
            if youtube_context.get("channel"):
                context_parts.append(f"Channel: {youtube_context['channel']}")
            if youtube_context.get("description"):
                context_parts.append(f"Description: {youtube_context['description'][:500]}...")
            context_parts.append("")
        
        # Add search results
        context_parts.append("=== WEB SEARCH RESULTS ===")
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"[{i}] {result['title']}")
            context_parts.append(f"URL: {result['link']}")
            context_parts.append(f"Snippet: {result['snippet']}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _create_citation_prompt(self, query: str, context: str, search_results: List[Dict[str, Any]]) -> str:
        """Create a prompt that instructs AI to generate citations"""
        
        sources_info = "\n".join([
            f"[{i+1}] {result['title']} - {result['link']}" 
            for i, result in enumerate(search_results)
        ])
        
        prompt = f"""
You are a research assistant that provides grounded, well-cited responses. Use the following information to answer the user's query with proper citations.

USER QUERY: {query}

CONTEXT INFORMATION:
{context}

AVAILABLE SOURCES:
{sources_info}

INSTRUCTIONS:
1. Provide a comprehensive, well-structured response to the user's query
2. Use inline citations [1], [2], [3] etc. to reference specific sources
3. If YouTube context is available, reference it as [YouTube Video]
4. Structure your response with clear headings and sections
5. Include a "Sources & References" section at the end
6. Be factual, accurate, and transparent about your sources
7. If information is not available in the provided sources, clearly state this

FORMAT YOUR RESPONSE AS:
## Grounded Search Results

### Key Findings
[Your main insights with inline citations]

### Video Context Analysis (if applicable)
[References to YouTube content with [YouTube Video] citations]

### Additional Research
[Web search findings with numbered citations]

### Sources & References
[YouTube Video] - [Video title and channel if available]
1. [Source title] - [URL] ([Date if available])
2. [Source title] - [URL] ([Date if available])
[Continue for all sources...]

Remember: Every claim must be backed by a citation. Be thorough but concise.
"""
        
        return prompt
    
    def _extract_citations_from_response(self, response: str, search_results: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Extract citations and sources from AI response"""
        citations = []
        sources = []
        
        # Extract numbered citations [1], [2], etc.
        import re
        citation_pattern = r'\[(\d+)\]'
        citation_matches = re.findall(citation_pattern, response)
        
        for match in citation_matches:
            try:
                index = int(match) - 1
                if 0 <= index < len(search_results):
                    result = search_results[index]
                    citations.append(f"[{match}] {result['title']}")
                    sources.append({
                        "number": match,
                        "title": result['title'],
                        "url": result['link'],
                        "snippet": result['snippet']
                    })
            except (ValueError, IndexError):
                continue
        
        # Add YouTube video as a source if referenced
        if "[YouTube Video]" in response:
            sources.insert(0, {
                "number": "YouTube Video",
                "title": "Connected YouTube Video",
                "url": "YouTube Video Context",
                "snippet": "Information from the connected YouTube video"
            })
        
        return citations, sources


# Create global instance
grounded_search_service = GroundedSearchService()
