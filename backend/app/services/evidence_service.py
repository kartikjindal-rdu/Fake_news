
"""
evidence_service.py
===================

Retrieves real search results for claims submitted to VeriNews AI 2.0.

Configuration:
    EVIDENCE_SEARCH_PROVIDER=duckduckgo
    EVIDENCE_SEARCH_PROVIDER=serpapi
    EVIDENCE_SEARCH_API_KEY=your_key  # Required for SerpAPI

If no supported provider is configured, returns NOT_CONFIGURED.

Integrity rules:
    - Never invent snippets, sources, URLs, or citations.
    - Search results are not proof that a claim is true or false.
    - Every search result defaults to INSUFFICIENT_EVIDENCE.
    - Do not label claims SUPPORTED or REFUTED without actual verification.
"""

import os
import logging
import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

_NOT_CONFIGURED_RESPONSE = {
    "status": "NOT_CONFIGURED",
    "message": (
        "Evidence search is not configured. Configure "
        "EVIDENCE_SEARCH_PROVIDER to enable external retrieval. "
        "SerpAPI also requires EVIDENCE_SEARCH_API_KEY."
    ),
    "provider": None,
    "items": [],
    "retrieved_at": None,
    "note": (
        "No external evidence was retrieved. No sources or evidence "
        "have been fabricated."
    ),
}


