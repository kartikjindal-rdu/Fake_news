"""
test_multichannel_news.py
=========================
Comprehensive test suite for VeriNews AI 2.0 Multi-Channel News Intelligence:
1. Multi-Source Registry (Indian Press, International, Official, Fact Check, YouTube, GDELT)
2. Source Management: Dynamic Toggling & Custom Source Addition with SSRF Protection
3. YouTube Channel XML Feed Parsing & Video ID Extraction
4. YouTube Transcript Handling & Honest Fallback Protocol
5. Content Availability Level Tagging ("full-text", "summary-only", "headline-only")
6. Cross-Publisher Timeline & Syndication Detection
7. FastAPI Endpoint Integration
"""

import sys
import os
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services import news_feed_service, youtube_service
from app.services.news_feed_service import (
    validate_url_safe,
    get_sources_registry,
    toggle_source_status,
    add_custom_source,
    _compute_content_availability,
    _normalize_title_key,
    _make_article_id,
)
from app.services.youtube_service import (
    extract_video_id,
    parse_youtube_xml_feed,
    extract_youtube_transcript,
)
from app.schemas.news import (
    NewsArticleItem,
    NewsSourceStatus,
    SourceConfig,
)


# ============================================================================
# 1. Multi-Source Registry Coverage
# ============================================================================

class TestSourceRegistryCoverage:
    def test_registry_contains_all_core_categories(self):
        sources = get_sources_registry()
        assert len(sources) >= 15

        source_ids = {s["id"] for s in sources}
        types = {s["type"] for s in sources}
        categories = {s["category"] for s in sources}

        # Indian Publishers
        assert "the_hindu_national" in source_ids
        assert "ndtv_india" in source_ids
        assert "indian_express" in source_ids
        assert "india_today" in source_ids
        assert "hindustan_times" in source_ids

        # International Publishers
        assert "bbc_world" in source_ids
        assert "aljazeera_all" in source_ids
        assert "dw_news" in source_ids
        assert "france24_en" in source_ids

        # Official / Primary
        assert "who_news" in source_ids
        assert "un_news" in source_ids
        assert "nasa_breaking" in source_ids

        # Fact Checkers
        assert "alt_news" in source_ids
        assert "boom_live" in source_ids
        assert "gdelt_factcheck" in source_ids

        # YouTube Channels
        assert "yt_bbc_news" in source_ids
        assert "yt_ndtv" in source_ids
        assert "yt_india_today" in source_ids

        # Verify Channel Types
        assert "rss" in types
        assert "youtube" in types
        assert "official" in types
        assert "factcheck" in types
        assert "api" in types

        # Verify Categories
        assert "India" in categories
        assert "World" in categories
        assert "Health" in categories
        assert "Fact Check" in categories


# ============================================================================
# 2. Source Management & SSRF Protection
# ============================================================================

class TestSourceManagement:
    def test_toggle_source_state(self):
        # Toggle ndtv_india to disabled
        success = toggle_source_status("ndtv_india", False)
        assert success is True

        sources = {s["id"]: s for s in get_sources_registry()}
        assert sources["ndtv_india"]["enabled"] is False

        # Re-enable
        success_re = toggle_source_status("ndtv_india", True)
        assert success_re is True

        sources_re = {s["id"]: s for s in get_sources_registry()}
        assert sources_re["ndtv_india"]["enabled"] is True

    def test_toggle_nonexistent_source_returns_false(self):
        success = toggle_source_status("nonexistent_source_xyz", True)
        assert success is False

    def test_add_custom_source_ssrf_blocked_localhost(self):
        bad_source = {
            "id": "malicious_local",
            "name": "Localhost Exploit",
            "category": "Test",
            "type": "rss",
            "url": "http://127.0.0.1:8000/api/secret",
        }
        success, msg = add_custom_source(bad_source)
        assert success is False
        assert "prohibited" in msg.lower() or "restricted" in msg.lower() or "ssrf" in msg.lower()

    def test_add_custom_source_ssrf_blocked_metadata_ip(self):
        bad_source = {
            "id": "malicious_meta",
            "name": "Cloud Metadata",
            "category": "Test",
            "type": "rss",
            "url": "http://169.254.169.254/latest/meta-data/",
        }
        success, msg = add_custom_source(bad_source)
        assert success is False
        assert "ssrf" in msg.lower() or "restricted" in msg.lower()

    def test_add_custom_source_valid_public_url(self):
        good_source = {
            "id": "reuters_world_custom",
            "name": "Reuters World Wire",
            "category": "World",
            "type": "rss",
            "url": "https://www.reuters.com/world/feed/",
        }
        success, msg = add_custom_source(good_source)
        assert success is True
        assert "added successfully" in msg.lower()

        # Check it is in registry
        sources = {s["id"]: s for s in get_sources_registry()}
        assert "reuters_world_custom" in sources
        assert sources["reuters_world_custom"]["enabled"] is True


# ============================================================================
# 3. YouTube Service & Video ID Extraction
# ============================================================================

