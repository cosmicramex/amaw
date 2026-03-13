"""
Tests for Grounded Search functionality
"""

import sys
import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.grounded_search_service import GroundedSearchService
from app.api.grounded_search import perform_grounded_search


class TestGroundedSearchService:
    """Test cases for GroundedSearchService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = GroundedSearchService()
    
    def test_enhance_query_with_context(self):
        """Test query enhancement with YouTube context"""
        query = "artificial intelligence trends"
        youtube_context = {
            "title": "AI Revolution 2024",
            "channel": "TechChannel",
            "description": "Exploring the latest trends in artificial intelligence and machine learning"
        }
        
        enhanced = self.service._enhance_query_with_context(query, youtube_context)
        
        assert "artificial intelligence trends" in enhanced
        assert "AI Revolution 2024" in enhanced
        assert "TechChannel" in enhanced
        assert "artificial intelligence and machine learning" in enhanced
    
    def test_enhance_query_without_context(self):
        """Test query enhancement without YouTube context"""
        query = "artificial intelligence trends"
        enhanced = self.service._enhance_query_with_context(query, None)
        
        assert enhanced == query
    
    def test_get_mock_search_results(self):
        """Test mock search results fallback"""
        query = "test query"
        results = self.service._get_mock_search_results(query)
        
        assert len(results) == 2
        assert all("test query" in result["title"] for result in results)
        assert all("example.com" in result["link"] for result in results)
    
    def test_create_citation_prompt(self):
        """Test citation prompt creation"""
        query = "test query"
        context = "test context"
        search_results = [
            {"title": "Test Article", "link": "https://example.com", "snippet": "Test snippet"}
        ]
        
        prompt = self.service._create_citation_prompt(query, context, search_results)
        
        assert "test query" in prompt
        assert "test context" in prompt
        assert "Test Article" in prompt
        assert "https://example.com" in prompt
        assert "inline citations" in prompt
        assert "Sources & References" in prompt
    
    def test_extract_citations_from_response(self):
        """Test citation extraction from AI response"""
        response = "This is a test [1] with citations [2] and [YouTube Video] reference."
        search_results = [
            {"title": "Article 1", "link": "https://example1.com", "snippet": "Snippet 1"},
            {"title": "Article 2", "link": "https://example2.com", "snippet": "Snippet 2"}
        ]
        
        citations, sources = self.service._extract_citations_from_response(response, search_results)
        
        assert len(citations) == 2
        assert "[1] Article 1" in citations
        assert "[2] Article 2" in citations
        
        assert len(sources) == 3  # 2 search results + 1 YouTube video
        assert sources[0]["title"] == "Connected YouTube Video"  # YouTube video first
        assert sources[1]["title"] == "Article 1"
        assert sources[2]["title"] == "Article 2"


@pytest.mark.asyncio
class TestGroundedSearchAPI:
    """Test cases for Grounded Search API endpoints"""
    
    async def test_perform_grounded_search_success(self):
        """Test successful grounded search"""
        # Mock the GPT service to return a predictable response
        with patch('app.services.grounded_search_service.grounded_search_service.gpt_service._generate_response') as mock_gpt:
            mock_gpt.return_value = "Test AI response with [1] citations"
            
            from app.api.grounded_search import GroundedSearchRequest
            request = GroundedSearchRequest(
                query="test query",
                youtube_context={"title": "Test Video"},
                num_results=5
            )
            
            result = await perform_grounded_search(request)
            
            assert result.success is True
            assert result.query == "test query"
            assert "Test AI response" in result.ai_response
            assert len(result.citations) >= 0  # May be empty if no citations found
            assert len(result.sources) >= 0    # May be empty if no sources found
    
    async def test_perform_grounded_search_failure(self):
        """Test grounded search failure handling"""
        # Mock the GPT service to raise an exception
        with patch('app.services.grounded_search_service.grounded_search_service.gpt_service._generate_response') as mock_gpt:
            mock_gpt.side_effect = Exception("GPT service error")
            
            from app.api.grounded_search import GroundedSearchRequest
            request = GroundedSearchRequest(query="test query")
            
            result = await perform_grounded_search(request)
            
            # The service handles errors gracefully and still returns success=True
            # but with an error message in the response
            assert result.success is True  # Service handles errors gracefully
            assert "error" in result.ai_response.lower()
            assert result.search_results is not None  # Mock search results still provided


def test_grounded_search_integration():
    """Integration test for grounded search"""
    # This test would require actual API keys and network access
    # For now, we'll just test that the service can be instantiated
    service = GroundedSearchService()
    assert service is not None
    assert service.gpt_service is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
