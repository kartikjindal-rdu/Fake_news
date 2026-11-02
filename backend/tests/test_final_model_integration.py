"""
test_final_model_integration.py
===============================
Dedicated verification & integration test suite for the VeriNews AI 2.0
final source-neutral model package:
1. Final model package loading
2. Prediction with valid news text
3. Empty input handling
4. Oversized input handling
5. Invalid input types handling
6. Logistic Regression output validation
7. Linear SVM output validation
8. Random Forest output validation
9. Hybrid Ensemble output validation
10. Transformer available scenario
11. Transformer unavailable scenario
12. Fallback behavior verification
13. API backward compatibility with /api/analyze/text and /api/model/info
14. Source-neutral preprocessing consistency across prediction & explainability
15. Explainability compatibility using the final source-neutral model artifacts
"""

import os
import sys
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app
from app.services import (
    final_model_service,
    ml_prediction_service,
    hybrid_ensemble_service,
    transformer_service,
    explainability_service,
)

client = TestClient(app)

SAMPLE_NEWS_VALID = (
    "The Federal Reserve announced on Wednesday that benchmark interest rates "
    "would remain unchanged following two days of economic policy deliberations. "
    "Central bank officials cited sustained progress toward labor market stability "
    "and balanced inflation indicators across major sectors."
)

SAMPLE_NEWS_CLICKBAIT = (
    "SHOCKING: Miracle cure discovered by rogue doctors that Big Pharma is desperately "
    "trying to ban! Forward this immediately before government censors delete this post!"
)


# ---------------------------------------------------------------------------
# 1. Final Model Package Loading
# ---------------------------------------------------------------------------
class TestFinalModelPackageLoading:
    """Verifies artifact presence, structure, and loading into memory."""

    def test_final_model_service_direct_load(self):
        loaded = final_model_service.load_final_models()
        assert loaded is True, f"Failed to load final models: {final_model_service._load_error}"
        status = final_model_service.get_final_model_status()
        assert status["available"] is True
        assert "Logistic Regression" in status["model_names"]
        assert "Linear SVM" in status["model_names"]
        assert "Random Forest" in status["model_names"]
        assert "Hybrid Ensemble" in status["model_names"]

    def test_ml_prediction_service_load(self):
        res = ml_prediction_service.load_models()
        assert res.get("status") in ("loaded", "already_loaded")
        assert res.get("feature_count", 0) > 0

    def test_ml_prediction_service_get_model_status(self):
        status = ml_prediction_service.get_model_status()
        assert status["available"] is True
        assert status["traditional_available"] is True
        assert "transformer_available" in status
        assert "model_version" in status


# ---------------------------------------------------------------------------
# 2. Input Boundary & Robustness Handling
# ---------------------------------------------------------------------------
class TestInputValidationAndBoundaries:
    """Tests empty, oversized, None, and invalid types."""

    def test_empty_string_input(self):
        res = ml_prediction_service._predict_traditional("")
        assert res["available"] is False
        assert "error" in res

    def test_whitespace_string_input(self):
        res = ml_prediction_service._predict_traditional("     ")
        assert res["available"] is False
        assert "error" in res

    def test_none_input(self):
        res = ml_prediction_service._predict_traditional(None)
        assert res["available"] is False
        assert "error" in res

    def test_invalid_type_integer(self):
        res = ml_prediction_service._predict_traditional(12345)
        assert res["available"] is False
        assert "error" in res

    def test_oversized_input_handled_gracefully(self):
        oversized = "News text sample. " * 15000  # > 200,000 characters
        res = ml_prediction_service.predict(oversized)
        assert "available" in res
        # Must either truncate and predict or return clean length error without crash
        if not res["available"]:
            assert "error" in res


# ---------------------------------------------------------------------------
# 3. Model Output Validation: LR, SVM, RF, Hybrid Ensemble
# ---------------------------------------------------------------------------
class TestIndividualAndEnsembleOutputs:
    """Verifies output format for all four trained classifiers."""

    def test_valid_news_traditional_prediction_fields(self):
        res = ml_prediction_service._predict_traditional(SAMPLE_NEWS_VALID)
        assert res["available"] is True
        assert res["lr"] in ("FAKE", "REAL")
        assert res["svm"] in ("FAKE", "REAL")
        assert res["rf"] in ("FAKE", "REAL")
        assert res["final"] in ("FAKE", "REAL")
        assert res["fake_votes"] + res["real_votes"] == 3
        assert res["winning_votes"] in (2, 3)
        assert res["model_agreement"] in (66.7, 100.0)

    def test_voting_consensus_score_semantics(self):
        """Validates that probabilities represent voting consensus percentages."""
        res = ml_prediction_service._predict_traditional(SAMPLE_NEWS_VALID)
        assert res["available"] is True
        # 3-model consensus must be discrete thirds (0.0%, 33.3%, 66.7%, 100.0%)
        assert res["fake_probability"] in (0.0, 33.3, 66.7, 100.0)
        assert res["real_probability"] in (0.0, 33.3, 66.7, 100.0)
        assert round(res["fake_probability"] + res["real_probability"], 1) == 100.0
        assert "consensus" in res["note"].lower()

    def test_clickbait_traditional_prediction(self):
        res = ml_prediction_service._predict_traditional(SAMPLE_NEWS_CLICKBAIT)
        assert res["available"] is True
        assert res["final"] in ("FAKE", "REAL")
        assert res["uncertainty_status"] in ("MODEL_CONSENSUS", "MODEL_DISAGREEMENT")


