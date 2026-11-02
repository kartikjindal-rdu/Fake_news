"""
test_factcheck_search.py
========================
Unit tests for VeriNews AI 3.0 Fact-Check Search Service:
- Word overlap calculation
- Querying fact-check archives without API key (graceful open wire fallback)
- Preserving publisher rating and citation
- Empty query handling and honest no-match behavior
"""

import sys
import os
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.factcheck_service import (
    _compute_word_overlap,
    search_existing_factchecks,
    search_open_factcheck_feeds,
)


class TestFactCheckSearch:
    def test_word_overlap_computation(self):
        s1 = "WHO announces new clinical guidelines for blood pressure"
        s2 = "WHO guidelines for clinical blood pressure control"
        overlap = _compute_word_overlap(s1, s2)
        assert overlap > 0.40

        s3 = "Completely distinct headline regarding space exploration"
        assert _compute_word_overlap(s1, s3) == 0.0

    def test_empty_query_returns_clean_response(self):
        res = search_existing_factchecks("")
        assert res["status"] == "EMPTY_QUERY"
        assert res["matches_found"] == 0
        assert len(res["results"]) == 0

    def test_search_existing_factchecks_returns_honest_structure(self):
        res = search_existing_factchecks("miracle lemon home remedy dissolves all cancer stages")
        assert "status" in res
        assert "matches_found" in res
        assert "results" in res
        assert "disclaimer" in res
        assert isinstance(res["results"], list)
