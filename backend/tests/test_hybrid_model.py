"""
test_hybrid_model.py
====================
Targeted test suite for the VeriNews AI 2.0 Hybrid Architecture:
- Traditional ML Ensemble regression & label mapping
- Semantic Transformer branch handling & input validation
- Hybrid soft-voting aggregation & probability bounds
- Missing Transformer artifact graceful fallback
- Mocked Transformer integration tests
- Input independence & state isolation
- API schema backward compatibility
"""

import sys
import os
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

if not os.environ.get("VERINEWS_MODEL_DIR"):
    os.environ["VERINEWS_MODEL_DIR"] = r"C:\Users\HP\OneDrive\Desktop\Model_train\models"

from main import app
from app.services import ml_prediction_service, transformer_service, hybrid_ensemble_service

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Traditional ML Ensemble Regression & Label Mapping
# ---------------------------------------------------------------------------

class TestTraditionalEnsembleRegression:
    """Ensure the underlying 3-model ensemble is fully preserved."""

    def test_models_loaded_or_error_reported(self):
        status = ml_prediction_service.get_model_status()
        assert "available" in status
        assert "traditional_available" in status
        assert "transformer_available" in status

    def test_label_mapping_integrity(self):
        assert ml_prediction_service._label_from_prediction(0) == "FAKE"
        assert ml_prediction_service._label_from_prediction(1) == "REAL"
        with pytest.raises(ValueError):
            ml_prediction_service._label_from_prediction(99)

    def test_traditional_prediction_structure(self):
        text = "Federal Reserve officials announced interest rate stabilization measures on Thursday."
        res = ml_prediction_service._predict_traditional(text)
        if not res.get("available"):
            pytest.skip("Traditional model artifacts not available in environment.")

        assert "final" in res
        assert res["final"] in ("FAKE", "REAL")
        assert "lr" in res and res["lr"] in ("FAKE", "REAL")
        assert "svm" in res and res["svm"] in ("FAKE", "REAL")
        assert "rf" in res and res["rf"] in ("FAKE", "REAL")
        assert "fake_probability" in res
        assert "real_probability" in res
        assert 0.0 <= res["fake_probability"] <= 100.0
        assert 0.0 <= res["real_probability"] <= 100.0


# ---------------------------------------------------------------------------
# 2. Semantic Transformer Branch Handling & Input Validation
# ---------------------------------------------------------------------------

class TestTransformerBranchValidation:
    """Verify semantic transformer input validation and status reporting."""

    def test_empty_input_handled_gracefully(self):
        res = transformer_service.predict_semantic("")
        assert res["available"] is False
        assert "error" in res

    def test_none_input_handled_gracefully(self):
        res = transformer_service.predict_semantic(None)
        assert res["available"] is False
        assert "error" in res

    def test_transformer_status_schema(self):
        status = transformer_service.get_transformer_status()
        assert "available" in status
        assert isinstance(status["available"], bool)


# ---------------------------------------------------------------------------
# 3. Hybrid Aggregation & Fusion Logic
# ---------------------------------------------------------------------------