def _utc_timestamp() -> str:
    """Return a timezone-aware UTC timestamp."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _empty_result(
    status: str,
    message: str,
    provider: Optional[str] = None,
    retrieved_at: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "status": status,
        "message": message,
        "provider": provider,
        "items": [],
        "retrieved_at": retrieved_at,
        "note": (
            "Search results do not establish factual accuracy. "
            "Independent verification is required."
        ),
    }


def retrieve_evidence(
    claim_text: str,
    max_results: int = 5,
) -> Dict[str, Any]:
    """
    Retrieve search results for a supplied claim.

    Status values:
        NOT_CONFIGURED
        OK
        NO_RESULTS
        ERROR

    Individual search results use INSUFFICIENT_EVIDENCE by default.
    """

    if not isinstance(claim_text, str) or not claim_text.strip():
        return _empty_result(
            "ERROR",
            "Claim text is empty or invalid.",
        )

    if (
        not isinstance(max_results, int)
        or isinstance(max_results, bool)
        or max_results < 1
    ):
        return _empty_result(
            "ERROR",
            "max_results must be a positive integer.",
        )

    # Avoid unexpectedly large external queries.
    max_results = min(max_results, 10)

    provider = os.environ.get(
        "EVIDENCE_SEARCH_PROVIDER", ""
    ).strip().lower()

    api_key = os.environ.get(
        "EVIDENCE_SEARCH_API_KEY", ""
    ).strip()

    # DuckDuckGo Instant Answer API does not require an API key.
    if provider == "duckduckgo":
        return _duckduckgo_search(
            claim_text,
            max_results,
            _utc_timestamp(),
        )

    if provider == "serpapi":
        if not api_key:
            return _NOT_CONFIGURED_RESPONSE.copy()

        return _serpapi_search(
            claim_text,
            max_results,
            _utc_timestamp(),
            api_key,
        )

    return _NOT_CONFIGURED_RESPONSE.copy()


def _duckduckgo_search(
    claim: str,
    max_results: int,
    retrieved_at: str,
) -> Dict[str, Any]:
    """
    Query DuckDuckGo's Instant Answer API.

    This API may return no results for ordinary news claims.
    It is not equivalent to a comprehensive web search.
    """

    try:
        import requests

        response = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": claim[:200],
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1,
            },
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()

        items = []

        def add_topic(topic: dict) -> None:
            if not isinstance(topic, dict):
                return

            snippet = topic.get("Text", "").strip()
            source_url = topic.get("FirstURL", "").strip()

            if not snippet or not source_url:
                return

            # Do not accept malformed or non-web source URLs.
            if not source_url.startswith(("https://", "http://")):
                return

            items.append({
                "snippet": snippet[:400],
                "source_title": (
                    topic.get("Text", "")[:100]
                    or "DuckDuckGo result"
                ),
                "url": source_url,
                "retrieved_at": retrieved_at,
                "evidence_status": "INSUFFICIENT_EVIDENCE",
                "note": (
                    "Retrieved from DuckDuckGo. This search result "
                    "does not independently verify the claim."
                ),
            })

        # RelatedTopics can contain nested topic groups.
        for topic in data.get("RelatedTopics", []):
            if len(items) >= max_results:
                break

            if not isinstance(topic, dict):
                continue

            if isinstance(topic.get("Topics"), list):
                for nested_topic in topic["Topics"]:
                    if len(items) >= max_results:
                        break
                    add_topic(nested_topic)
            else:
                add_topic(topic)

        # Use the API's abstract only if it includes an actual source URL.
        if (
            not items
            and data.get("AbstractText")
            and data.get("AbstractURL", "").startswith(
                ("https://", "http://")
            )
        ):
            items.append({
                "snippet": data["AbstractText"][:400],
                "source_title": (
                    data.get("AbstractSource")
                    or "DuckDuckGo abstract"
                ),
                "url": data["AbstractURL"],
                "retrieved_at": retrieved_at,
                "evidence_status": "INSUFFICIENT_EVIDENCE",
                "note": (
                    "Retrieved abstract. Its relevance and accuracy "
                    "must be checked against the original source."
                ),
            })

        if not items:
            return _empty_result(
                "NO_RESULTS",
                "DuckDuckGo returned no usable results for this query.",
                provider="DuckDuckGo Instant Answer API",
                retrieved_at=retrieved_at,
            )

        return {
            "status": "OK",
            "message": f"{len(items)} search result(s) retrieved.",
            "provider": "DuckDuckGo Instant Answer API",
            "items": items,
            "retrieved_at": retrieved_at,
            "note": (
                "Search results are not factual verification. "
                "All returned items remain INSUFFICIENT_EVIDENCE "
                "until independently assessed."
            ),
        }

    except Exception:
        logger.exception("DuckDuckGo evidence retrieval failed.")

        return _empty_result(
            "ERROR",
            "DuckDuckGo search could not be completed.",
            provider="DuckDuckGo",
            retrieved_at=retrieved_at,
        )


def _serpapi_search(
    claim: str,
    max_results: int,
    retrieved_at: str,
    api_key: str,
) -> Dict[str, Any]:
    """Query SerpAPI using a configured API key."""

    try:
        import requests

        response = requests.get(
            "https://serpapi.com/search",
            params={
                "q": claim[:200],
                "api_key": api_key,
                "engine": "google",
                "num": max_results,
                "hl": "en",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        # SerpAPI may return an API-level error in its JSON response.
        if data.get("error"):
            logger.warning("SerpAPI returned an API-level error.")
            return _empty_result(
                "ERROR",
                "The configured search provider returned an error.",
                provider="SerpAPI",
                retrieved_at=retrieved_at,
            )

        items = []

        for result in data.get("organic_results", [])[:max_results]:
            if not isinstance(result, dict):
                continue

            snippet = result.get("snippet", "").strip()
            title = result.get("title", "").strip()
            source_url = result.get("link", "").strip()

            if not snippet or not title:
                continue

            if not source_url.startswith(("https://", "http://")):
                continue

            items.append({
                "snippet": snippet[:400],
                "source_title": title[:200],
                "url": source_url,
                "retrieved_at": retrieved_at,
                "evidence_status": "INSUFFICIENT_EVIDENCE",
                "note": (
                    "Search result retrieved from Google via SerpAPI. "
                    "This snippet does not establish whether the claim "
                    "is true or false."
                ),
            })

        if not items:
            return _empty_result(
                "NO_RESULTS",
                "The search provider returned no usable results.",
                provider="SerpAPI",
                retrieved_at=retrieved_at,
            )

        return {
            "status": "OK",
            "message": f"{len(items)} search result(s) retrieved.",
            "provider": "SerpAPI (Google)",
            "items": items,
            "retrieved_at": retrieved_at,
            "note": (
                "Results require independent assessment. "
                "Search ranking and snippets are not fact-check verdicts."
            ),
        }

    except Exception:
        # Avoid exposing request details, credentials, or raw exceptions.
        logger.exception("SerpAPI evidence retrieval failed.")

        return _empty_result(
            "ERROR",
            "The configured search provider could not complete the request.",
            provider="SerpAPI",
            retrieved_at=retrieved_at,
        )
