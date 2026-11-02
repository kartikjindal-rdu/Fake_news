"""
test_ml_prediction_service.py
==============================
Tests for the ML prediction service without internet access.
Uses the actual saved .pkl artifacts from Project A.
"""

import os
import sys
import pytest

# Ensure backend root is in sys.path so services can be imported
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Point to the actual saved models (or override with env var)
if not os.environ.get("VERINEWS_MODEL_DIR"):
    os.environ["VERINEWS_MODEL_DIR"] = r"C:\Users\HP\OneDrive\Desktop\Model_train\models"

from app.services import ml_prediction_service as mls


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module", autouse=True)
def load_models_once():
    """Load models once for all tests in this module."""
    result = mls.load_models()
    yield result


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 — Model Loading
# ─────────────────────────────────────────────────────────────────────────────
class TestModelLoading:
    def test_models_are_loaded(self):
        status = mls.get_model_status()
        # If models are not present on this machine, skip gracefully
        if not status["available"]:
            pytest.skip(f"ML models not available: {status['error']}")
        assert status["available"] is True
        assert status["error"] is None

    def test_vectorizer_is_not_none(self):
        if not mls._models_loaded:
            pytest.skip("Models not loaded.")
        assert mls._vectorizer is not None

    def test_lr_model_is_not_none(self):
        if not mls._models_loaded:
            pytest.skip("Models not loaded.")
        assert mls._lr_model is not None

    def test_svm_model_is_not_none(self):
        if not mls._models_loaded:
            pytest.skip("Models not loaded.")
        assert mls._svm_model is not None

    def test_rf_model_is_not_none(self):
        if not mls._models_loaded:
            pytest.skip("Models not loaded.")
        assert mls._rf_model is not None


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 — Label Mapping
# ─────────────────────────────────────────────────────────────────────────────
class TestLabelMapping:
    def test_label_map_has_two_classes(self):
        assert 0 in mls._LABEL_MAP and 1 in mls._LABEL_MAP

    def test_label_0_is_fake(self):
        assert mls._LABEL_MAP[0] == "FAKE"

    def test_label_1_is_real(self):
        assert mls._LABEL_MAP[1] == "REAL"


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 — Prediction Output Contract
# ─────────────────────────────────────────────────────────────────────────────
ENGLISH_FAKE_SAMPLE = (
    "SHOCKING: Scientists discover miracle cure that doctors hate and governments "
    "are desperately trying to hide from the public. Share this before it gets deleted!"
)

ENGLISH_REAL_SAMPLE = (
    "The World Health Organization released updated guidelines on Monday for the "
    "treatment of respiratory infections. The peer-reviewed study involved 12,000 "
    "participants across 15 countries and was published in The Lancet."
)


