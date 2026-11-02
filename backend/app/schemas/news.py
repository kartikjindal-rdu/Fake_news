"""
news.py
=======
Pydantic data schemas for the Live News Feed and Multi-Channel News Intelligence
feature in VeriNews AI 2.0.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


SourceType = Literal["rss", "api", "youtube", "official", "factcheck"]
ContentAvailability = Literal["headline-only", "summary-only", "full-text"]


class NewsArticleItem(BaseModel):
    id: str = Field(..., description="Unique deterministic identifier for the article")
    headline: str = Field(..., description="Article headline / title")
    publisher: str = Field(..., description="Publisher or outlet name, e.g. BBC News, WHO, NDTV")
    source_id: str = Field(..., description="Machine identifier of the feed source")
    url: str = Field(..., description="Original article URL or video URL")
    published_at: Optional[str] = Field(default=None, description="ISO or RFC date string")
    summary: str = Field(default="", description="Short synopsis or excerpt from the feed")
    content: Optional[str] = Field(default=None, description="Extracted body text or transcript if available")
    category: str = Field(default="General", description="Topic category (India, World, Health, Science, Fact Check, Elections)")
    source_type: str = Field(default="rss", description="Source channel type: rss, api, youtube, official, factcheck")
    content_availability: str = Field(
        default="summary-only",
        description="Availability level of content: headline-only, summary-only, full-text"
    )
    has_full_text: bool = Field(default=False, description="True if full body text or transcript was retrieved")
    image_url: Optional[str] = Field(default=None, description="Optional lead image or video thumbnail URL")
    video_id: Optional[str] = Field(default=None, description="YouTube Video ID if applicable")
    channel_title: Optional[str] = Field(default=None, description="YouTube Channel title if applicable")
    has_transcript: Optional[bool] = Field(default=None, description="True if video captions/transcript available")


class NewsSourceStatus(BaseModel):
    source_id: str
    name: str
    category: str
    source_type: str = "rss"  # "rss", "api", "youtube", "official", "factcheck"
    status: str = "OK"  # "OK", "ERROR", "TIMEOUT", "DISABLED"
    enabled: bool = True
    article_count: int = 0
    error_message: Optional[str] = None
    feed_url: Optional[str] = None
    last_success: Optional[str] = None
    last_error: Optional[str] = None
    refresh_interval_sec: int = 300


class SourceConfig(BaseModel):
    source_id: str
    name: str
    category: str
    type: str = "rss"  # "rss", "api", "youtube", "official", "factcheck"
    url: str
    enabled: bool = True
    channel_id: Optional[str] = None
    refresh_interval_sec: int = 300
    last_success: Optional[str] = None
    last_error: Optional[str] = None
    article_count: int = 0


class ToggleSourceRequest(BaseModel):
    enabled: bool = Field(..., description="Target state for the source")


class AddSourceRequest(BaseModel):
    id: str = Field(..., min_length=2, max_length=50, description="Unique source identifier")
    name: str = Field(..., min_length=2, max_length=100, description="Display name of source")
    category: str = Field(default="General", description="Category: India, World, Health, Fact Check, etc.")
    type: str = Field(default="rss", description="Type: rss, youtube, official, factcheck")
    url: str = Field(..., description="Feed URL or YouTube channel URL")


class YouTubeTranscriptRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video identifier")


class YouTubeTranscriptResponse(BaseModel):
    video_id: str
    title: Optional[str] = None
    channel: Optional[str] = None
    has_transcript: bool = False
    transcript: Optional[str] = None
    word_count: int = 0
    note: Optional[str] = None


class NewsFeedResponse(BaseModel):
    articles: List[NewsArticleItem]
    total: int
    page: int
    limit: int
    total_pages: int
    sources: List[NewsSourceStatus]
    categories: List[str]
    source_types: List[str] = Field(default_factory=lambda: ["all", "rss", "api", "youtube", "official", "factcheck"])
    cached: bool = False
    last_updated: str


class FetchArticleRequest(BaseModel):
    url: str = Field(..., description="Target article URL to extract content from")


class FetchArticleResponse(BaseModel):
    url: str
    headline: Optional[str] = None
    content: Optional[str] = None
    has_full_text: bool = False
    content_availability: str = "summary-only"
    publisher: Optional[str] = None
    word_count: int = 0
    note: Optional[str] = None
