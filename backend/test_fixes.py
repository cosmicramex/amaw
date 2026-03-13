#!/usr/bin/env python3
"""
Test the fixes for multi-gen workflow
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_fixes():
    """Test the fixes for multi-gen workflow"""
    print("🔧 Testing Multi-Gen Fixes")
    print("="*50)
    
    # Test 1: Multi-Gen API
    print("\n1. Testing Multi-Gen API...")
    try:
        from fastapi.testclient import TestClient
        import main as main_module
        
        client = TestClient(main_module.app)
        
        # Test health endpoint
        health_response = client.get("/api/multi-gen/health")
        print(f"   Health check: {health_response.status_code}")
        
        # Test generate endpoint
        test_request = {
            "user_prompt": "Test prompt for fixes",
            "ai_response": "Test AI response for fixes",
            "search_context": [],
            "connected_nodes": [],
            "modalities": ["pdf", "image"]
        }
        
        response = client.post("/api/multi-gen/generate", json=test_request)
        print(f"   Generate endpoint: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success', False)}")
            print(f"   Has PDF content: {bool(result.get('pdf_content'))}")
            print(f"   Has image URL: {bool(result.get('image_url'))}")
            print("   ✅ Multi-Gen API working")
        else:
            print(f"   ❌ Multi-Gen API failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Multi-Gen API error: {e}")
    
    # Test 2: Image Agent
    print("\n2. Testing Image Agent...")
    try:
        from app.services.image_agent import image_agent
        result = await image_agent.generate_image("Test image for fixes", "realistic")
        
        if result.get("success"):
            print("   ✅ Image Agent working")
            print(f"   Model: {result.get('model', 'unknown')}")
            print(f"   Has image data: {bool(result.get('image_data'))}")
        else:
            print(f"   ❌ Image Agent failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ Image Agent error: {e}")
    
    # Test 3: PDF Agent
    print("\n3. Testing PDF Agent...")
    try:
        from app.services.pdf_agent import pdf_agent
        result = await pdf_agent.generate_pdf("# Test PDF\nThis is a test PDF for fixes.", "Test Document")
        
        if result.get("success"):
            print("   ✅ PDF Agent working")
            print(f"   Filename: {result.get('filename', 'unknown')}")
            print(f"   Has PDF data: {bool(result.get('pdf_data'))}")
        else:
            print(f"   ❌ PDF Agent failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ PDF Agent error: {e}")
    
    print("\n" + "="*50)
    print("🎉 Fix testing complete!")

if __name__ == "__main__":
    asyncio.run(test_fixes())
