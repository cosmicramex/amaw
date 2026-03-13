"""
Integration tests to verify API keys and core endpoints work.

Run from the backend directory:
  pytest -q
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use the lightweight test app that avoids DB deps
from test_backend import app


client = TestClient(app)


def test_root_and_health():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json().get("status") == "running"

    # Test AI health endpoint instead of generic health
    health = client.get("/api/ai/health")
    assert health.status_code == 200
    assert health.json().get("status") == "healthy"


def test_ai_health_and_mock_or_real():
    # This endpoint internally calls OpenAI in health, but the implementation
    # falls back to mock response when OPENAI_API_KEY is missing.
    resp = client.get("/api/ai/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") in {"healthy", "unhealthy"}


def test_ai_process_with_minimal_node():
    payload = {
        "user_prompt": "Summarize the content",
        "nodes": [
            {
                "id": "youtube-1",
                "type": "youtube",
                "data": {
                    "title": "Test Video",
                    "video_id": "lg48Bi9DA54",
                    "channel_title": "Test Channel"
                }
            }
        ],
        "search_context": []
    }

    resp = client.post("/api/ai/process", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["success"] is True
    assert isinstance(data.get("response"), str) and len(data["response"]) > 0


@pytest.mark.skipif(not os.getenv("YOUTUBE_API_KEY"), reason="YOUTUBE_API_KEY not set")
def test_youtube_video_endpoint():
    # Only runs when a valid key is present
    video_id = "lg48Bi9DA54"
    resp = client.get(f"/api/youtube/video/{video_id}")
    
    # Handle API key issues gracefully
    if resp.status_code == 400 and "forbidden" in resp.text.lower():
        pytest.skip(f"YouTube API key is blocked: {resp.text}")
    
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data.get("success") is True
    assert data.get("data", {}).get("video_id") == video_id


