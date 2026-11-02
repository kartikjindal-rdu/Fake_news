"""
news_feed_service.py
====================
Aggregates, normalizes, and caches real-time news articles and video broadcasts
from open-access, multi-channel sources across categories:
1. Indian News Publishers: The Hindu, NDTV, Indian Express, India Today, Hindustan Times.
2. International Publishers & Agencies: BBC News, Al Jazeera, Deutsche Welle, France 24, NPR, Phys.org.
3. Official & Primary Sources: WHO, UN News, NASA Breaking.
4. Fact-Checking Sources: Alt News, BOOM Live, GDELT Fact-Check Wire.
5. YouTube News Channels: BBC News, NDTV, India Today, DW News, Al Jazeera.
6. GDELT DOC 2.0 API: Real-time global open-access news database (no key required).
7. Optional FreshRSS Integration: Self-hosted aggregator if FRESHRSS_URL configured.

Features:
- SSRF-protected HTTP fetching (rejects private, loopback, and local IPs).
- Dynamic Source Registry with enable/disable toggling and custom source registration.
- Explicit Content Availability tagging ("full-text", "summary-only", "headline-only").
- Concurrent multi-source feed retrieval with strict timeouts.
- In-memory thread-safe TTL caching (default: 5 minutes) to respect rate limits.
- Deduplication via normalized headline/URL fingerprinting.
- Safe article body text extraction with fallback to feed synopsis.
"""

import os
import re
import time
import socket
import ipaddress
import hashlib
import logging
import threading
from urllib.parse import urlparse
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Tuple
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

from app.schemas.news import (
    NewsArticleItem,
    NewsSourceStatus,
    NewsFeedResponse,
    FetchArticleResponse,
    SourceConfig,
)
from app.services import youtube_service

logger = logging.getLogger(__name__)

_USER_AGENT = "VeriNewsBot/2.0 (+https://github.com/verinews; multi-channel news verification research)"
_DEFAULT_TIMEOUT = 8.0  # seconds
_CACHE_TTL_SECONDS = 300  # 5 minutes

# In-memory cache
_CACHE_LOCK = threading.Lock()
_CACHE: Dict[str, Any] = {
    "articles": [],
    "sources": [],
    "timestamp": 0.0,
}

# ============================================================================
# MASTER SOURCE CONFIGURATION REGISTRY
# ============================================================================

INITIAL_FEED_SOURCES: List[Dict[str, Any]] = [
    # --- Indian Publishers ---
    {
        "id": "the_hindu_national",
        "name": "The Hindu (National)",
        "category": "India",
        "type": "rss",
        "url": "https://www.thehindu.com/news/national/feeder/default.rss",
        "enabled": True,
    },
    {
        "id": "ndtv_india",
        "name": "NDTV News (India)",
        "category": "India",
        "type": "rss",
        "url": "https://feeds.feedburner.com/ndtvnews-top-stories",
        "enabled": True,
    },
    {
        "id": "indian_express",
        "name": "The Indian Express",
        "category": "India",
        "type": "rss",
        "url": "https://indianexpress.com/section/india/feed/",
        "enabled": True,
    },
    {
        "id": "india_today",
        "name": "India Today (Top Stories)",
        "category": "India",
        "type": "rss",
        "url": "https://www.indiatoday.in/rss/1206584",
        "enabled": True,
    },
    {
        "id": "hindustan_times",
        "name": "Hindustan Times",
        "category": "India",
        "type": "rss",
        "url": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
        "enabled": True,
    },

    # --- International Publishers & Agencies ---
    {
        "id": "bbc_world",
        "name": "BBC News (World)",
        "category": "World",
        "type": "rss",
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "enabled": True,
    },
    {
        "id": "aljazeera_all",
        "name": "Al Jazeera English",
        "category": "World",
        "type": "rss",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "enabled": True,
    },
    {
        "id": "dw_news",
        "name": "Deutsche Welle (DW)",
        "category": "World",
        "type": "rss",
        "url": "https://rss.dw.com/rdf/rss-en-all",
        "enabled": True,
    },
    {
        "id": "france24_en",
        "name": "France 24 (English)",
        "category": "World",
        "type": "rss",
        "url": "https://www.france24.com/en/rss",
        "enabled": True,
    },
    {
        "id": "npr_world",
        "name": "NPR News (World)",
        "category": "World",
        "type": "rss",
        "url": "https://feeds.npr.org/1004/rss.xml",
        "enabled": True,
    },
    {
        "id": "phys_org",
        "name": "Phys.org (Science & Tech)",
        "category": "Science",
        "type": "rss",
        "url": "https://phys.org/rss-feed/",
        "enabled": True,
    },

    # --- Official & Primary Sources ---
    {
        "id": "who_news",
        "name": "World Health Organization (WHO)",
        "category": "Health",
        "type": "official",
        "url": "https://www.who.int/rss-feeds/news-english.xml",
        "enabled": True,
    },
    {
        "id": "un_news",
        "name": "United Nations News",
        "category": "World",
        "type": "official",
        "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
        "enabled": True,
    },
    {
        "id": "nasa_breaking",
        "name": "NASA Breaking News",
        "category": "Science",
        "type": "official",
        "url": "https://www.nasa.gov/news-release/feed/",
        "enabled": True,
    },

    # --- Fact-Checking Sources ---
    {
        "id": "alt_news",
        "name": "Alt News (Fact Check)",
        "category": "Fact Check",
        "type": "factcheck",
        "url": "https://www.altnews.in/feed/",
        "enabled": True,
    },
    {
        "id": "boom_live",
        "name": "BOOM Live (Fact Check)",
        "category": "Fact Check",
        "type": "factcheck",
        "url": "https://www.boomlive.in/feed",
        "enabled": True,
    },
]