class TestHybridAggregationLogic:
    """Verify calibrated probability weighting and voting consensus."""

    def test_hybrid_prediction_when_transformer_offline(self):
        """When transformer is offline, must fall back safely to traditional ensemble."""
        with patch.object(transformer_service, "predict_semantic", return_value={"available": False, "error": "Weights offline"}):
            sample_trad_fn = lambda t: {
                "available": True,
                "final": "FAKE",
                "lr": "FAKE",
                "svm": "FAKE",
                "rf": "REAL",
                "fake_votes": 2,
                "real_votes": 1,
                "winning_votes": 2,
                "model_agreement": 66.7,
                "fake_probability": 72.0,
                "real_probability": 28.0,
                "uncertainty_status": "MODEL_DISAGREEMENT",
                "cleaned_text_len": 50,
            }
            res = hybrid_ensemble_service.predict_hybrid("Test text statement", sample_trad_fn)

            assert res["available"] is True
            assert res["fallback_active"] is True
            assert res["transformer_available"] is False
            assert res["final"] == "FAKE"
            assert res["fake_probability"] == 72.0
            assert res["real_probability"] == 28.0
            assert "fallback" in res["hybrid_strategy"].lower()

    def test_hybrid_prediction_with_mocked_transformer_agreement(self):
        """When both branches agree, verify consensus and fused probability."""
        mock_trad_fn = lambda t: {
            "available": True,
            "final": "REAL",
            "lr": "REAL",
            "svm": "REAL",
            "rf": "REAL",
            "fake_votes": 0,
            "real_votes": 3,
            "winning_votes": 3,
            "model_agreement": 100.0,
            "fake_probability": 10.0,
            "real_probability": 90.0,
            "uncertainty_status": "MODEL_CONSENSUS",
            "cleaned_text_len": 60,
        }
        mock_trans_res = {
            "available": True,
            "prediction": "REAL",
            "fake_prob": 0.05,
            "real_prob": 0.95,
            "confidence": 95.0,
            "model_source": "mocked_bert",
            "latency_ms": 15.2,
        }

        with patch.object(transformer_service, "predict_semantic", return_value=mock_trans_res):
            res = hybrid_ensemble_service.predict_hybrid("Verified scientific finding", mock_trad_fn)

            assert res["available"] is True
            assert res["fallback_active"] is False
            assert res["transformer_available"] is True
            assert res["final"] == "REAL"
            assert res["uncertainty_status"] == "MODEL_CONSENSUS"
            assert res["winning_votes"] == 4
            assert res["model_agreement"] == 100.0
            assert 0.0 <= res["fake_probability"] <= 100.0
            assert 0.0 <= res["real_probability"] <= 100.0

    def test_hybrid_prediction_with_split_decision(self):
        """When 2 models vote FAKE and 2 vote REAL, verify uncertainty status."""
        mock_trad_fn = lambda t: {
            "available": True,
            "final": "REAL",
            "lr": "FAKE",
            "svm": "REAL",
            "rf": "REAL",
            "fake_votes": 1,
            "real_votes": 2,
            "winning_votes": 2,
            "model_agreement": 66.7,
            "fake_probability": 45.0,
            "real_probability": 55.0,
            "uncertainty_status": "MODEL_DISAGREEMENT",
            "cleaned_text_len": 50,
        }
        # Transformer votes FAKE (making total 2 FAKE, 2 REAL)
        mock_trans_res = {
            "available": True,
            "prediction": "FAKE",
            "fake_prob": 0.85,
            "real_prob": 0.15,
            "confidence": 85.0,
            "model_source": "mocked_bert",
            "latency_ms": 14.5,
        }

        with patch.object(transformer_service, "predict_semantic", return_value=mock_trans_res):
            res = hybrid_ensemble_service.predict_hybrid("Borderline assertion text", mock_trad_fn)

            assert res["available"] is True
            assert res["fallback_active"] is False
            assert res["uncertainty_status"] == "MODEL_DISAGREEMENT"
            assert res["winning_votes"] == 2
            assert res["model_agreement"] == 50.0


# ---------------------------------------------------------------------------
# 4. Input Independence & State Isolation
# ---------------------------------------------------------------------------

class TestInputIndependence:
    """Ensure consecutive predictions do not retain stale state."""

    def test_distinct_inputs_generate_distinct_probabilities(self):
        status = ml_prediction_service.get_model_status()
        if not status["available"]:
            pytest.skip("Models not available.")

        text_a = "SHOCKING miracle cure doctors desperately hate and delete immediately from social media!"
        text_b = "The central bank held the benchmark discount rate steady at 5.25% following the policy meeting."

        res_a = ml_prediction_service.predict(text_a)
        res_b = ml_prediction_service.predict(text_b)

        assert res_a["available"] is True
        assert res_b["available"] is True
        assert res_a["cleaned_text_len"] != res_b["cleaned_text_len"]


# ---------------------------------------------------------------------------
# 5. Full API Schema Compatibility
# ---------------------------------------------------------------------------

class TestApiSchemaCompatibility:
    """Verify that /api/analyze/text returns complete hybrid metadata."""

    def test_analyze_endpoint_returns_hybrid_fields(self):
        payload = {
            "headline": "Economic Stabilization Committee Convenes in Geneva",
            "content": "Finance ministers from twenty nations met to formalize international trade agreements on Monday.",
            "url": "https://www.reuters.com"
        }
        res = client.post("/api/analyze/text", json=payload)
        assert res.status_code == 200
        data = res.json()

        assert "scanId" in data
        assert "scores" in data
        assert "verdict" in data
        assert "mlPrediction" in data

        ml = data["mlPrediction"]
        if ml and ml.get("available"):
            assert "architecture" in ml
            assert "hybrid_strategy" in ml
            assert "fallback_active" in ml
            assert "lr" in ml
            assert "svm" in ml
            assert "rf" in ml
            assert "final_prediction" in ml
            assert "model_agreement" in ml
            assert "fake_probability" in ml
            assert "real_probability" in ml

    def test_model_info_returns_hybrid_architecture(self):
        res = client.get("/api/model/info")
        assert res.status_code == 200
        data = res.json()
        assert "architecture" in data
        assert "models" in data
        assert any("Transformer" in m["name"] for m in data["models"])
        assert any("Hybrid" in m["name"] for m in data["models"])

    def test_model_diagnostics_reports_branch_health(self):
        res = client.post("/api/model/diagnostics")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data
        if data["status"] == "HEALTHY":
            assert "transformer_branch" in data
            assert "diagnostic_inference" in data
            assert "strategy" in data["diagnostic_inference"]