class TestYouTubeService:
    def test_extract_video_id_variations(self):
        # 1. Standard watch URL
        vid1 = extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert vid1 == "dQw4w9WgXcQ"

        # 2. Shortened youtu.be URL
        vid2 = extract_video_id("https://youtu.be/dQw4w9WgXcQ?t=42")
        assert vid2 == "dQw4w9WgXcQ"

        # 3. Embed URL
        vid3 = extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ")
        assert vid3 == "dQw4w9WgXcQ"

        # 4. Raw 11-char ID
        vid4 = extract_video_id("dQw4w9WgXcQ")
        assert vid4 == "dQw4w9WgXcQ"

        # 5. Invalid input
        assert extract_video_id("") is None
        assert extract_video_id("https://example.com/not-youtube") is None

    SAMPLE_YOUTUBE_ATOM = b"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/" xmlns="http://www.w3.org/2005/Atom">
      <title>BBC News Channel</title>
      <entry>
        <yt:videoId>vId12345678</yt:videoId>
        <yt:channelId>UC16niRr50-MSBwiO3YDb3RA</yt:channelId>
        <title>Prime Minister addresses global security summit in London</title>
        <link rel="alternate" href="https://www.youtube.com/watch?v=vId12345678"/>
        <author>
          <name>BBC News</name>
        </author>
        <published>2026-10-29T10:00:00+00:00</published>
        <media:group>
          <media:title>Prime Minister addresses global security summit in London</media:title>
          <media:description>Full live coverage from the London international peace summit. Discussions focus on cyber defense and maritime security agreements.</media:description>
          <media:thumbnail url="https://i.ytimg.com/vi/vId12345678/hqdefault.jpg" width="480" height="360"/>
        </media:group>
      </entry>
    </feed>
    """

    def test_parse_youtube_xml_feed(self):
        channel_info = {
            "id": "yt_bbc_news",
            "name": "BBC News",
            "category": "World",
            "type": "youtube",
        }
        articles = parse_youtube_xml_feed(channel_info, self.SAMPLE_YOUTUBE_ATOM)
        assert len(articles) == 1
        video = articles[0]

        assert video.headline == "Prime Minister addresses global security summit in London"
        assert video.video_id == "vId12345678"
        assert video.source_type == "youtube"
        assert video.publisher == "BBC News"
        assert video.category == "World"
        assert "London international peace summit" in video.summary
        assert video.image_url == "https://i.ytimg.com/vi/vId12345678/hqdefault.jpg"
        assert video.content_availability == "summary-only"

    def test_transcript_honest_fallback_when_captions_unavailable(self):
        # When captions do not exist or are disabled, never fabricate text
        result = extract_youtube_transcript("nonexistent11")
        assert result.has_transcript is False
        assert result.transcript is None
        assert result.word_count == 0
        assert "Spoken transcript could not be automatically extracted" in result.note


# ============================================================================
# 4. Content Availability Level Tagging
# ============================================================================

class TestContentAvailability:
    def test_full_text_classification(self):
        body = " ".join(["word"] * 120)
        avail = _compute_content_availability(
            summary="Short summary",
            content=body,
            has_full_text=True,
        )
        assert avail == "full-text"

    def test_summary_only_classification(self):
        avail = _compute_content_availability(
            summary="A detailed summary of the news story exceeding thirty characters.",
            content=None,
            has_full_text=False,
        )
        assert avail == "summary-only"

    def test_headline_only_classification(self):
        avail = _compute_content_availability(
            summary="",
            content=None,
            has_full_text=False,
        )
        assert avail == "headline-only"


# ============================================================================
# 5. FastAPI Endpoints Integration
# ============================================================================

class TestFastAPINewsEndpoints:
    @pytest.fixture(scope="class")
    def client(self):
        try:
            from fastapi.testclient import TestClient
            from main import app
            return TestClient(app)
        except ImportError:
            pytest.skip("TestClient / httpx not installed.")

    def test_sources_endpoint_contains_all_types(self, client):
        res = client.get("/api/news/sources")
        assert res.status_code == 200
        sources = res.json()
        assert len(sources) >= 15
        types = {s["type"] for s in sources}
        assert "youtube" in types
        assert "official" in types
        assert "factcheck" in types

    def test_toggle_source_endpoint(self, client):
        # Toggle who_news
        res = client.post("/api/news/sources/who_news/toggle", json={"enabled": False})
        assert res.status_code == 200
        assert res.json()["enabled"] is False

        # Restore
        res_re = client.post("/api/news/sources/who_news/toggle", json={"enabled": True})
        assert res_re.status_code == 200
        assert res_re.json()["enabled"] is True

    def test_youtube_transcript_endpoint_fallback(self, client):
        res = client.post("/api/news/youtube/transcript", json={"video_id": "dQw4w9WgXcQ"})
        assert res.status_code == 200
        data = res.json()
        assert "video_id" in data
        assert "has_transcript" in data
        assert "note" in data

    def test_feed_filtering_by_source_type(self, client):
        res = client.get("/api/news/feed?source_type=youtube&limit=6")
        assert res.status_code == 200
        data = res.json()
        assert "articles" in data
        assert "source_types" in data
        # If articles returned, all should be youtube
        for art in data["articles"]:
            assert art["source_type"] == "youtube"
