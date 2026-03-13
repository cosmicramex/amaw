#!/usr/bin/env python3
"""
Comprehensive API Test Script for AMAW Backend
Tests all major APIs and functions including DALL-E 2, OpenAI GPT, PDF generation, and multi-gen services.
"""

import os
import sys
import asyncio
import json
import base64
import tempfile
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

import pytest
import httpx
from fastapi.testclient import TestClient

# Import our services
from app.services.gpt_service import GPTService
from app.services.image_agent import image_agent
from app.services.pdf_agent import pdf_agent
from app.services.grounded_search_service import GroundedSearchService
from app.api.multi_gen import router as multi_gen_router
import main as main_module

class APITester:
    def __init__(self):
        self.results = []
        self.client = TestClient(main_module.app)
        
    def log_result(self, test_name: str, success: bool, message: str, details: dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")

    def test_environment_setup(self):
        """Test environment variables and basic setup"""
        print("\n🔧 Testing Environment Setup...")
        
        # Check OpenAI API key
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.log_result("OpenAI API Key", True, "API key found", {"length": len(openai_key)})
        else:
            self.log_result("OpenAI API Key", False, "API key not found - using mock mode")
        
        # Check Google Search API key
        google_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        if google_key:
            self.log_result("Google Search API Key", True, "API key found", {"length": len(google_key)})
        else:
            self.log_result("Google Search API Key", False, "API key not found - search will use fallback")
        
        # Check YouTube API key
        youtube_key = os.getenv('YOUTUBE_API_KEY')
        if youtube_key:
            self.log_result("YouTube API Key", True, "API key found", {"length": len(youtube_key)})
        else:
            self.log_result("YouTube API Key", False, "API key not found - YouTube will use fallback")

    async def test_gpt_service(self):
        """Test OpenAI GPT service"""
        print("\n🤖 Testing OpenAI GPT Service...")
        
        try:
            gpt_service = GPTService()
            
            # Test text generation
            test_prompt = "Write a brief summary about artificial intelligence in 2 sentences."
            response = await gpt_service._generate_response(test_prompt)
            
            if response and len(response) > 10:
                self.log_result("GPT Text Generation", True, "Text generated successfully", {
                    "response_length": len(response),
                    "preview": response[:100] + "..." if len(response) > 100 else response
                })
            else:
                self.log_result("GPT Text Generation", False, "Empty or invalid response")
                
        except Exception as e:
            self.log_result("GPT Text Generation", False, f"Error: {str(e)}")

    async def test_dalle_image_generation(self):
        """Test DALL-E 2 image generation"""
        print("\n🎨 Testing DALL-E 2 Image Generation...")
        
        try:
            test_prompt = "A futuristic cityscape at sunset with flying cars"
            result = await image_agent.generate_image(test_prompt, style="realistic")
            
            if result.get("success"):
                self.log_result("DALL-E 2 Image Generation", True, "Image generated successfully", {
                    "model": result.get("model", "unknown"),
                    "resolution": result.get("resolution", "unknown"),
                    "cost_estimate": result.get("cost_estimate", "unknown"),
                    "has_image_data": bool(result.get("image_data")),
                    "filename": result.get("filename", "unknown")
                })
                
                # Test image data validation
                if result.get("image_data"):
                    try:
                        # Check if it's base64 data
                        if result["image_data"].startswith("data:image/"):
                            self.log_result("Image Data Format", True, "Valid base64 data URL format")
                        else:
                            # Try to decode base64
                            base64.b64decode(result["image_data"])
                            self.log_result("Image Data Format", True, "Valid base64 data")
                    except Exception as e:
                        self.log_result("Image Data Format", False, f"Invalid image data: {str(e)}")
            else:
                self.log_result("DALL-E 2 Image Generation", False, f"Generation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.log_result("DALL-E 2 Image Generation", False, f"Error: {str(e)}")

    async def test_pdf_generation(self):
        """Test PDF generation service"""
        print("\n📄 Testing PDF Generation...")
        
        try:
            test_content = """
# Test Research Report

## Executive Summary
This is a test report generated by the AMAW system to verify PDF generation capabilities.

## Key Findings
1. The system is working correctly
2. PDF generation is functional
3. All components are integrated properly

## Methodology
- Test data generation
- PDF creation using ReportLab
- Base64 encoding for web delivery

## Recommendations
- Continue monitoring system performance
- Regular testing of all components
- Maintain API key security

## References
- AMAW System Documentation
- Test Suite Results
- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            result = await pdf_agent.generate_pdf(
                content=test_content,
                title="AMAW Test Report",
                include_images=[]
            )
            
            if result.get("success"):
                self.log_result("PDF Generation", True, "PDF generated successfully", {
                    "filename": result.get("filename", "unknown"),
                    "file_size": result.get("file_size", 0),
                    "page_count": result.get("page_count", 0),
                    "has_pdf_data": bool(result.get("pdf_data"))
                })
                
                # Test PDF data validation
                if result.get("pdf_data"):
                    try:
                        pdf_bytes = base64.b64decode(result["pdf_data"])
                        self.log_result("PDF Data Format", True, f"Valid PDF data ({len(pdf_bytes)} bytes)")
                        
                        # Check if it's actually a PDF (starts with %PDF)
                        if pdf_bytes.startswith(b'%PDF'):
                            self.log_result("PDF File Format", True, "Valid PDF file format")
                        else:
                            self.log_result("PDF File Format", False, "Invalid PDF file format")
                    except Exception as e:
                        self.log_result("PDF Data Format", False, f"Invalid PDF data: {str(e)}")
            else:
                self.log_result("PDF Generation", False, f"Generation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.log_result("PDF Generation", False, f"Error: {str(e)}")

    async def test_grounded_search(self):
        """Test grounded search service"""
        print("\n🔍 Testing Grounded Search Service...")
        
        try:
            search_service = GroundedSearchService()
            
            # Test search functionality
            test_query = "artificial intelligence trends 2024"
            result = await search_service.perform_grounded_search(
                query=test_query,
                youtube_context=None,
                num_results=3
            )
            
            if result.get("success"):
                self.log_result("Grounded Search", True, "Search completed successfully", {
                    "ai_response_length": len(result.get("ai_response", "")),
                    "citations_count": len(result.get("citations", [])),
                    "sources_count": len(result.get("sources", [])),
                    "search_results_count": len(result.get("search_results", []))
                })
            else:
                self.log_result("Grounded Search", False, f"Search failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.log_result("Grounded Search", False, f"Error: {str(e)}")

    def test_multi_gen_api(self):
        """Test multi-generation API endpoints"""
        print("\n🔄 Testing Multi-Generation API...")
        
        try:
            # Test health endpoint
            health_response = self.client.get("/api/multi-gen/health")
            if health_response.status_code == 200:
                self.log_result("Multi-Gen Health Check", True, "Health endpoint working")
            else:
                self.log_result("Multi-Gen Health Check", False, f"Status code: {health_response.status_code}")
            
            # Test multi-gen generation endpoint
            test_request = {
                "user_prompt": "Test prompt for multi-generation",
                "ai_response": "This is a test AI response for multi-generation testing.",
                "search_context": [],
                "connected_nodes": [],
                "modalities": ["pdf", "image"]
            }
            
            response = self.client.post("/api/multi-gen/generate", json=test_request)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("Multi-Gen API", True, "Multi-generation API working", {
                        "has_pdf_content": bool(result.get("pdf_content")),
                        "has_image_prompt": bool(result.get("image_prompt")),
                        "has_image_url": bool(result.get("image_url"))
                    })
                else:
                    self.log_result("Multi-Gen API", False, f"API returned success=False: {result.get('error', 'Unknown error')}")
            else:
                self.log_result("Multi-Gen API", False, f"HTTP error: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Multi-Gen API", False, f"Error: {str(e)}")

    def test_ai_processing_api(self):
        """Test AI processing API"""
        print("\n🧠 Testing AI Processing API...")
        
        try:
            # Test AI processing endpoint
            test_request = {
                "user_prompt": "What is artificial intelligence?",
                "nodes": [],
                "search_context": []
            }
            
            response = self.client.post("/api/ai/process", json=test_request)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("AI Processing API", True, "AI processing working", {
                        "response_length": len(result.get("response", "")),
                        "preview": result.get("response", "")[:100] + "..." if len(result.get("response", "")) > 100 else result.get("response", "")
                    })
                else:
                    self.log_result("AI Processing API", False, f"Processing failed: {result.get('error', 'Unknown error')}")
            else:
                self.log_result("AI Processing API", False, f"HTTP error: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("AI Processing API", False, f"Error: {str(e)}")

    def test_grounded_search_api(self):
        """Test grounded search API"""
        print("\n🔍 Testing Grounded Search API...")
        
        try:
            # Test grounded search endpoint
            test_request = {
                "query": "latest AI developments",
                "youtube_context": None,
                "num_results": 3
            }
            
            response = self.client.post("/api/grounded-search/search", json=test_request)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("Grounded Search API", True, "Grounded search API working", {
                        "ai_response_length": len(result.get("ai_response", "")),
                        "citations_count": len(result.get("citations", [])),
                        "sources_count": len(result.get("sources", []))
                    })
                else:
                    self.log_result("Grounded Search API", False, f"Search failed: {result.get('error', 'Unknown error')}")
            else:
                self.log_result("Grounded Search API", False, f"HTTP error: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Grounded Search API", False, f"Error: {str(e)}")

    def test_youtube_api(self):
        """Test YouTube API"""
        print("\n📺 Testing YouTube API...")
        
        try:
            # Test with a known video ID
            test_video_id = "dQw4w9WgXcQ"  # Rick Roll video (always available)
            response = self.client.get(f"/api/youtube/video/{test_video_id}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("YouTube API", True, "YouTube API working", {
                        "title": result.get("title", "Unknown"),
                        "has_thumbnail": bool(result.get("thumbnail_url")),
                        "has_description": bool(result.get("description"))
                    })
                else:
                    self.log_result("YouTube API", False, f"Video fetch failed: {result.get('error', 'Unknown error')}")
            else:
                self.log_result("YouTube API", False, f"HTTP error: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("YouTube API", False, f"Error: {str(e)}")

    def generate_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE API TEST REPORT")
        print("="*80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 80)
        
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            print(f"   Message: {result['message']}")
            if result['details']:
                for key, value in result['details'].items():
                    print(f"   {key}: {value}")
            print()
        
        # Save results to file
        report_file = f"api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"📄 Detailed report saved to: {report_file}")
        
        return passed_tests == total_tests

async def main():
    """Main test execution function"""
    print("🚀 Starting Comprehensive API Tests for AMAW Backend")
    print("="*80)
    
    tester = APITester()
    
    # Run all tests
    tester.test_environment_setup()
    await tester.test_gpt_service()
    await tester.test_dalle_image_generation()
    await tester.test_pdf_generation()
    await tester.test_grounded_search()
    tester.test_multi_gen_api()
    tester.test_ai_processing_api()
    tester.test_grounded_search_api()
    tester.test_youtube_api()
    
    # Generate final report
    all_passed = tester.generate_report()
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! The AMAW backend is fully functional.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED! Please check the detailed report above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
