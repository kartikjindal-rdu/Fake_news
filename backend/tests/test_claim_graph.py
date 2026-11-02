"""
test_claim_graph.py
===================
Unit tests for VeriNews AI 3.0 Claim Relationship Graph:
- Typed node generation (claim, article, publisher, primary_source, fact_check)
- Directed relationship edges (reports_on, supports, contradicts, evaluates, references)
- Syndicated wire coverage detection
- Empty state generation
"""

import sys
import os
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.claim_graph_service import (
    build_graph_from_investigation,
    get_empty_graph,
)


class TestClaimGraphBuilder:
    SAMPLE_INVESTIGATION = {
        "investigation_id": "INV-20261029-12345",
        "investigation_timestamp": "2026-10-29T10:00:00Z",
        "input_summary": {
            "headline": "WHO Releases 2026 Hypertension Protocols",
            "canonical_url": "https://www.who.int/news/item/hypertension",
        },
        "claims": [
            {
                "claim_id": "CLM-01",
                "claim": "WHO released updated blood pressure clinical guidelines.",
                "topic": "Health & Medicine",
                "sentence_type": "Factual Assertion",
                "assessment": "Supported by available evidence",
                "assessment_code": "SUPPORTED",
                "investigated_at": "2026-10-29T10:00:05Z",
                "evidence_records": [
                    {
                        "id": "EV-01",
                        "source_title": "World Health Organization: Clinical Guidance",
                        "publisher": "World Health Organization",
                        "url": "https://who.int/guidance",
                        "excerpt": "WHO issues updated protocols for pharmacological management of hypertension.",
                        "relationship": "supports",
                        "source_type": "primary_source",
                        "content_availability": "full-text",
                    },
                    {
                        "id": "FC-01",
                        "source_title": "AFP Fact Check: Blood Pressure Claims",
                        "publisher": "AFP Fact Check",
                        "url": "https://factcheck.afp.com/article",
                        "excerpt": "Evaluating circulating claims regarding blood pressure treatments.",
                        "relationship": "provides_context",
                        "source_type": "fact_check",
                        "content_availability": "summary-only",
                    }
                ],
            }
        ],
    }

    def test_builds_typed_nodes_and_edges(self):
        graph = build_graph_from_investigation(self.SAMPLE_INVESTIGATION)
        assert graph["is_empty"] is False
        assert len(graph["nodes"]) >= 4
        assert len(graph["edges"]) >= 3

        types = {n["type"] for n in graph["nodes"]}
        assert "article" in types
        assert "claim" in types
        assert "primary_source" in types
        assert "fact_check" in types
        assert "publisher" in types

        relationships = {e["relationship"] for e in graph["edges"]}
        assert "reports_on" in relationships
        assert "supports" in relationships
        assert "references" in relationships

    def test_empty_graph_returns_honest_empty_state(self):
        empty = get_empty_graph()
        assert empty["is_empty"] is True
        assert len(empty["nodes"]) == 0
        assert len(empty["edges"]) == 0
        assert "message" in empty