# Thread-safe in-memory source configuration table
_SOURCES_LOCK = threading.Lock()
_SOURCES_REGISTRY: Dict[str, Dict[str, Any]] = {}

def _init_source_registry():
    global _SOURCES_REGISTRY
    with _SOURCES_LOCK:
        if not _SOURCES_REGISTRY:
            for s in INITIAL_FEED_SOURCES:
                _SOURCES_REGISTRY[s["id"]] = dict(s)
                _SOURCES_REGISTRY[s["id"]]["article_count"] = 0
                _SOURCES_REGISTRY[s["id"]]["last_success"] = None
                _SOURCES_REGISTRY[s["id"]]["last_error"] = None
                _SOURCES_REGISTRY[s["id"]]["refresh_interval_sec"] = 300

            # Add verified YouTube channels
            for yt in youtube_service.VERIFIED_YOUTUBE_CHANNELS:
                sid = yt["id"]
                _SOURCES_REGISTRY[sid] = {
                    "id": sid,
                    "name": yt["name"],
                    "category": yt["category"],
                    "type": "youtube",
                    "url": f"https://www.youtube.com/feeds/videos.xml?channel_id={yt['channel_id']}",
                    "channel_id": yt["channel_id"],
                    "enabled": True,
                    "article_count": 0,
                    "last_success": None,
                    "last_error": None,
                    "refresh_interval_sec": 300,
                }

            # Add GDELT streams
            gdelt_definitions = [
                ("gdelt_india", "GDELT India Dispatches", "India", "sourcecountry:IN OR India news"),
                ("gdelt_factcheck", "GDELT Fact-Check Wire", "Fact Check", "factcheck OR \"fact check\" OR debunk OR claim"),
                ("gdelt_elections", "GDELT Election Watch", "Elections", "election OR voters OR parliament OR ballot"),
                ("gdelt_world", "GDELT World Affairs", "World", "world affairs OR international summit OR united nations"),
            ]
            for gid, gname, gcat, gq in gdelt_definitions:
                _SOURCES_REGISTRY[gid] = {
                    "id": gid,
                    "name": gname,
                    "category": gcat,
                    "type": "api",
                    "url": f"https://api.gdeltproject.org/api/v2/doc/doc?query={gq}",
                    "query": gq,
                    "enabled": True,
                    "article_count": 0,
                    "last_success": None,
                    "last_error": None,
                    "refresh_interval_sec": 300,
                }

_init_source_registry()

# ============================================================================
# SSRF PROTECTION
# ============================================================================

