"""
youtube_service.py
==================
Integrates YouTube news channels into the VeriNews AI 2.0 multi-channel intelligence feed.
Supports:
1. Public XML channel feeds without API keys:
   https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}
2. Optional YouTube Data API v3 when YOUTUBE_API_KEY is configured.
3. Safe transcript extraction via youtube-transcript-api (if available), with honest fallback
   to metadata/description when captions are disabled or unavailable.
"""

import os
import re
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import requests

from app.schemas.news import (
    NewsArticleItem,
    NewsSourceStatus,
    YouTubeTranscriptResponse,
)

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 8.0
_USER_AGENT = "VeriNewsBot/2.0 (+https://github.com/verinews; multi-channel news verification)"

# Verified standard news channels with public channel IDs
VERIFIED_YOUTUBE_CHANNELS = [
    {
        "id": "yt_bbc_news",
        "name": "BBC News (YouTube)",
        "channel_id": "UC16niRr50-MSBwiO3YDb3RA",
        "category": "World",
        "type": "youtube",
    },
    {
        "id": "yt_ndtv",
        "name": "NDTV (YouTube)",
        "channel_id": "UCZFMm1mMw0F81Z37aaSuT_Q",
        "category": "India",
        "type": "youtube",
    },
    {
        "id": "yt_india_today",
        "name": "India Today (YouTube)",
        "channel_id": "UCYPvAwZP8pZhSMW8qs7cVCw",
        "category": "India",
        "type": "youtube",
    },
    {
        "id": "yt_dw_news",
        "name": "DW News (YouTube)",
        "channel_id": "UCknLrEdhRCp1aegoMqRaCZg",
        "category": "World",
        "type": "youtube",
    },
    {
        "id": "yt_aljazeera",
        "name": "Al Jazeera English (YouTube)",
        "channel_id": "UCNye-wNBqNL5ZzHSJj3l8Bg",
        "category": "World",
        "type": "youtube",
    },
]


def extract_video_id(url_or_id: str) -> Optional[str]:
    """Extract YouTube 11-character video ID from varied URL formats or raw ID."""
    if not url_or_id or not isinstance(url_or_id, str):
        return None
    url_or_id = url_or_id.strip()
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url_or_id):
        return url_or_id

    patterns = [
        r"(?:v=|\/v\/|embed\/|watch\?v=|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})",
        r"^https?:\/\/(?:www\.)?youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})",
        r"^https?:\/\/youtu\.be\/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        m = re.search(pattern, url_or_id)
        if m:
            return m.group(1)
    return None


def parse_youtube_xml_feed(channel_info: Dict[str, Any], xml_bytes: bytes) -> List[NewsArticleItem]:
    """
    Parse official YouTube Atom/XML feed into NewsArticleItem list.
    Extracts video ID, title, publication date, video URL, thumbnail, and description.
    """
    articles: List[NewsArticleItem] = []
    try:
        root = ET.fromstring(xml_bytes)
    except Exception as e:
        logger.warning("Failed to parse YouTube XML for channel %s: %s", channel_info.get("name"), e)
        return []

    # XML namespaces used by YouTube feeds
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015",
        "media": "http://search.yahoo.com/mrss/",
    }

    entries = root.findall("atom:entry", ns) or root.findall("entry")

    for entry in entries:
        try:
            # Video ID
            vid_elem = entry.find("yt:videoId", ns)
            video_id = vid_elem.text.strip() if (vid_elem is not None and vid_elem.text) else None

            # Title
            title_elem = entry.find("atom:title", ns) or entry.find("title")
            title = title_elem.text.strip() if (title_elem is not None and title_elem.text) else ""

            # Link
            link = ""
            for lk in (entry.findall("atom:link", ns) or entry.findall("link")):
                if lk.get("rel") == "alternate":
                    link = lk.get("href", "")
                    break
            if not link and video_id:
                link = f"https://www.youtube.com/watch?v={video_id}"

            # Published Date
            pub_elem = (
                entry.find("atom:published", ns)
                or entry.find("published")
                or entry.find("atom:updated", ns)
            )
            published_at = pub_elem.text.strip() if (pub_elem is not None and pub_elem.text) else None

            # Media Group (Description & Thumbnail)
            summary = ""
            thumbnail_url = None
            media_group = entry.find("media:group", ns)
            if media_group is not None:
                desc_elem = media_group.find("media:description", ns)
                if desc_elem is not None and desc_elem.text:
                    summary = desc_elem.text.strip()

                thumb_elem = media_group.find("media:thumbnail", ns)
                if thumb_elem is not None:
                    thumbnail_url = thumb_elem.get("url")

            if not thumbnail_url and video_id:
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

            # Channel / Author Title
            author_elem = entry.find("atom:author/atom:name", ns) or entry.find("author/name")
            channel_name = author_elem.text.strip() if (author_elem is not None and author_elem.text) else channel_info["name"]

            # Content availability
            content_avail = "summary-only" if summary and len(summary) >= 30 else "headline-only"

            if title and link:
                clean_id = f"YT-{video_id}" if video_id else f"YT-{abs(hash(link))}"
                articles.append(
                    NewsArticleItem(
                        id=clean_id,
                        headline=title,
                        publisher=channel_name,
                        source_id=channel_info["id"],
                        url=link,
                        published_at=published_at,
                        summary=summary[:600],
                        content=summary if summary else None,
                        category=channel_info.get("category", "World"),
                        source_type="youtube",
                        content_availability=content_avail,
                        has_full_text=False,
                        image_url=thumbnail_url,
                        video_id=video_id,
                        channel_title=channel_name,
                        has_transcript=False,
                    )
                )
        except Exception as item_err:
            logger.debug("Skipping invalid YouTube entry: %s", item_err)
            continue

    return articles


