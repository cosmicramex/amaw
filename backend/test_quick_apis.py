#!/usr/bin/env python3
"""
Quick API Test Script for AMAW Backend
Quick verification of core APIs and functions.
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_core_services():
    """Test core services quickly"""
    print("🚀 Quick API Test for AMAW Backend")
    print("="*50)
    
    results = []
    
    # Test 1: Environment Setup
    print("\n1. Testing Environment Setup...")
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print("   ✅ OpenAI API key found")
        results.append(("Environment", True))
    else:
        print("   ⚠️  OpenAI API key not found - will use mock mode")
        results.append(("Environment", False))
    
    # Test 2: GPT Service
    print("\n2. Testing GPT Service...")
    try:
        from app.services.gpt_service import GPTService
        gpt_service = GPTService()
        response = await gpt_service._generate_response("Hello, this is a test.")
        if response and len(response) > 5:
            print("   ✅ GPT Service working")
            results.append(("GPT Service", True))
        else:
            print("   ❌ GPT Service failed")
            results.append(("GPT Service", False))
    except Exception as e:
        print(f"   ❌ GPT Service error: {e}")
        results.append(("GPT Service", False))
    
    # Test 3: Image Agent
    print("\n3. Testing Image Agent...")
    try:
        from app.services.image_agent import image_agent
        result = await image_agent.generate_image("A test image", "realistic")
        if result.get("success"):
            print("   ✅ Image Agent working")
            results.append(("Image Agent", True))
        else:
            print("   ❌ Image Agent failed")
            results.append(("Image Agent", False))
    except Exception as e:
        print(f"   ❌ Image Agent error: {e}")
        results.append(("Image Agent", False))
    
    # Test 4: PDF Agent
    print("\n4. Testing PDF Agent...")
    try:
        from app.services.pdf_agent import pdf_agent
        result = await pdf_agent.generate_pdf("# Test PDF\nThis is a test PDF document.", "Test Document")
        if result.get("success"):
            print("   ✅ PDF Agent working")
            results.append(("PDF Agent", True))
        else:
            print("   ❌ PDF Agent failed")
            results.append(("PDF Agent", False))
    except Exception as e:
        print(f"   ❌ PDF Agent error: {e}")
        results.append(("PDF Agent", False))
    
    # Test 5: Multi-Gen API
    print("\n5. Testing Multi-Gen API...")
    try:
        from fastapi.testclient import TestClient
        import main as main_module  # Import main.py from current directory
        
        client = TestClient(main_module.app)
        response = client.get("/api/multi-gen/health")
        if response.status_code == 200:
            print("   ✅ Multi-Gen API working")
            results.append(("Multi-Gen API", True))
        else:
            print("   ❌ Multi-Gen API failed")
            results.append(("Multi-Gen API", False))
    except Exception as e:
        print(f"   ❌ Multi-Gen API error: {e}")
        results.append(("Multi-Gen API", False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 QUICK TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nPassed: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL CORE SERVICES WORKING!")
    else:
        print("\n⚠️  SOME SERVICES NEED ATTENTION!")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(test_core_services())
    sys.exit(0 if success else 1)
