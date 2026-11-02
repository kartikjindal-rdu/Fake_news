"""
test_master_upgrade.py
======================
Comprehensive regression tests for the VeritasAI / VeriNews AI 2.0 Master Upgrade:
- Feature 1: Live News Intelligence Feed & Sources (GDELT, Indian Feeds, Categories)
- Feature 2: Evidence-Based Claim Verification (Wikipedia OpenSearch, Contradictions, Insufficient Evidence)
- Feature 3: Advanced Model Studio (ISOT Ground Truth Metrics, Diagnostics)
- Feature 4: Hindi & Hinglish Script Forensics (Devanagari, Hinglish, English)
- Feature 5: News Timeline & Syndication Comparison
- Feature 7: Investigation Certificate Export (Self-Contained HTML/Printable Report)
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

if not os.environ.get("VERINEWS_MODEL_DIR"):
    os.environ["VERINEWS_MODEL_DIR"] = r"C:\Users\HP\OneDrive\Desktop\Model_train\models"

from main import app
from app.services import news_feed_service
from app.services import claim_verification_service
from app.services import language_service
from app.api import scans

client = TestClient(app)


# ============================================================================
# FEATURE 1: LIVE NEWS INTELLIGENCE FEED
# ============================================================================

class TestFeature1LiveNewsFeed:
    """Verify live news feed aggregator, sources, categories, and GDELT streams."""

    def test_sources_contain_indian_and_gdelt_streams(self):
        sources = news_feed_service.get_available_sources()
        source_ids = {s["id"] for s in sources}

        # Must include Indian sources
        assert "the_hindu_national" in source_ids
        assert "ndtv_india" in source_ids

        # Must include specialized GDELT streams
        assert "gdelt_india" in source_ids
        assert "gdelt_factcheck" in source_ids
        assert "gdelt_elections" in source_ids
        assert "gdelt_world" in source_ids

    def test_news_feed_categories_include_india_and_factcheck(self):
        res = client.get("/api/news/feed?limit=5")
        assert res.status_code == 200
        data = res.json()
        assert "categories" in data
        cats = set(data["categories"])
        assert "India" in cats
        assert "Fact Check" in cats
        assert "Elections" in cats
        assert "Science" in cats
        assert "Health" in cats
        assert "World" in cats

    def test_news_feed_pagination_structure(self):
        res = client.get("/api/news/feed?page=1&limit=6")
        assert res.status_code == 200
        data = res.json()
        assert "articles" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert data["page"] == 1
        assert data["limit"] == 6


# ============================================================================
# FEATURE 2: EVIDENCE-BASED CLAIM VERIFICATION
# ============================================================================

class TestFeature2ClaimVerification:
    """Verify claim extraction, open evidence lookup, and factual integrity."""

    def test_extract_factual_claims_heuristics(self):
        sample_text = (
            "The World Health Organization announced updated clinical guidelines on Monday for hypertension. "
            "The peer-reviewed clinical trial involved 12,000 participants across 15 countries. "
            "Scientists confirmed that benchmark blood pressure targets reduce cardiovascular mortality by 24%."
        )
        claims = claim_verification_service.extract_factual_claims_from_text(sample_text, max_claims=3)
        assert len(claims) >= 1
        assert all("claim" in c and "importance" in c for c in claims)

    def test_verify_known_medical_miracle_hoax_returns_contradicted(self):
        hoax_claim = "Ancient lemon peel home remedy dissolves all stages of cancer in 24 hours without medical intervention."
        result = claim_verification_service.verify_single_claim(hoax_claim)
        assert result["status"] == "CONTRADICTED"
        assert "oncology" in result["explanation"].lower() or "medical" in result["explanation"].lower()
        assert "limitations_disclaimer" in result

    def test_empty_claim_returns_insufficient_evidence(self):
        result = claim_verification_service.verify_single_claim("")
        assert result["status"] == "INSUFFICIENT_EVIDENCE"

    def test_api_claims_verify_endpoint(self):
        res = client.post("/api/claims/verify", json={"claim": "NASA James Webb Space Telescope oldest galaxy observation"})
        assert res.status_code == 200
        data = res.json()
        assert "status" in data
        assert "explanation" in data
        assert "evidence_sources" in data
        assert "limitations_disclaimer" in data

    def test_api_claims_extract_endpoint(self):
        text = "Federal Reserve benchmark interest rates remained unchanged at the recent central bank meeting."
        res = client.post("/api/claims/extract", json={"text": text, "max_claims": 2})
        assert res.status_code == 200
        data = res.json()
        assert "claims" in data
        assert len(data["claims"]) >= 1


# ============================================================================
# FEATURE 3: ADVANCED MODEL STUDIO & DIAGNOSTICS
# ============================================================================

class TestFeature3ModelStudio:
    """Verify ground-truth ISOT evaluation metrics and diagnostic endpoint."""

    def test_model_info_returns_isot_ground_truth_metrics(self):
        res = client.get("/api/model/info")
        assert res.status_code == 200
        data = res.json()
        assert "benchmark" in data
        bm = data["benchmark"]
        assert bm["dataset"]["test_samples"] == 8980
        assert bm["dataset"]["total_samples"] == 44898

        models = bm["models"]
        # Logistic Regression
        assert models["logistic_regression"]["accuracy"] == 98.7
        # Linear SVM
        assert models["linear_svm"]["accuracy"] == 99.1
        # Random Forest
        assert models["random_forest"]["accuracy"] == 98.9
        # Hybrid Ensemble
        assert models["hybrid_ensemble"]["accuracy"] == 99.2
        assert "confusion_matrix" in models["hybrid_ensemble"]

    def test_model_diagnostics_endpoint_runs_live_inference(self):
        res = client.post("/api/model/diagnostics")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data
        assert data["status"] in ("HEALTHY", "FAIL")
        if data["status"] == "HEALTHY":
            assert "diagnostic_inference" in data
            assert "latency_ms" in data["diagnostic_inference"]
            assert data["feature_count"] == 50000
            assert data["rf_feature_slice"] == 5000


# ============================================================================
# FEATURE 4: HINDI & HINGLISH SCRIPT FORENSICS
# ============================================================================

class TestFeature4HindiHinglishForensics:
    """Verify language detection and transparent disclosure of model limitations."""

    def test_devanagari_hindi_detection(self):
        hindi_text = "विश्व स्वास्थ्य संगठन ने उच्च रक्तचाप के इलाज के लिए नए दिशा-निर्देश जारी किए हैं।"
        res = language_service.detect_language(hindi_text)
        assert res["detected_language"] == "Hindi (Devanagari)"
        assert res["is_ml_supported"] is False
        assert "warning" in res

    def test_transliterated_hinglish_detection(self):
        hinglish_text = "bhai yeh sach hai kya dekho aur batao jaldi share karo"
        res = language_service.detect_language(hinglish_text)
        assert res["detected_language"] == "Hinglish"
        assert res["is_ml_supported"] is False

    def test_standard_english_news_detection(self):
        english_text = "The Federal Reserve held benchmark interest rates steady following a two-day monetary policy meeting."
        res = language_service.detect_language(english_text)
        assert res["detected_language"] == "English"
        assert res["is_ml_supported"] is True


# ============================================================================
# FEATURE 5: NEWS TIMELINE & SYNDICATION COMPARISON
# ============================================================================

class TestFeature5TimelineSyndication:
    """Verify topic timeline synthesis and syndication detection."""

    def test_news_timeline_endpoint(self):
        res = client.get("/api/news/timeline?q=health&limit=10")
        assert res.status_code == 200
        data = res.json()
        assert "query" in data
        assert "timeline" in data
        assert "has_syndication" in data
        assert "syndication_summary" in data


# ============================================================================
# FEATURE 7: INVESTIGATION REPORT EXPORT
# ============================================================================

class TestFeature7ReportExport:
    """Verify self-contained printable investigation certificates."""

    def test_export_nonexistent_scan_returns_404(self):
        res = client.get("/api/export/SCAN-DOESNOTEXIST-9999/export")
        assert res.status_code == 404

    def test_export_existing_scan_returns_valid_html_report(self):
        # 1. Create a scan record via analyze
        scan_req = {
            "headline": "WHO Releases Updated Guidelines on Respiratory Infections",
            "content": "GENEVA (Reuters) - The World Health Organization issued new global clinical treatment guidance on Monday.",
            "url": "https://www.who.int"
        }
        res_analyze = client.post("/api/analyze/text", json=scan_req)
        assert res_analyze.status_code == 200
        scan_id = res_analyze.json()["scanId"]

        # 2. Request export certificate
        res_export = client.get(f"/api/export/{scan_id}/export")
        assert res_export.status_code == 200
        assert "text/html" in res_export.headers.get("content-type", "")
        html_body = res_export.text
        assert "VERITASAI FORENSIC INTELLIGENCE REPORT" in html_body
        assert scan_id in html_body
        assert "RESEARCH & METHODOLOGICAL INTEGRITY DISCLAIMER" in html_body
        assert "window.print()" in html_body