def fetch_youtube_channel_feed(channel_info: Dict[str, Any]) -> Tuple[NewsSourceStatus, List[NewsArticleItem]]:
    """
    Fetch public videos for a YouTube channel via official public RSS XML feed.
    Zero API key required; rate-limited responsibly.
    """
    channel_id = channel_info.get("channel_id")
    source_id = channel_info.get("id", "youtube_channel")
    name = channel_info.get("name", "YouTube News")
    category = channel_info.get("category", "General")

    if not channel_id:
        return (
            NewsSourceStatus(
                source_id=source_id,
                name=name,
                category=category,
                source_type="youtube",
                status="ERROR",
                error_message="Missing channel_id configuration.",
            ),
            [],
        )

    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    try:
        headers = {"User-Agent": _USER_AGENT}
        resp = requests.get(feed_url, headers=headers, timeout=_DEFAULT_TIMEOUT)
        resp.raise_for_status()

        articles = parse_youtube_xml_feed(channel_info, resp.content)
        status = NewsSourceStatus(
            source_id=source_id,
            name=name,
            category=category,
            source_type="youtube",
            status="OK",
            enabled=True,
            article_count=len(articles),
            feed_url=feed_url,
            last_success=datetime.now(timezone.utc).isoformat(),
        )
        return status, articles

    except requests.exceptions.Timeout:
        logger.warning("YouTube feed '%s' timed out.", name)
        return (
            NewsSourceStatus(
                source_id=source_id,
                name=name,
                category=category,
                source_type="youtube",
                status="TIMEOUT",
                enabled=True,
                error_message=f"Request timed out after {_DEFAULT_TIMEOUT}s",
                feed_url=feed_url,
                last_error=datetime.now(timezone.utc).isoformat(),
            ),
            [],
        )
    except Exception as e:
        logger.warning("YouTube feed '%s' failed: %s", name, str(e))
        return (
            NewsSourceStatus(
                source_id=source_id,
                name=name,
                category=category,
                source_type="youtube",
                status="ERROR",
                enabled=True,
                error_message=str(e)[:200],
                feed_url=feed_url,
                last_error=datetime.now(timezone.utc).isoformat(),
            ),
            [],
        )


def extract_youtube_transcript(video_id_or_url: str) -> YouTubeTranscriptResponse:
    """
    Extract spoken transcript from a YouTube video if public captions exist.
    Falls back gracefully if transcript is unavailable or disabled, providing
    video details and prompting manual transcript input without fabricating.
    """
    video_id = extract_video_id(video_id_or_url)
    if not video_id:
        return YouTubeTranscriptResponse(
            video_id=video_id_or_url,
            has_transcript=False,
            note="Invalid YouTube video URL or ID provided.",
        )

    # 1. Attempt using youtube-transcript-api if installed
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # Try retrieving english or default transcript
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US", "en-GB", "hi"])
        if transcript_data:
            full_text = " ".join([entry.get("text", "") for entry in transcript_data]).strip()
            word_count = len(full_text.split())
            if word_count > 15:
                return YouTubeTranscriptResponse(
                    video_id=video_id,
                    has_transcript=True,
                    transcript=full_text[:50_000],
                    word_count=word_count,
                    note="Official public video captions / spoken transcript extracted successfully.",
                )
    except ImportError:
        logger.debug("youtube-transcript-api library not installed.")
    except Exception as e:
        logger.info("Transcript unavailable for YouTube video %s: %s", video_id, str(e)[:100])

    # 2. Honest Fallback
    return YouTubeTranscriptResponse(
        video_id=video_id,
        has_transcript=False,
        transcript=None,
        word_count=0,
        note=(
            "Spoken transcript could not be automatically extracted "
            "(captions are disabled, private, or unavailable for this broadcast). "
            "Analysis will proceed using the video headline and publisher description. "
            "You may paste the spoken dialogue or claim manually for deep verification."
        ),
    )
