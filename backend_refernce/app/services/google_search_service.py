import os
import requests
from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSearchService:
    def __init__(self):
        """Initialize Google Search service with API key"""
        self.api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Search API credentials not found - using mock mode")
            self.mock_mode = True
        else:
            self.mock_mode = False
            logger.info("Google Search service initialized successfully")

    async def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Perform Google Search and return results
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results with title, link, and snippet
        """
        try:
            if self.mock_mode:
                # Return mock search results
                return [
                    {
                        "title": f"Mock Result 1 for '{query}'",
                        "link": "https://example.com/result1",
                        "snippet": f"This is a mock search result for the query: {query}. In production, this would be a real search result from Google."
                    },
                    {
                        "title": f"Mock Result 2 for '{query}'",
                        "link": "https://example.com/result2", 
                        "snippet": f"Another mock search result for: {query}. Add your Google Search API credentials to enable real search."
                    }
                ]
            
            # Google Custom Search API endpoint
            url = "https://www.googleapis.com/customsearch/v1"
            
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10)  # Google API limits to 10 results per request
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract search results
            results = []
            for item in data.get('items', []):
                results.append({
                    "title": item.get('title', ''),
                    "link": item.get('link', ''),
                    "snippet": item.get('snippet', '')
                })
            
            logger.info(f"Google Search completed: {len(results)} results for query '{query}'")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Google Search API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Google Search: {e}")
            return []

    async def search_and_format(self, query: str, num_results: int = 5) -> str:
        """
        Perform Google Search and format results as structured text with citations
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Formatted search results as structured text with citations
        """
        results = await self.search(query, num_results)
        
        if not results:
            return f"No search results found for: {query}"
        
        formatted_results = f"## Web Search Results for: {query}\n\n"
        
        for i, result in enumerate(results, 1):
            formatted_results += f"### [{i}] {result['title']}\n"
            formatted_results += f"**Source:** {result['link']}\n"
            formatted_results += f"**Summary:** {result['snippet']}\n\n"
        
        # Add citation section
        formatted_results += "## References\n"
        for i, result in enumerate(results, 1):
            formatted_results += f"[{i}] {result['title']} - {result['link']}\n"
        
        return formatted_results

# Create global instance
google_search_service = GoogleSearchService()