def validate_url_safe(url: str) -> str:
    """
    Validate that a URL is safe to fetch and does not point to internal/private
    networks, localhost, cloud metadata services (e.g. 169.254.169.254), or unsupported schemes.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL cannot be empty.")

    url = url.strip()
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported URL scheme '{parsed.scheme}'. Only http and https are permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL is missing a valid hostname.")

    # Check for direct localhost aliases
    if hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        raise ValueError("Access to localhost is prohibited.")

    # Resolve hostname to all IP addresses
    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        raise ValueError(f"Could not resolve host '{hostname}': {e}")

    for item in addr_info:
        ip_str = item[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
                or ip.is_unspecified
            ):
                raise ValueError(f"SSRF Protection: Host '{hostname}' resolves to restricted IP {ip_str}.")
        except ValueError as err:
            if "SSRF Protection" in str(err):
                raise
            raise ValueError(f"Invalid IP address resolved for host '{hostname}': {ip_str}")

    return url


# ============================================================================
# PARSING UTILITIES
# ============================================================================

def _clean_html_text(raw_html: Optional[str]) -> str:
    """Strip HTML tags and clean up whitespace."""
    if not raw_html:
        return ""
    if "<" not in raw_html:
        return re.sub(r"\s+", " ", raw_html).strip()
    try:
        soup = BeautifulSoup(raw_html, "html.parser")
        return re.sub(r"\s+", " ", soup.get_text(separator=" ")).strip()
    except Exception:
        text = re.sub(r"<[^>]+>", " ", raw_html)
        return re.sub(r"\s+", " ", text).strip()


def _make_article_id(url: str, headline: str) -> str:
    """Generate a stable deterministic ID from URL and headline."""
    payload = f"{url.strip().lower()}|{headline.strip().lower()}"
    return f"ART-{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:12].upper()}"


def _normalize_title_key(headline: str) -> str:
    """Normalized key for deduplication."""
    return re.sub(r"[^a-z0-9]", "", headline.lower())


def _compute_content_availability(summary: str, content: Optional[str] = None, has_full_text: bool = False) -> str:
    """Determine honest content availability level."""
    if has_full_text and content and len(content.split()) >= 80:
        return "full-text"
    if summary and len(summary.strip()) >= 30:
        return "summary-only"
    return "headline-only"


# ============================================================================
# RSS & ATOM FEED FETCHER
# ============================================================================

def _parse_xml_feed(source_info: Dict[str, Any], xml_content: bytes) -> List[NewsArticleItem]:
    """Parse RSS 2.0 or Atom XML content into NewsArticleItem list."""
    articles = []
    root = ET.fromstring(xml_content)

    tag = root.tag
    is_atom = "feed" in tag.lower()
    source_type = source_info.get("type", "rss")

    if is_atom:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns) or root.findall("entry")
        for entry in entries:
            title_elem = entry.find("atom:title", ns) or entry.find("title")
            title = _clean_html_text(title_elem.text if title_elem is not None else "")

            link = ""
            for lk in (entry.findall("atom:link", ns) or entry.findall("link")):
                href = lk.get("href", "")
                rel = lk.get("rel", "alternate")
                if rel in ("alternate", "") and href:
                    link = href
                    break
            if not link:
                lk_elem = entry.find("atom:link", ns) or entry.find("link")
                if lk_elem is not None:
                    link = lk_elem.get("href", "") or lk_elem.text or ""

            summary_elem = (
                entry.find("atom:summary", ns)
                or entry.find("summary")
                or entry.find("atom:content", ns)
                or entry.find("content")
            )
            summary = _clean_html_text(summary_elem.text if summary_elem is not None else "")

            pub_elem = (
                entry.find("atom:published", ns)
                or entry.find("published")
                or entry.find("atom:updated", ns)
                or entry.find("updated")
            )
            published_at = pub_elem.text.strip() if (pub_elem is not None and pub_elem.text) else None

            if title and link:
                avail = _compute_content_availability(summary)
                articles.append(
                    NewsArticleItem(
                        id=_make_article_id(link, title),
                        headline=title,
                        publisher=source_info["name"],
                        source_id=source_info["id"],
                        url=link,
                        published_at=published_at,
                        summary=summary[:600],
                        content=summary if summary else None,
                        category=source_info.get("category", "General"),
                        source_type=source_type,
                        content_availability=avail,
                        has_full_text=False,
                    )
                )
    else:
        channel = root.find("channel")
        items = channel.findall("item") if channel is not None else root.findall(".//item")
        for item in items:
            title_elem = item.find("title")
            title = _clean_html_text(title_elem.text if title_elem is not None else "")

            link_elem = item.find("link")
            link = link_elem.text.strip() if (link_elem is not None and link_elem.text) else ""

            desc_elem = item.find("description")
            summary = _clean_html_text(desc_elem.text if desc_elem is not None else "")

            pub_elem = item.find("pubDate")
            published_at = pub_elem.text.strip() if (pub_elem is not None and pub_elem.text) else None

            image_url = None
            enclosure = item.find("enclosure")
            if enclosure is not None and "image" in enclosure.get("type", ""):
                image_url = enclosure.get("url")

            if title and link:
                avail = _compute_content_availability(summary)
                articles.append(
                    NewsArticleItem(
                        id=_make_article_id(link, title),
                        headline=title,
                        publisher=source_info["name"],
                        source_id=source_info["id"],
                        url=link,
                        published_at=published_at,
                        summary=summary[:600],
                        content=summary if summary else None,
                        category=source_info.get("category", "General"),
                        source_type=source_type,
                        content_availability=avail,
                        has_full_text=False,
                        image_url=image_url,
                    )
                )

    return articles


def _fetch_single_rss_source(source_info: Dict[str, Any]) -> Tuple[NewsSourceStatus, List[NewsArticleItem]]:
    """Fetch and parse a single RSS/Atom feed with timeout and isolation."""
    source_id = source_info["id"]
    name = source_info["name"]
    category = source_info.get("category", "General")
    source_type = source_info.get("type", "rss")
    url = source_info["url"]

    try:
        safe_url = validate_url_safe(url)
        headers = {
            "User-Agent": _USER_AGENT,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9",
        }
        resp = requests.get(safe_url, headers=headers, timeout=_DEFAULT_TIMEOUT)
        resp.raise_for_status()

        articles = _parse_xml_feed(source_info, resp.content)
        status = NewsSourceStatus(
            source_id=source_id,
            name=name,
            category=category,
            source_type=source_type,
            status="OK",
            enabled=True,
            article_count=len(articles),
            feed_url=url,
            last_success=datetime.now(timezone.utc).isoformat(),
        )
        return status, articles

    except requests.exceptions.Timeout:
        logger.warning("Feed '%s' timed out after %ss", name, _DEFAULT_TIMEOUT)
        return (
            NewsSourceStatus(
                source_id=source_id,
                name=name,
                category=category,
                source_type=source_type,
                status="TIMEOUT",
                enabled=True,
                error_message=f"Request timed out after {_DEFAULT_TIMEOUT}s",
                feed_url=url,
                last_error=datetime.now(timezone.utc).isoformat(),
            ),
            [],
        )
    except Exception as e:
        logger.warning("Feed '%s' failed: %s", name, str(e))
        return (
            NewsSourceStatus(
                source_id=source_id,
                name=name,
                category=category,
                source_type=source_type,
                status="ERROR",
                enabled=True,
                error_message=str(e)[:200],
                feed_url=url,
                last_error=datetime.now(timezone.utc).isoformat(),
            ),
            [],
        )


# ============================================================================
# GDELT DOC 2.0 API FETCHER
# ============================================================================

def _fetch_gdelt_articles(
    query: str = "news",
    max_records: int = 25,
    source_id: str = "gdelt_world",
    name: str = "GDELT World Affairs",
    category: str = "World",
) -> Tuple[NewsSourceStatus, List[NewsArticleItem]]:
    """
    Query the GDELT DOC 2.0 API for real-time global news.
    Requires no API key; freely accessible open data.
    """
    endpoint = "https://api.gdeltproject.org/api/v2/doc/doc"
    clean_query = query.strip() or "news"
    params = {
        "query": clean_query,
        "mode": "artlist",
        "format": "json",
        "maxrecords": str(min(50, max(5, max_records))),
        "sort": "DateDesc",
    }

    try:
        validate_url_safe(endpoint)
        headers = {"User-Agent": _USER_AGENT}
        resp = requests.get(endpoint, params=params, headers=headers, timeout=_DEFAULT_TIMEOUT)
        resp.raise_for_status()

        data = resp.json()
        articles_raw = data.get("articles", [])
        parsed_articles = []

        for item in articles_raw:
            title = _clean_html_text(item.get("title", ""))
            url = item.get("url", "").strip()
            domain = item.get("domain", "Global Press")
            seendate = item.get("seendate")
            socialimage = item.get("socialimage")

            pub_date = None
            if seendate and len(seendate) >= 8:
                try:
                    dt = datetime.strptime(seendate[:15], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
                    pub_date = dt.isoformat()
                except Exception:
                    pub_date = seendate

            if title and url:
                parsed_articles.append(
                    NewsArticleItem(
                        id=_make_article_id(url, title),
                        headline=title,
                        publisher=f"{domain.upper()} (via GDELT)",
                        source_id=source_id,
                        url=url,
                        published_at=pub_date,
                        summary=f"Reported from {domain} as tracked by the GDELT global news monitoring system.",
                        category=category,
                        source_type="api",
                        content_availability="summary-only",
                        has_full_text=False,
                        image_url=socialimage if socialimage and socialimage.startswith("http") else None,
                    )
                )

        status = NewsSourceStatus(
            source_id=source_id,
            name=name,
            category=category,
            source_type="api",
            status="OK",
            enabled=True,
            article_count=len(parsed_articles),
            feed_url=endpoint,
            last_success=datetime.now(timezone.utc).isoformat(),
        )
        return status, parsed_articles

    except requests.exceptions.Timeout:
        logger.warning("GDELT DOC 2.0 API timed out for query '%s'", query)
        return (
            NewsSourceStatus(
                source_id=source_id,
                name=name,
                category=category,
                source_type="api",
                status="TIMEOUT",
                enabled=True,
                error_message=f"GDELT timed out after {_DEFAULT_TIMEOUT}s",
                feed_url=endpoint,
                last_error=datetime.now(timezone.utc).isoformat(),
            ),
            [],
        )
    except Exception as e:
        logger.warning("GDELT DOC 2.0 query failed: %s", str(e))
        return (
            NewsSourceStatus(
                source_id=source_id,
                name=name,
                category=category,
                source_type="api",
                status="ERROR",
                enabled=True,
                error_message=str(e)[:200],
                feed_url=endpoint,
                last_error=datetime.now(timezone.utc).isoformat(),
            ),
            [],
        )


# ============================================================================
# OPTIONAL FRESHRSS INTEGRATION
# ============================================================================

def _fetch_freshrss_articles() -> Tuple[Optional[NewsSourceStatus], List[NewsArticleItem]]:
    """Optionally fetch feeds from a self-hosted FreshRSS instance if configured."""
    freshrss_url = os.getenv("FRESHRSS_URL", "").strip()
    if not freshrss_url:
        return None, []

    source_id = "freshrss"
    name = "FreshRSS Aggregator"
    category = "General"

    try:
        safe_url = validate_url_safe(freshrss_url)
        headers = {"User-Agent": _USER_AGENT}
        auth = None
        user = os.getenv("FRESHRSS_USER")
        api_key = os.getenv("FRESHRSS_API_KEY")
        if user and api_key:
            auth = (user, api_key)

        resp = requests.get(safe_url, headers=headers, auth=auth, timeout=_DEFAULT_TIMEOUT)
        resp.raise_for_status()

        articles = _parse_xml_feed(
            {"id": source_id, "name": name, "category": category, "type": "rss"},
            resp.content,
        )
        status = NewsSourceStatus(
            source_id=source_id,
            name=name,
            category=category,
            source_type="rss",
            status="OK",
            enabled=True,
            article_count=len(articles),
            feed_url=safe_url,
            last_success=datetime.now(timezone.utc).isoformat(),
        )
        return status, articles

    except Exception as e:
        logger.warning("Optional FreshRSS fetch failed: %s", e)
        return (
            NewsSourceStatus(
                source_id=source_id,
                name=name,
                category=category,
                source_type="rss",
                status="ERROR",
                enabled=True,
                error_message=f"FreshRSS instance unreachable: {str(e)[:150]}",
                feed_url=freshrss_url,
                last_error=datetime.now(timezone.utc).isoformat(),
            ),
            [],
        )


# ============================================================================
# AGGREGATOR & CACHE CONTROLLER
# ============================================================================

def get_live_news_feed(
    category: Optional[str] = None,
    source: Optional[str] = None,
    source_type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 12,
    force_refresh: bool = False,
) -> NewsFeedResponse:
    """
    Fetch, aggregate, deduplicate, and return filtered & paginated articles.
    Utilizes an in-memory TTL cache to prevent upstream spam.
    Respects source enabled/disabled status in _SOURCES_REGISTRY.
    """
    global _CACHE

    now = time.time()
    needs_refresh = force_refresh or (now - _CACHE["timestamp"] > _CACHE_TTL_SECONDS) or not _CACHE["articles"]

    if needs_refresh:
        with _CACHE_LOCK:
            if force_refresh or (time.time() - _CACHE["timestamp"] > _CACHE_TTL_SECONDS) or not _CACHE["articles"]:
                logger.info("Refreshing multi-channel live news feeds (cache expired or forced)...")
                all_articles: List[NewsArticleItem] = []
                all_statuses: List[NewsSourceStatus] = []

                # Collect active sources from registry
                with _SOURCES_LOCK:
                    active_sources = [s for s in _SOURCES_REGISTRY.values() if s.get("enabled", True)]
                    disabled_sources = [s for s in _SOURCES_REGISTRY.values() if not s.get("enabled", True)]

                # Add disabled statuses
                for ds in disabled_sources:
                    all_statuses.append(
                        NewsSourceStatus(
                            source_id=ds["id"],
                            name=ds["name"],
                            category=ds.get("category", "General"),
                            source_type=ds.get("type", "rss"),
                            status="DISABLED",
                            enabled=False,
                            article_count=0,
                            feed_url=ds.get("url"),
                            last_success=ds.get("last_success"),
                            last_error=ds.get("last_error"),
                        )
                    )

                # Execute active feed fetches in parallel
                with ThreadPoolExecutor(max_workers=12) as executor:
                    future_map = {}

                    for src in active_sources:
                        stype = src.get("type", "rss")
                        if stype == "youtube":
                            future_map[executor.submit(youtube_service.fetch_youtube_channel_feed, src)] = src["id"]
                        elif stype == "api" and "gdelt" in src["id"]:
                            q = src.get("query", "news")
                            future_map[executor.submit(_fetch_gdelt_articles, q, 20, src["id"], src["name"], src["category"])] = src["id"]
                        else:
                            # Standard RSS, Atom, Official, or Fact-Check feeds
                            future_map[executor.submit(_fetch_single_rss_source, src)] = src["id"]

                    # Optional FreshRSS
                    freshrss_future = executor.submit(_fetch_freshrss_articles)

                    for future in as_completed(future_map):
                        sid = future_map[future]
                        try:
                            status, items = future.result()
                            all_statuses.append(status)
                            all_articles.extend(items)
                            # Update registry metrics
                            with _SOURCES_LOCK:
                                if sid in _SOURCES_REGISTRY:
                                    _SOURCES_REGISTRY[sid]["article_count"] = len(items)
                                    if status.status == "OK":
                                        _SOURCES_REGISTRY[sid]["last_success"] = status.last_success
                                    else:
                                        _SOURCES_REGISTRY[sid]["last_error"] = status.error_message
                        except Exception as e:
                            logger.warning("Source %s task failed: %s", sid, e)

                    # FreshRSS result
                    try:
                        fr_status, fr_items = freshrss_future.result()
                        if fr_status is not None:
                            all_statuses.append(fr_status)
                            all_articles.extend(fr_items)
                    except Exception as e:
                        logger.debug("FreshRSS check completed: %s", e)

                # Deduplicate by normalized title & URL
                seen_keys = set()
                deduped: List[NewsArticleItem] = []
                for art in all_articles:
                    norm_title = _normalize_title_key(art.headline)
                    norm_url = art.url.split("?")[0].strip().lower()
                    key = f"{norm_title}|{norm_url}"
                    if key not in seen_keys:
                        seen_keys.add(key)
                        deduped.append(art)

                _CACHE["articles"] = deduped
                _CACHE["sources"] = all_statuses
                _CACHE["timestamp"] = time.time()
                logger.info(
                    "Multi-channel feed refreshed: %d unique articles from %d sources.",
                    len(deduped),
                    len(all_statuses),
                )

    articles = list(_CACHE["articles"])
    sources = list(_CACHE["sources"])

    # 1. Source filter
    if source and source.lower() not in ("all", "all sources"):
        articles = [a for a in articles if a.source_id.lower() == source.lower()]

    # 2. Category filter
    if category and category.lower() not in ("all", "all categories"):
        articles = [a for a in articles if a.category.lower() == category.lower()]

    # 3. Source Type filter
    if source_type and source_type.lower() not in ("all", "all types"):
        articles = [a for a in articles if a.source_type.lower() == source_type.lower()]

    # 4. Search query filter
    if search and search.strip():
        q = search.strip().lower()
        articles = [
            a
            for a in articles
            if q in a.headline.lower() or q in a.summary.lower() or q in a.publisher.lower()
        ]

    # Collect available categories
    categories = sorted(list({"India", "World", "Health", "Science", "Technology", "Elections", "Fact Check", "General"}))

    # Pagination
    total = len(articles)
    limit = max(1, min(50, limit))
    total_pages = max(1, (total + limit - 1) // limit)
    page = max(1, min(page, total_pages)) if total > 0 else 1

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    page_articles = articles[start_idx:end_idx]

    iso_updated = datetime.fromtimestamp(_CACHE["timestamp"], tz=timezone.utc).isoformat()

    return NewsFeedResponse(
        articles=page_articles,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        sources=sources,
        categories=categories,
        source_types=["all", "rss", "api", "youtube", "official", "factcheck"],
        cached=not needs_refresh,
        last_updated=iso_updated,
    )


def get_sources_registry() -> List[Dict[str, Any]]:
    """Return all sources from the registry including enabled status, stats, and type."""
    with _SOURCES_LOCK:
        return [
            {
                "id": s["id"],
                "name": s["name"],
                "category": s.get("category", "General"),
                "type": s.get("type", "rss"),
                "url": s.get("url", ""),
                "enabled": s.get("enabled", True),
                "article_count": s.get("article_count", 0),
                "last_success": s.get("last_success"),
                "last_error": s.get("last_error"),
                "refresh_interval_sec": s.get("refresh_interval_sec", 300),
            }
            for s in _SOURCES_REGISTRY.values()
        ]


def get_available_sources() -> List[Dict[str, Any]]:
    """Return all sources for backwards compatibility with existing tests and callers."""
    sources = list(get_sources_registry())
    if not any(s["id"] == "gdelt" for s in sources):
        sources.append({
            "id": "gdelt",
            "name": "GDELT Global News",
            "category": "World",
            "type": "api",
            "enabled": True,
        })
    return sources


def toggle_source_status(source_id: str, enabled: bool) -> bool:
    """Toggle enabled status of a source in the registry and invalidate cache."""
    global _CACHE
    with _SOURCES_LOCK:
        if source_id not in _SOURCES_REGISTRY:
            return False
        _SOURCES_REGISTRY[source_id]["enabled"] = enabled

    # Invalidate cache to force update on next fetch
    with _CACHE_LOCK:
        _CACHE["timestamp"] = 0.0
    return True


def add_custom_source(source_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Register a new feed source with SSRF protection.
    Validates URL before persisting.
    """
    global _CACHE
    sid = source_data.get("id", "").strip()
    name = source_data.get("name", "").strip()
    category = source_data.get("category", "General").strip()
    stype = source_data.get("type", "rss").strip().lower()
    url = source_data.get("url", "").strip()

    if not sid or not name or not url:
        return False, "Missing required fields (id, name, url)."

    if sid in _SOURCES_REGISTRY:
        return False, f"Source ID '{sid}' already exists."

    # Validate safe URL against SSRF
    try:
        safe_url = validate_url_safe(url)
    except ValueError as e:
        return False, f"URL validation failed: {str(e)}"

    with _SOURCES_LOCK:
        _SOURCES_REGISTRY[sid] = {
            "id": sid,
            "name": name,
            "category": category,
            "type": stype,
            "url": safe_url,
            "enabled": True,
            "article_count": 0,
            "last_success": None,
            "last_error": None,
            "refresh_interval_sec": 300,
        }

    # Invalidate cache so new source is queried on next request
    with _CACHE_LOCK:
        _CACHE["timestamp"] = 0.0

    return True, f"Source '{name}' added successfully."


