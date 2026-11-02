"""
news.py
=======
FastAPI routes for the Live Multi-Channel News Feed and Source Management in VeriNews AI 2.0.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException, Path

from app.schemas.news import (
    NewsFeedResponse,
    FetchArticleRequest,
    FetchArticleResponse,
    ToggleSourceRequest,
    AddSourceRequest,
    YouTubeTranscriptRequest,
    YouTubeTranscriptResponse,
)
from app.services import news_feed_service, youtube_service

router = APIRouter()


@router.get("/feed", response_model=NewsFeedResponse)
def get_feed(
    category: Optional[str] = Query(None, description="Filter by category (e.g. India, World, Health, Science, Fact Check)"),
    source: Optional[str] = Query(None, description="Filter by source ID (e.g. bbc_world, the_hindu_national, yt_ndtv)"),
    source_type: Optional[str] = Query(None, description="Filter by channel type (rss, api, youtube, official, factcheck)"),
    search: Optional[str] = Query(None, description="Keyword search across headlines and descriptions"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(12, ge=1, le=50, description="Items per page"),
    refresh: bool = Query(False, description="Force cache invalidation and fetch fresh feeds"),
):
    """
    Fetch live news articles and broadcasts aggregated from Indian publishers,
    international outlets, official sources (WHO, UN), fact-checkers, YouTube channels, and GDELT.
    Responses are cached with a 5-minute TTL to prevent rate limiting.
    """
    try:
        response = news_feed_service.get_live_news_feed(
            category=category,
            source=source,
            source_type=source_type,
            search=search,
            page=page,
            limit=limit,
            force_refresh=refresh,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch live news feed: {str(e)}",
        )


@router.get("/sources")
def get_sources() -> List[Dict[str, Any]]:
    """Return all configured live news feed sources with their categories, types, and health telemetry."""
    return news_feed_service.get_sources_registry()


@router.post("/sources/{source_id}/toggle")
def toggle_source(
    source_id: str = Path(..., description="Machine identifier of the source"),
    payload: ToggleSourceRequest = ...,
):
    """Enable or disable a specific feed source in the multi-channel registry."""
    success = news_feed_service.toggle_source_status(source_id, payload.enabled)
    if not success:
        raise HTTPException(status_code=404, detail=f"Source ID '{source_id}' not found in registry.")
    return {
        "status": "success",
        "source_id": source_id,
        "enabled": payload.enabled,
        "message": f"Source '{source_id}' set to {'enabled' if payload.enabled else 'disabled'}.",
    }


@router.post("/sources/add")
def add_source(payload: AddSourceRequest):
    """
    Register a new feed endpoint with strict SSRF protection.
    Rejects private networks, loopback IPs, and cloud metadata endpoints.
    """
    success, message = news_feed_service.add_custom_source({
        "id": payload.id,
        "name": payload.name,
        "category": payload.category,
        "type": payload.type,
        "url": payload.url,
    })
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {
        "status": "success",
        "message": message,
        "source": {
            "id": payload.id,
            "name": payload.name,
            "category": payload.category,
            "type": payload.type,
            "url": payload.url,
        }
    }


@router.post("/youtube/transcript", response_model=YouTubeTranscriptResponse)
def get_youtube_transcript(payload: YouTubeTranscriptRequest):
    """
    Extract public video transcript or caption stream for a YouTube news broadcast.
    Falls back gracefully to video description when captions are disabled without fabricating.
    """
    return youtube_service.extract_youtube_transcript(payload.video_id)


@router.get("/timeline")
def get_timeline(
    q: str = Query("health guidelines OR election", description="Topic or headline keyword to inspect"),
    limit: int = Query(15, ge=1, le=50, description="Max articles to compare"),
) -> Dict[str, Any]:
    """
    Synthesize a multi-publisher coverage timeline for a topic,
    tracking publication timestamps and detecting syndication versus independent reporting.
    """
    return news_feed_service.get_topic_timeline(query=q, limit=limit)


@router.post("/fetch-article", response_model=FetchArticleResponse)
def fetch_article(req: FetchArticleRequest):
    """
    Safely extract full body text or YouTube transcript with SSRF protection.
    Returns explicit content availability level ("full-text", "summary-only", "headline-only").
    """
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail="Article URL is required.")

    return news_feed_service.fetch_article_content(req.url)
