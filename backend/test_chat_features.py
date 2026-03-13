import asyncio
import os
import sys
import json
from app.services.gpt_service import gpt_service
from app.services.dalle_service import dalle_service

async def test_gpt_service():
    print("\n=== Testing GPT-4o mini Service ===")
    
    # Test text generation
    print("Testing text generation...")
    result = await gpt_service.process_content(
        content_type="text",
        content_data={"text": "This is a test document."},
        user_prompt="Summarize this text."
    )
    
    print(f"Success: {result['success']}")
    print(f"Response: {result['response']}")
    
    # Test multiple nodes processing
    print("\nTesting multiple nodes processing...")
    result = await gpt_service.process_multiple_nodes(
        nodes_data=[
            {"type": "text", "data": {"text": "First document"}},
            {"type": "code", "data": {"language": "python", "code": "print('Hello World')"}}
        ],
        user_prompt="Explain these contents."
    )
    
    print(f"Success: {result['success']}")
    print(f"Response: {result['response']}")
    
    # Test text summarization
    print("\nTesting text summarization...")
    result = await gpt_service.summarize_text(
        "This is a longer text that needs to be summarized. It contains multiple sentences and should be condensed into a shorter version while maintaining the key points. The summary should be concise but informative."
    )
    
    print(f"Success: {result['success']}")
    print(f"Summary: {result['summary']}")
    print(f"Original length: {result['original_length']}")
    print(f"Summary length: {result['summary_length']}")

async def test_dalle_service():
    print("\n=== Testing DALL-E 2 Service ===")
    
    # Test image generation
    print("Testing image generation...")
    result = await dalle_service.generate_image(
        prompt="A beautiful sunset over mountains",
        size="512x512"
    )
    
    print(f"Success: {result['success']}")
    print(f"Image URL: {result['image_url']}")
    
    # Test image variation
    print("\nTesting image variation...")
    result = await dalle_service.generate_variation(
        image_url="https://example.com/image.jpg"  # This is just a placeholder
    )
    
    print(f"Success: {result['success']}")
    print(f"Variation URL: {result['image_url']}")

async def main():
    print("Starting Chat Features Tests")
    print("============================")
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("Tests will run in mock mode.")
    
    try:
        await test_gpt_service()
        await test_dalle_service()
        
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