def get_topic_timeline(query: str, limit: int = 15) -> Dict[str, Any]:
    """
    Search available cached or live articles matching a topic/query,
    group them chronologically across publishers, and assess syndication
    versus independent reporting.
    """
    if not query or not query.strip():
        return {
            "query": query,
            "total_articles": 0,
            "timeline": [],
            "publishers": [],
            "syndication_assessment": "No query provided for timeline synthesis.",
        }

    q = query.strip().lower()
    feed = get_live_news_feed(search=q, limit=limit)
    matching = feed.articles

    if not matching:
        fallback_feed = get_live_news_feed(limit=limit)
        matching = fallback_feed.articles[:6]

    def _parse_time(art: NewsArticleItem) -> float:
        if art.published_at:
            try:
                dt = datetime.fromisoformat(art.published_at.replace("Z", "+00:00"))
                return dt.timestamp()
            except Exception:
                pass
        return 0.0

    sorted_articles = sorted(matching, key=_parse_time, reverse=True)

    publishers = list({a.publisher for a in sorted_articles})
    syndication_detected = False
    clusters = []

    for i, a1 in enumerate(sorted_articles):
        cluster_peers = []
        words1 = set(re.findall(r"\w+", a1.headline.lower()))
        for j, a2 in enumerate(sorted_articles):
            if i != j and a1.publisher != a2.publisher:
                words2 = set(re.findall(r"\w+", a2.headline.lower()))
                overlap = len(words1 & words2) / max(1, len(words1 | words2))
                if overlap > 0.45:
                    syndication_detected = True
                    cluster_peers.append(a2.publisher)
        clusters.append({
            "headline": a1.headline,
            "publisher": a1.publisher,
            "published_at": a1.published_at,
            "url": a1.url,
            "category": a1.category,
            "source_type": a1.source_type,
            "content_availability": a1.content_availability,
            "syndicated_with": list(set(cluster_peers)),
            "coverage_type": "Syndicated / Wire Pickup" if cluster_peers else "Independent Coverage",
        })

    return {
        "query": query,
        "total_articles": len(sorted_articles),
        "publishers_count": len(publishers),
        "publishers": publishers,
        "has_syndication": syndication_detected,
        "syndication_summary": (
            "Cross-publisher text duplication detected. Multiple outlets appear to be syndicating the same underlying wire release."
            if syndication_detected
            else "Distinct reporting framing observed across independent media publishers."
        ),
        "timeline": clusters,
    }


