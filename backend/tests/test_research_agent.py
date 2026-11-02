"""
test_research_agent.py
======================
Unit tests for VeriNews AI 3.0 AI Research Agent workflow:
- Sentence classification (factual assertion vs opinion vs prediction vs rhetoric)
- Checkable claim extraction
- Targeted query generation
- Passage relationship evaluation (supports, contradicts, provides_context, unresolved)
- End-to-end research workflow synthesis
"""

import sys
import os
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.research_agent_service import (
    classify_sentence_type,
    extract_checkable_claims,
    generate_search_queries,
    evaluate_passage_relationship,
    execute_research_workflow,
)


class TestSentenceClassification:
    def test_identifies_factual_assertion(self):
        s = "The World Health Organization announced updated clinical guidelines for hypertension in Geneva."
        res = classify_sentence_type(s)
        assert res["is_checkable"] is True
        assert "Factual" in res["type"]

    def test_identifies_subjective_opinion(self):
        s = "In my opinion, this policy is arguably the most terrible decision ever made."
        res = classify_sentence_type(s)
        assert res["is_checkable"] is False
        assert "Opinion" in res["type"]

    def test_identifies_prediction(self):
        s = "Global electric vehicle sales are projected to reach 40 million units by 2030."
        res = classify_sentence_type(s)
        assert res["is_checkable"] is False
        assert "Prediction" in res["type"]

    def test_identifies_rhetorical_clickbait(self):
        s = "The shocking truth doctors hate will blow your mind and change everything you know!!!"
        res = classify_sentence_type(s)
        assert res["is_checkable"] is False
        assert "Rhetorical" in res["type"]


class TestClaimExtraction:
    def test_extracts_distinct_checkable_assertions(self):
        text = (
            "The Federal Reserve kept interest rates steady at 5.25 percent. "
            "I personally feel this was an amazing choice. "
            "NASA launched a new lunar observation satellite from Cape Canaveral."
        )
        claims = extract_checkable_claims(text, max_claims=3)
        assert len(claims) >= 2
        claim_texts = [c["claim"] for c in claims]
        assert any("Federal Reserve" in c for c in claim_texts)
        assert any("Cape Canaveral" in c for c in claim_texts)
        # Opinion should be excluded
        assert not any("personally feel" in c for c in claim_texts)


class TestQueryGeneration:
    def test_generates_concise_keywords(self):
        claim = "NASA James Webb Space Telescope identified oldest galaxy dating back 300 million years."
        queries = generate_search_queries(claim)
        assert len(queries) >= 1
        q = queries[0].lower()
        assert "nasa" in q or "james" in q or "webb" in q
        assert "the" not in q.split()


class TestPassageRelationshipEvaluation:
    def test_evaluates_supporting_relationship(self):
        claim = "James Webb Space Telescope observed early cosmic galaxies."
        passage = "The James Webb Space Telescope is an infrared observatory designed to study early cosmic galaxies."
        rel = evaluate_passage_relationship(claim, passage)
        assert rel in ("supports", "provides_context")

    def test_evaluates_contradicting_medical_hoax(self):
        claim = "Lemon peel home remedy dissolves all stages of cancer in 24 hours overnight."
        passage = "Clinical pharmacology proves conventional therapies; no home remedy dissolves tumors overnight."
        rel = evaluate_passage_relationship(claim, passage)
        assert rel == "contradicts"

    def test_evaluates_unresolved_unrelated_passage(self):
        claim = "European Central Bank raised benchmark interest rates."
        passage = "Local football team won the championship match in sudden death penalty shootout."
        rel = evaluate_passage_relationship(claim, passage)
        assert rel == "unresolved"


class TestResearchWorkflowSynthesis:
    def test_workflow_runs_and_returns_structured_report(self):
        text = "WHO released global clinical guidelines for blood pressure management."
        inv = execute_research_workflow(text=text, headline="WHO Hypertension Guidelines", max_claims=2)
        assert inv["status"] == "COMPLETED"
        assert "investigation_id" in inv
        assert len(inv["claims"]) >= 1
        assert "overall_verdict" in inv
        assert "methodology" in inv