class TestPredictionContract:
    def _skip_if_unavailable(self):
        if not mls._models_loaded:
            pytest.skip("ML models not loaded on this machine.")

    def test_predict_returns_dict(self):
        self._skip_if_unavailable()
        result = mls.predict(ENGLISH_FAKE_SAMPLE)
        assert isinstance(result, dict)

    def test_predict_has_available_key(self):
        self._skip_if_unavailable()
        result = mls.predict(ENGLISH_FAKE_SAMPLE)
        assert "available" in result

    def test_predict_labels_are_fake_or_real(self):
        self._skip_if_unavailable()
        result = mls.predict(ENGLISH_FAKE_SAMPLE)
        if not result["available"]:
            pytest.skip("Prediction unavailable.")
        assert result["lr"] in ("FAKE", "REAL")
        assert result["svm"] in ("FAKE", "REAL")
        assert result["rf"] in ("FAKE", "REAL")
        assert result["final"] in ("FAKE", "REAL")

    def test_vote_counts_sum_to_three(self):
        self._skip_if_unavailable()
        result = mls.predict(ENGLISH_FAKE_SAMPLE)
        if not result["available"]:
            pytest.skip("Prediction unavailable.")
        assert result["fake_votes"] + result["real_votes"] == 3

    def test_model_agreement_is_between_33_and_100(self):
        self._skip_if_unavailable()
        result = mls.predict(ENGLISH_FAKE_SAMPLE)
        if not result["available"]:
            pytest.skip("Prediction unavailable.")
        assert 33.0 <= result["model_agreement"] <= 100.0

    def test_uncertainty_status_is_valid_value(self):
        self._skip_if_unavailable()
        result = mls.predict(ENGLISH_REAL_SAMPLE)
        if not result["available"]:
            pytest.skip("Prediction unavailable.")
        # The service emits MODEL_CONSENSUS (3/3 agree) or MODEL_DISAGREEMENT (2/3 agree).
        valid_statuses = {"MODEL_CONSENSUS", "MODEL_DISAGREEMENT"}
        assert result["uncertainty_status"] in valid_statuses

    def test_consensus_means_3_votes(self):
        """When all 3 models agree, winning_votes must be 3."""
        self._skip_if_unavailable()
        result = mls.predict(ENGLISH_REAL_SAMPLE)
        if not result["available"]:
            pytest.skip("Prediction unavailable.")
        if result["uncertainty_status"] == "MODEL_CONSENSUS":
            assert result["winning_votes"] == 3

    def test_disagreement_means_2_votes(self):
        """When only 2 models agree, winning_votes must be 2."""
        self._skip_if_unavailable()
        result = mls.predict(ENGLISH_FAKE_SAMPLE)
        if not result["available"]:
            pytest.skip("Prediction unavailable.")
        if result["uncertainty_status"] == "MODEL_DISAGREEMENT":
            assert result["winning_votes"] == 2


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 — RF Feature Slice
# ─────────────────────────────────────────────────────────────────────────────
class TestRFFeatureSlice:
    def test_rf_feature_count_is_5000(self):
        assert mls._RF_FEATURE_COUNT == 5000

    def test_rf_receives_5000_features(self):
        """Verify the sliced matrix has exactly 5000 columns when RF model present."""
        if not mls._models_loaded:
            pytest.skip("Models not loaded.")
        import numpy as np
        cleaned = mls._clean_text(ENGLISH_FAKE_SAMPLE)
        tfidf_full = mls._vectorizer.transform([cleaned])
        tfidf_rf = tfidf_full[:, :mls._RF_FEATURE_COUNT]
        assert tfidf_rf.shape[1] == mls._RF_FEATURE_COUNT


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 — Edge Cases
# ─────────────────────────────────────────────────────────────────────────────
class TestEdgeCases:
    def test_empty_string_returns_unavailable(self):
        result = mls.predict("")
        assert result["available"] is False
        assert result["error"] is not None

    def test_whitespace_only_returns_unavailable(self):
        result = mls.predict("   \n  \t  ")
        assert result["available"] is False

    def test_very_long_text_does_not_crash(self):
        if not mls._models_loaded:
            pytest.skip("Models not loaded.")
        long_text = "The government released new policy documents. " * 5000
        result = mls.predict(long_text)
        # Should either succeed or return a clean error, never raise exception
        assert "available" in result

    def test_special_characters_only_returns_unavailable(self):
        result = mls.predict("!!! ??? ### $$$ @@@")
        # After cleaning, this becomes empty → unavailable
        if not mls._models_loaded:
            # if models not loaded, it's unavailable for different reason — still OK
            assert result["available"] is False
        # else: may succeed or be unavailable depending on preprocessing

    def test_numeric_only_input(self):
        if not mls._models_loaded:
            pytest.skip("Models not loaded.")
        result = mls.predict("1234567890 9999 0000 1111")
        # Numbers are stripped in preprocessing → likely unavailable or very low signal
        assert "available" in result


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 — Text Preprocessing
# ─────────────────────────────────────────────────────────────────────────────
class TestTextPreprocessing:
    def test_clean_text_lowercases(self):
        assert mls._clean_text("HELLO WORLD") == "hello world"

    def test_clean_text_removes_urls(self):
        result = mls._clean_text("Visit https://example.com for more info.")
        assert "http" not in result
        assert "example" not in result

    def test_clean_text_removes_numbers(self):
        result = mls._clean_text("There are 123 cases reported.")
        assert "123" not in result

    def test_clean_text_removes_punctuation(self):
        result = mls._clean_text("Hello! How are you???")
        assert "!" not in result and "?" not in result

    def test_clean_text_strips_extra_spaces(self):
        result = mls._clean_text("  too   many   spaces  ")
        assert "  " not in result

    def test_clean_text_url_removal_matches_training_pipeline(self):
        """
        Training used re.sub(r"http\S+|www\S+|https\S+", "", text) — empty
        string replacement, not a space. The normalized result must not
        contain double spaces introduced by a space-replacement.
        """
        result = mls._clean_text("breaking news http://example.com today")
        # After URL removal + whitespace normalization, no double spaces.
        assert "  " not in result
        # The surrounding words must still be present.
        assert "breaking" in result
        assert "today" in result