# ---------------------------------------------------------------------------
# 4. Hybrid Scenarios: Transformer Available vs Fallback
# ---------------------------------------------------------------------------
class TestHybridAndFallbackBehavior:
    """Verifies true hybrid orchestration and safe fallback mode."""

    def test_transformer_unavailable_triggers_fallback(self):
        with patch.object(
            transformer_service,
            "predict_semantic",
            return_value={"available": False, "error": "Offline"},
        ):
            res = ml_prediction_service.predict(SAMPLE_NEWS_VALID)
            assert res["available"] is True
            assert res["fallback_active"] is True
            assert res["transformer_available"] is False
            assert "fallback" in res["hybrid_strategy"].lower()
            assert res["fake_probability"] in (0.0, 33.3, 66.7, 100.0)
            assert res["real_probability"] in (0.0, 33.3, 66.7, 100.0)

    def test_transformer_available_preserves_independent_signal(self):
        mock_semantic = {
            "available": True,
            "prediction": "REAL",
            "fake_prob": 0.08,
            "real_prob": 0.92,
            "confidence": 92.0,
            "model_source": "mock_roberta",
            "latency_ms": 12.5,
        }
        with patch.object(transformer_service, "predict_semantic", return_value=mock_semantic):
            res = ml_prediction_service.predict(SAMPLE_NEWS_VALID)
            assert res["available"] is True
            assert res["fallback_active"] is False
            assert res["transformer_available"] is True
            assert res["transformer"] is not None
            assert res["transformer"]["prediction"] == "REAL"
            assert res["transformer_prediction"] == "REAL"
            # Consensus percentage must remain unpolluted by transformer float
            assert res["fake_probability"] in (0.0, 33.3, 66.7, 100.0)


# ---------------------------------------------------------------------------
# 5. Preprocessing Consistency: Prediction vs Explainability
# ---------------------------------------------------------------------------
class TestPreprocessingAndExplainabilityConsistency:
    """Verifies that prediction and explainability share source-neutral cleaning."""

    def test_source_neutral_clean_strips_wire_sources(self):
        wire_text = "WASHINGTON (Reuters) - Federal Reserve officials met today."
        cleaned = ml_prediction_service._clean_text(wire_text)
        assert "reuters" not in cleaned.lower()
        assert "(reuters)" not in cleaned.lower()

    def test_explainability_uses_same_cleaner_and_bound_models(self):
        ml_prediction_service.load_models()
        # Verify vectorizer and lr_model are bound
        assert ml_prediction_service._vectorizer is not None
        assert ml_prediction_service._lr_model is not None

        cleaned = ml_prediction_service._clean_text(SAMPLE_NEWS_VALID)
        expl_res = explainability_service.get_influential_features(cleaned, top_n=5)
        assert expl_res["status"] == "ok"
        assert len(expl_res["features"]) > 0
        for feat in expl_res["features"]:
            assert "word" in feat
            assert feat["direction"] in ("FAKE", "REAL")
            assert feat["contribution_score"] >= 0.0


# ---------------------------------------------------------------------------
# 6. API Integration: /api/analyze/text and /api/model/info
# ---------------------------------------------------------------------------
class TestApiEndpointCompatibility:
    """Verifies end-to-end API response schema compatibility."""

    def test_analyze_text_endpoint(self):
        payload = {
            "headline": "Economic Stabilization Committee Convenes",
            "content": SAMPLE_NEWS_VALID,
            "url": "https://www.example.com/news/economy",
        }
        resp = client.post("/api/analyze/text", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert "scanId" in data
        assert "verdict" in data
        assert "scores" in data
        assert "mlPrediction" in data
        assert "explainability" in data

        ml = data["mlPrediction"]
        assert ml["available"] is True
        assert ml["final_prediction"] in ("FAKE", "REAL")
        assert ml["fake_probability"] is not None
        assert ml["real_probability"] is not None
        assert ml["model_agreement"] is not None
        assert ml["lr"] in ("FAKE", "REAL")
        assert ml["svm"] in ("FAKE", "REAL")
        assert ml["rf"] in ("FAKE", "REAL")

    def test_model_info_endpoint(self):
        resp = client.get("/api/model/info")
        assert resp.status_code == 200
        data = resp.json()
        assert data["available"] is True
        assert "traditional_available" in data
        assert "models" in data
        assert len(data["models"]) >= 4
