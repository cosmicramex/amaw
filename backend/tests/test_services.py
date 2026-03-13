"""
Service-level tests that bypass HTTP and exercise GPT and YouTube services.
Run: pytest -q
"""

import os
import sys
import pytest

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.gpt_service import gpt_service
from app.services.youtube_service import youtube_service


@pytest.mark.asyncio
async def test_gpt_mock_or_real():
    res = await gpt_service.process_content(
        content_type="text",
        content_data={"text": "Hello from tests"},
        user_prompt="Summarize"
    )
    assert res["success"] is True
    assert isinstance(res.get("response"), str)


@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("YOUTUBE_API_KEY"), reason="YOUTUBE_API_KEY not set")
async def test_youtube_service_info():
    try:
        data = await youtube_service.get_video_info("lg48Bi9DA54")
        assert data.get("video_id") == "lg48Bi9DA54"
        assert "title" in data
    except Exception as e:
        # If API key is invalid or quota exceeded, skip the test
        if "forbidden" in str(e).lower() or "quota" in str(e).lower():
            pytest.skip(f"YouTube API key issue: {str(e)}")
        else:
            raise


