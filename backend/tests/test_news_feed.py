"""
test_news_feed.py
=================
Tests for the Live News Feed aggregation service, SSRF protection,
feed parsing, deduplication, caching, and FastAPI endpoints.
"""

import sys
import os
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.news_feed_service import (
    validate_url_safe,
    _parse_xml_feed,
    _normalize_title_key,
    _make_article_id,
    get_available_sources,
)
from app.schemas.news import NewsFeedResponse


# ============================================================================
# 1. SSRF Protection Tests
# ============================================================================

class TestSSRFProtection:
    def test_blocks_localhost(self):
        with pytest.raises(ValueError, match="Access to localhost is prohibited"):
            validate_url_safe("http://localhost:8000/api/health")

    def test_blocks_loopback_ip(self):
        with pytest.raises(ValueError, match="Access to localhost is prohibited"):
            validate_url_safe("http://127.0.0.1/admin")

    def test_blocks_aws_metadata_ip(self):
        with pytest.raises(ValueError, match="SSRF Protection"):
            validate_url_safe("http://169.254.169.254/latest/meta-data/")

    def test_blocks_private_rfc1918_ips(self):
        for ip in ("10.0.0.1", "192.168.1.1", "172.16.0.1"):
            with pytest.raises(ValueError, match="SSRF Protection"):
                validate_url_safe(f"http://{ip}/secret")

    def test_blocks_unsupported_schemes(self):
        for scheme in ("ftp://example.com", "file:///etc/passwd", "gopher://example.com"):
            with pytest.raises(ValueError, match="Unsupported URL scheme"):
                validate_url_safe(scheme)

    def test_accepts_valid_public_https(self):
        # Public domains that resolve to global public IPs
        url = "https://www.bbc.com/news"
        safe = validate_url_safe(url)
        assert safe == url


# ============================================================================
# 2. XML / Atom Parser Tests
# ============================================================================

class TestXMLFeedParsing:
    SAMPLE_RSS_2 = b"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>BBC News - World</title>
        <link>https://www.bbc.co.uk/news/</link>
        <description>BBC News world section</description>
        <item>
          <title><![CDATA[Global climate summit reaches historic agreement]]></title>
          <link>https://www.bbc.com/news/world-12345</link>
          <description><![CDATA[Delegates from 190 nations have reached a comprehensive agreement on emissions.]]></description>
          <pubDate>Wed, 28 Oct 2026 12:00:00 GMT</pubDate>
        </item>
        <item>
          <title>Second World Headline &amp; Analysis</title>
          <link>https://www.bbc.com/news/world-67890</link>
          <description>Summary of the second article with &lt;b&gt;HTML&lt;/b&gt; tags.</description>
          <pubDate>Wed, 28 Oct 2026 13:00:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """

    SAMPLE_ATOM = b"""<?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <title>WHO News Releases</title>
      <link href="https://www.who.int" rel="alternate"/>
      <entry>
        <title>WHO announces updated health emergency guidelines</title>
        <link href="https://www.who.int/news/item/28-10-2026-guidelines" rel="alternate"/>
        <summary>New global health response protocols released today.</summary>
        <updated>2026-10-28T14:30:00Z</updated>
      </entry>
    </feed>
    """

    def test_parse_rss_2(self):
        src = {"id": "bbc_world", "name": "BBC News (World)", "category": "World"}
        articles = _parse_xml_feed(src, self.SAMPLE_RSS_2)
        assert len(articles) == 2
        assert articles[0].headline == "Global climate summit reaches historic agreement"
        assert articles[0].url == "https://www.bbc.com/news/world-12345"
        assert articles[0].publisher == "BBC News (World)"
        assert articles[0].category == "World"
        assert "190 nations" in articles[0].summary
        # Second item HTML stripped
        assert "<b>" not in articles[1].summary
        assert "HTML" in articles[1].summary

    def test_parse_atom(self):
        src = {"id": "who_news", "name": "WHO News", "category": "Health"}
        articles = _parse_xml_feed(src, self.SAMPLE_ATOM)
        assert len(articles) == 1
        assert articles[0].headline == "WHO announces updated health emergency guidelines"
        assert articles[0].url == "https://www.who.int/news/item/28-10-2026-guidelines"
        assert articles[0].publisher == "WHO News"
        assert articles[0].category == "Health"
        assert articles[0].published_at == "2026-10-28T14:30:00Z"

    def test_malformed_xml_handled_gracefully(self):
        src = {"id": "test", "name": "Test", "category": "General"}
        with pytest.raises(Exception):
            _parse_xml_feed(src, b"<broken><xml>no end tag")


# ============================================================================
# 3. Deduplication & Helper Tests
# ============================================================================

class TestFeedDeduplication:
    def test_title_key_normalization(self):
        k1 = _normalize_title_key("Breaking: Climate Deal Signed in Geneva!!")
        k2 = _normalize_title_key("breaking climate deal signed in geneva")
        assert k1 == k2

    def test_article_id_is_deterministic(self):
        id1 = _make_article_id("https://bbc.com/news/1", "Headline")
        id2 = _make_article_id("https://bbc.com/news/1", "Headline")
        assert id1 == id2
        assert id1.startswith("ART-")

    def test_sources_list_returns_configured_sources(self):
        sources = get_available_sources()
        assert len(sources) >= 8
        source_ids = {s["id"] for s in sources}
        assert "bbc_world" in source_ids
        assert "who_news" in source_ids
        assert "gdelt" in source_ids


# ============================================================================
# 4. FastAPI Endpoint Integration Tests
# ============================================================================

class TestNewsFeedEndpoints:
    @pytest.fixture(scope="class")
    def client(self):
        try:
            from fastapi.testclient import TestClient
            from main import app
            return TestClient(app)
        except ImportError:
            pytest.skip("TestClient / httpx not installed.")

    def test_sources_endpoint(self, client):
        res = client.get("/api/news/sources")
        assert res.status_code == 200
        sources = res.json()
        assert isinstance(sources, list)
        assert len(sources) >= 8

    def test_feed_endpoint_schema(self, client):
        # Uses local cache or mock
        res = client.get("/api/news/feed?limit=5")
        assert res.status_code == 200
        data = res.json()
        assert "articles" in data
        assert "total" in data
        assert "sources" in data
        assert "categories" in data
        assert isinstance(data["articles"], list)
        assert isinstance(data["sources"], list)

    def test_fetch_article_empty_url_returns_400(self, client):
        res = client.post("/api/news/fetch-article", json={"url": ""})
        assert res.status_code == 400

    def test_fetch_article_ssrf_blocked_safely(self, client):
        res = client.post(
            "/api/news/fetch-article",
            json={"url": "http://169.254.169.254/meta"}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["has_full_text"] is False
        assert "SSRF Protection" in data["note"] or "Invalid or restricted" in data["note"]