# ============================================================================
# SAFE FULL-TEXT ARTICLE EXTRACTION
# ============================================================================

def fetch_article_content(url: str) -> FetchArticleResponse:
    """
    Safely fetch and extract article body text or YouTube transcript.
    - If URL is a YouTube video, routes to youtube_service.extract_youtube_transcript.
    - Otherwise, validates URL against SSRF vulnerabilities and parses HTML.
    - Explicitly sets content_availability.
    """
    # Check if YouTube URL
    video_id = youtube_service.extract_video_id(url)
    if video_id:
        yt_resp = youtube_service.extract_youtube_transcript(video_id)
        if yt_resp.has_transcript:
            return FetchArticleResponse(
                url=url,
                headline=yt_resp.title,
                content=yt_resp.transcript,
                has_full_text=True,
                content_availability="full-text",
                publisher=yt_resp.channel or "YouTube News",
                word_count=yt_resp.word_count,
                note=yt_resp.note,
            )
        else:
            return FetchArticleResponse(
                url=url,
                headline=yt_resp.title,
                content=None,
                has_full_text=False,
                content_availability="summary-only",
                publisher=yt_resp.channel or "YouTube News",
                word_count=0,
                note=yt_resp.note,
            )

    try:
        safe_url = validate_url_safe(url)
    except ValueError as e:
        return FetchArticleResponse(
            url=url,
            has_full_text=False,
            content_availability="headline-only",
            note=f"Invalid or restricted URL: {e}",
        )

    headers = {
        "User-Agent": _USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        resp = requests.get(safe_url, headers=headers, timeout=_DEFAULT_TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()

        headline = ""
        title_tag = soup.find("h1") or soup.find("title")
        if title_tag:
            headline = _clean_html_text(title_tag.get_text())

        article_elem = soup.find("article") or soup.find("main") or soup
        paragraphs = article_elem.find_all("p")
        text_paragraphs = [
            _clean_html_text(p.get_text())
            for p in paragraphs
            if len(_clean_html_text(p.get_text())) > 25
        ]

        full_text = "\n\n".join(text_paragraphs).strip()
        word_count = len(full_text.split())

        if word_count >= 80:
            return FetchArticleResponse(
                url=safe_url,
                headline=headline,
                content=full_text[:50_000],
                has_full_text=True,
                content_availability="full-text",
                word_count=word_count,
                note="Full article text retrieved successfully from publisher.",
            )
        else:
            return FetchArticleResponse(
                url=safe_url,
                headline=headline,
                content=full_text if full_text else None,
                has_full_text=False,
                content_availability="summary-only" if full_text else "headline-only",
                word_count=word_count,
                note=(
                    "Full article body could not be extracted (publisher may require "
                    "JavaScript, a paywall, or client-side rendering). "
                    "Analysis will run on available headline and excerpt. "
                    "You may paste full text manually for comprehensive analysis."
                ),
            )

    except requests.exceptions.Timeout:
        return FetchArticleResponse(
            url=url,
            has_full_text=False,
            content_availability="headline-only",
            note="Publisher server timed out while fetching article body.",
        )
    except requests.exceptions.HTTPError as e:
        status_code = getattr(e.response, "status_code", "HTTP error")
        return FetchArticleResponse(
            url=url,
            has_full_text=False,
            content_availability="headline-only",
            note=f"Publisher returned {status_code}. Full body text unavailable.",
        )
    except Exception as e:
        logger.warning("Article extraction failed for %s: %s", url, e)
        return FetchArticleResponse(
            url=url,
            has_full_text=False,
            content_availability="headline-only",
            note=f"Unable to retrieve full text: {str(e)[:150]}",
        )
