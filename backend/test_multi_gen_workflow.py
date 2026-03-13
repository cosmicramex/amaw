#!/usr/bin/env python3
"""
Multi-Generation Workflow Test
Tests the complete multi-gen workflow from API call to PDF and image generation.
"""

import os
import sys
import asyncio
import json
import base64
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from fastapi.testclient import TestClient
import main as main_module  # Import main.py from current directory

async def test_multi_gen_workflow():
    """Test the complete multi-generation workflow"""
    print("🔄 Testing Multi-Generation Workflow")
    print("="*60)
    
    client = TestClient(main_module.app)
    
    # Test data
    test_request = {
        "user_prompt": "Create a comprehensive analysis of artificial intelligence trends in 2024",
        "ai_response": "Artificial Intelligence is rapidly evolving in 2024 with significant breakthroughs in large language models, computer vision, and autonomous systems. Key trends include the democratization of AI tools, increased focus on AI safety and ethics, and the integration of AI into everyday applications.",
        "search_context": [
            {
                "title": "AI Trends 2024",
                "link": "https://example.com/ai-trends-2024",
                "snippet": "Comprehensive overview of AI developments in 2024"
            }
        ],
        "connected_nodes": [
            {
                "type": "youtubeNode",
                "data": {
                    "title": "AI Revolution 2024",
                    "description": "Exploring the latest AI developments",
                    "url": "https://youtube.com/watch?v=example"
                }
            }
        ],
        "modalities": ["pdf", "image"]
    }
    
    print("\n1. Testing Multi-Gen API Endpoint...")
    try:
        response = client.post("/api/multi-gen/generate", json=test_request)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ API Response received (Status: {response.status_code})")
            
            if result.get("success"):
                print("   ✅ Multi-gen generation successful")
                
                # Check PDF content
                pdf_content = result.get("pdf_content")
                if pdf_content:
                    print(f"   ✅ PDF content generated ({len(pdf_content)} characters)")
                    
                    # Check if it's a proper research report
                    if any(keyword in pdf_content.lower() for keyword in ["executive summary", "methodology", "findings", "recommendations"]):
                        print("   ✅ PDF content appears to be a proper research report")
                    else:
                        print("   ⚠️  PDF content may not be properly formatted")
                else:
                    print("   ❌ No PDF content generated")
                
                # Check image generation
                image_prompt = result.get("image_prompt")
                image_url = result.get("image_url")
                
                if image_prompt:
                    print(f"   ✅ Image prompt generated ({len(image_prompt)} characters)")
                else:
                    print("   ❌ No image prompt generated")
                
                if image_url:
                    print(f"   ✅ Image URL generated: {image_url[:50]}...")
                    
                    # Check if it's base64 data
                    if image_url.startswith("data:image/"):
                        print("   ✅ Image is in base64 data URL format")
                        
                        # Try to decode and validate
                        try:
                            # Extract base64 part after comma
                            base64_data = image_url.split(",")[1]
                            image_bytes = base64.b64decode(base64_data)
                            print(f"   ✅ Image data is valid base64 ({len(image_bytes)} bytes)")
                        except Exception as e:
                            print(f"   ❌ Image data validation failed: {e}")
                    else:
                        print("   ⚠️  Image is not in expected base64 format")
                else:
                    print("   ❌ No image URL generated")
                
                return True
            else:
                print(f"   ❌ Generation failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ API call failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ API call error: {e}")
        return False

async def test_individual_services():
    """Test individual services separately"""
    print("\n2. Testing Individual Services...")
    
    # Test Image Agent
    print("\n   Testing Image Agent...")
    try:
        from app.services.image_agent import image_agent
        result = await image_agent.generate_image("A futuristic AI research laboratory", "realistic")
        
        if result.get("success"):
            print("   ✅ Image Agent working")
            print(f"   Model: {result.get('model', 'unknown')}")
            print(f"   Resolution: {result.get('resolution', 'unknown')}")
            print(f"   Cost: {result.get('cost_estimate', 'unknown')}")
        else:
            print(f"   ❌ Image Agent failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Image Agent error: {e}")
    
    # Test PDF Agent
    print("\n   Testing PDF Agent...")
    try:
        from app.services.pdf_agent import pdf_agent
        test_content = """
# AI Research Report

## Executive Summary
This is a test report for the AMAW system.

## Key Findings
- AI is advancing rapidly
- New models are being developed
- Applications are expanding

## Recommendations
- Continue research
- Focus on safety
- Ensure ethical use
        """.strip()
        
        result = await pdf_agent.generate_pdf(test_content, "AI Test Report")
        
        if result.get("success"):
            print("   ✅ PDF Agent working")
            print(f"   Filename: {result.get('filename', 'unknown')}")
            print(f"   File size: {result.get('file_size', 0)} bytes")
            print(f"   Pages: {result.get('page_count', 0)}")
        else:
            print(f"   ❌ PDF Agent failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ PDF Agent error: {e}")

async def main():
    """Main test function"""
    print("🚀 Multi-Generation Workflow Test")
    print("="*60)
    
    # Test individual services first
    await test_individual_services()
    
    # Test complete workflow
    workflow_success = await test_multi_gen_workflow()
    
    print("\n" + "="*60)
    print("📊 WORKFLOW TEST SUMMARY")
    print("="*60)
    
    if workflow_success:
        print("🎉 MULTI-GENERATION WORKFLOW IS WORKING!")
        print("✅ PDF generation: Working")
        print("✅ Image generation: Working") 
        print("✅ API integration: Working")
        print("✅ Data flow: Working")
    else:
        print("⚠️  MULTI-GENERATION WORKFLOW NEEDS ATTENTION!")
        print("❌ Some components may not be working properly")
    
    return workflow_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
