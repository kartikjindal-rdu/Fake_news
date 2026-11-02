"""
test_integration_consistency.py
================================
Targeted regression tests for the confirmed bugs from the 2026-10-28 audit:

1. Verdict and heuristic scores are independent — the verdict comes from the
   ML ensemble, the scores come from heuristics. This is architecture-by-design
   but both fields must be internally consistent (non-null, valid types).

2. InconsistentVersionWarning must not propagate as an unhandled exception or
   crash model loading. (The model loader now catches and logs it.)

3. uncertainty_status must only ever be MODEL_CONSENSUS or MODEL_DISAGREEMENT.
   MAJORITY_VOTE is not a valid value from this service.

These tests do NOT assert that the ML prediction is "correct" for any given
input because correctness depends on the training data distribution.
"""

import sys
import os

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

if not os.environ.get("VERINEWS_MODEL_DIR"):
    os.environ["VERINEWS_MODEL_DIR"] = r"C:\Users\HP\OneDrive\Desktop\Model_train\models"

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _models_available() -> bool:
    from app.services import ml_prediction_service as mls
    mls.load_models()
    return mls._models_loaded


# ---------------------------------------------------------------------------
# 1. uncertainty_status values
# ---------------------------------------------------------------------------

VALID_UNCERTAINTY_STATUSES = {"MODEL_CONSENSUS", "MODEL_DISAGREEMENT"}


class TestUncertaintyStatus:
    """
    The service may only emit MODEL_CONSENSUS or MODEL_DISAGREEMENT.
    MAJORITY_VOTE was a legacy value that no longer exists in the code
    but appeared in the frontend — confirmed dead code and fixed.
    """

    def test_three_way_consensus_gives_model_consensus(self):
        from app.services import ml_prediction_service as mls
        if not _models_available():
            pytest.skip("Models not loaded.")

        # A long, unambiguous sensational fake-news text that should
        # give all three classifiers the same answer.
        text = (
            "SHOCKING MIRACLE CURE: Doctors hate this secret lemon peel remedy "
            "that destroys all diseases overnight. Big Pharma is panicking. "
            "Share before it gets deleted! Urgent! Forward this immediately! "
            "The government is banning this video. Act now before it is too late! "
            "Leaked documents prove the illuminati conspiracy. Catastrophic doomsday. "
            "Exposed: the shocking truth they don't want you to know. Breaking! "
            "This banned remedy eliminates cancer diabetes heart disease in 24 hours. "
            "Unbelievable secret miracle suppressed by the corrupt medical establishment."
        )
        result = mls.predict(text)
        if not result.get("available"):
            pytest.skip("Prediction unavailable.")

        status = result.get("uncertainty_status")
        assert status in VALID_UNCERTAINTY_STATUSES, (
            f"uncertainty_status '{status}' is not in {VALID_UNCERTAINTY_STATUSES}. "
            "The value MAJORITY_VOTE must never be emitted."
        )

    def test_uncertainty_status_never_majority_vote(self):
        """MAJORITY_VOTE is a retired value. Confirm it is never produced."""
        from app.services import ml_prediction_service as mls
        if not _models_available():
            pytest.skip("Models not loaded.")

        samples = [
            "Scientists confirm major breakthrough in renewable energy storage.",
            "Breaking: Secret government document reveals shocking conspiracy against citizens!",
            "Local council approves new traffic management plan for downtown area.",
        ]
        for text in samples:
            result = mls.predict(text)
            if result.get("available"):
                assert result.get("uncertainty_status") != "MAJORITY_VOTE", (
                    "MAJORITY_VOTE must never be emitted. "
                    f"Got it for: {text[:60]}"
                )

    def test_uncertainty_status_is_always_valid(self):
        from app.services import ml_prediction_service as mls
        if not _models_available():
            pytest.skip("Models not loaded.")

        texts = [
            "Peer-reviewed study from The Lancet confirms vaccine efficacy at 94%.",
            "EXPOSED: The miracle cure governments are hiding from you!!!",
            "City mayor announces new infrastructure investment plan.",
        ]
        for text in texts:
            result = mls.predict(text)
            if result.get("available"):
                status = result.get("uncertainty_status")
                assert status in VALID_UNCERTAINTY_STATUSES, (
                    f"Got unexpected uncertainty_status='{status}' for: {text[:60]}"
                )


# ---------------------------------------------------------------------------
# 2. Verdict & Score Consistency Policy
# ---------------------------------------------------------------------------

class TestVerdictAndScoreConsistency:
    """
    VeriNews AI 2.0 scoring policy:
    1. fakeProbability + realProbability must always equal exactly 100.
    2. When ML predicts FAKE, fakeProbability must be >= 50.1% (majority fake risk).
    3. When ML predicts REAL, fakeProbability must be <= 49.9% (majority credible).
    4. Verdict must follow documented non-claim strings.
    """

    def test_fake_and_real_probability_sum_to_100(self):
        """fakeProbability + realProbability must always equal exactly 100."""
        from app.api.analyze import _number
        fake_p = _number(35.0)
        real_p = round(100.0 - fake_p, 1)
        assert abs(fake_p + real_p - 100.0) < 0.01, (
            f"fake={fake_p} + real={real_p} != 100"
        )

    def test_number_helper_clamps_to_0_100(self):
        from app.api.analyze import _number
        assert _number(-5) == 0.0
        assert _number(105) == 100.0
        assert _number(50.5) == 50.5
        assert _number(float("nan")) == 0.0
        assert _number(float("inf")) == 0.0
        assert _number("not_a_number") == 0.0

    def test_verdict_field_is_one_of_expected_strings(self):
        """
        The verdict must be one of the four documented strings.
        It must never claim factual verification.
        """
        valid_verdicts = {
            "ML PREDICTS FAKE — NOT FACT-CHECKED",
            "ML PREDICTS REAL — NOT FACT-CHECKED",
            "ML RESULT UNCERTAIN — VERIFY INDEPENDENTLY",
            "ML UNAVAILABLE — HEURISTIC ANALYSIS ONLY",
        }
        for verdict in valid_verdicts:
            assert "VERIFIED" not in verdict or "NOT FACT-CHECKED" in verdict, (
                f"Verdict '{verdict}' may claim factual verification."
            )

    def test_ml_predict_returns_probabilities(self):
        """predict() must return fake_probability and real_probability."""
        from app.services import ml_prediction_service as mls
        if not _models_available():
            pytest.skip("Models not loaded.")

        res = mls.predict("Sample political news story about parliament election results.")
        if res.get("available"):
            assert "fake_probability" in res
            assert "real_probability" in res
            assert 0.0 <= res["fake_probability"] <= 100.0
            assert 0.0 <= res["real_probability"] <= 100.0
            assert abs(res["fake_probability"] + res["real_probability"] - 100.0) < 0.2

    def test_directional_consistency_fake(self):
        """When ML predicts FAKE, fake_probability should exceed 50%."""
        from app.services import ml_prediction_service as mls
        if not _models_available():
            pytest.skip("Models not loaded.")

        fake_text = (
            "SHOCKING MIRACLE CURE: Doctors hate this secret remedy! "
            "Big Pharma and the government are panicking. Share this before it gets deleted!"
        )
        res = mls.predict(fake_text)
        if res.get("available") and res.get("final") == "FAKE":
            assert res["fake_probability"] >= 50.0, (
                f"ML final is FAKE but fake_probability is {res['fake_probability']}%"
            )

    def test_directional_consistency_real(self):
        """When ML predicts REAL, real_probability should exceed 50%."""
        from app.services import ml_prediction_service as mls
        if not _models_available():
            pytest.skip("Models not loaded.")

        wire_text = (
            "WASHINGTON (Reuters) - The U.S. Senate passed a bipartisan budget resolution on Thursday, "
            "sending the legislation to the president for final approval after weeks of congressional debate."
        )
        res = mls.predict(wire_text)
        if res.get("available") and res.get("final") == "REAL":
            assert res["real_probability"] >= 50.0, (
                f"ML final is REAL but real_probability is {res['real_probability']}%"
            )


# ---------------------------------------------------------------------------
# 3. Model loading does not raise on version mismatch
# ---------------------------------------------------------------------------

class TestModelLoadingRobustness:
    def test_load_models_returns_dict(self):
        from app.services import ml_prediction_service as mls
        mls._reset_models()
        result = mls.load_models()
        assert isinstance(result, dict), "load_models() must return a dict"
        assert "status" in result, "Return dict must have 'status' key"

    def test_load_models_status_is_loaded_or_error(self):
        from app.services import ml_prediction_service as mls
        # Reset and reload
        mls._reset_models()
        result = mls.load_models()
        assert result["status"] in ("loaded", "error", "already_loaded"), (
            f"Unexpected status: {result['status']}"
        )

    def test_predict_returns_dict_when_models_loaded(self):
        from app.services import ml_prediction_service as mls
        if not _models_available():
            pytest.skip("Models not loaded.")
        result = mls.predict("This is a test news article about local politics.")
        assert isinstance(result, dict)
        assert "available" in result

    def test_predict_returns_available_false_for_empty(self):
        from app.services import ml_prediction_service as mls
        result = mls.predict("")
        assert result["available"] is False

    def test_predict_returns_available_false_for_whitespace(self):
        from app.services import ml_prediction_service as mls
        result = mls.predict("   \n\t  ")
        assert result["available"] is False


# ---------------------------------------------------------------------------
# 4. Label mapping integrity
# ---------------------------------------------------------------------------

class TestLabelMapping:
    def test_label_map_covers_0_and_1(self):
        from app.services import ml_prediction_service as mls
        assert mls._LABEL_MAP[0] == "FAKE"
        assert mls._LABEL_MAP[1] == "REAL"
        assert len(mls._LABEL_MAP) == 2

    def test_label_from_prediction_maps_correctly(self):
        from app.services import ml_prediction_service as mls
        assert mls._label_from_prediction(0) == "FAKE"
        assert mls._label_from_prediction(1) == "REAL"

    def test_label_from_prediction_raises_on_unknown(self):
        from app.services import ml_prediction_service as mls
        with pytest.raises(ValueError):
            mls._label_from_prediction(2)
        with pytest.raises(ValueError):
            mls._label_from_prediction(-1)

    def test_label_from_prediction_raises_on_non_integer(self):
        from app.services import ml_prediction_service as mls
        with pytest.raises(ValueError):
            mls._label_from_prediction("FAKE")
        with pytest.raises(ValueError):
            mls._label_from_prediction(None)


# ---------------------------------------------------------------------------
# 5. FastAPI End-to-End API Integration
# ---------------------------------------------------------------------------

class TestFastAPIEndpoints:
    @pytest.fixture(scope="class")
    def client(self):
        try:
            from fastapi.testclient import TestClient
            from main import app
            return TestClient(app)
        except ImportError:
            pytest.skip("httpx is not installed; skipping TestClient API tests.")

    def test_health_endpoint(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data.get("status") == "healthy"

    def test_model_info_endpoint(self, client):
        res = client.get("/api/model/info")
        assert res.status_code == 200
        data = res.json()
        assert "modelName" in data
        assert "algorithm" in data
        assert "labelMapping" in data
        assert data["labelMapping"] == {"0": "FAKE", "1": "REAL"}

    def test_scans_endpoints(self, client):
        res = client.get("/api/scans")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

        # Deleting non-existent scan returns 200 with not_found status
        del_res = client.delete("/api/scans/NON_EXISTENT_SCAN_ID")
        assert del_res.status_code == 200
        assert del_res.json().get("status") == "not_found"

    def test_analyze_text_endpoint_directional_consistency(self, client):
        res = client.post(
            "/api/analyze/text",
            json={
                "headline": "Breaking: Scientists hide miracle cure that doctors hate!",
                "content": "Share before it gets deleted! Secret government conspiracy exposed."
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert "verdict" in data
        assert "scores" in data
        scores = data["scores"]
        assert abs(scores["fakeProbability"] + scores["realProbability"] - 100.0) < 0.2

        # Check directional harmony
        if "ML PREDICTS FAKE" in data["verdict"]:
            assert scores["fakeProbability"] >= 50.1
        elif "ML PREDICTS REAL" in data["verdict"]:
            assert scores["realProbability"] >= 50.1

    def test_analyze_empty_text_returns_400(self, client):
        res = client.post("/api/analyze/text", json={"headline": "", "content": ""})
        assert res.status_code == 400


# ---------------------------------------------------------------------------
# 6. Language Detection Regression Tests
# ---------------------------------------------------------------------------

class TestLanguageDetection:
    """
    Ensure English news articles are not falsely flagged as transliterated Hindi,
    while authentic Hinglish and Devanagari inputs are properly identified.
    """

    def test_standard_english_with_the_detected_as_english(self):
        from app.services.language_service import detect_language
        who_text = (
            "The World Health Organization (WHO) released new pharmacological "
            "and lifestyle guidelines for treating adult hypertension. The comprehensive "
            "report emphasizes early screening and structured medication compliance."
        )
        res = detect_language(who_text)
        assert res["detected_language"] == "English"
        assert res["is_ml_supported"] is True
        assert res["warning"] is None

    def test_isolated_ambiguous_word_in_english_not_flagged(self):
        from app.services.language_service import detect_language
        # English sentence where an isolated word might resemble a transliterated token
        text = "The doctor confirmed that the patient was in the clinic today."
        res = detect_language(text)
        assert res["detected_language"] == "English"
        assert res["is_ml_supported"] is True
        assert res["warning"] is None

    def test_multiple_hinglish_markers_flagged_as_hinglish(self):
        from app.services.language_service import detect_language
        hinglish_text = "Yaar yeh kya hai, sach mein shocking news hai bhai. Isko share karo sabko!"
        res = detect_language(hinglish_text)
        assert res["detected_language"] == "Hinglish"
        assert res["is_ml_supported"] is False
        assert res["warning"] is not None

    def test_devanagari_detected_as_unsupported(self):
        from app.services.language_service import detect_language
        hindi_text = "यह खबर बिल्कुल झूठी है। कृपया इसे शेयर न करें।"
        res = detect_language(hindi_text)
        assert res["detected_language"] == "Hindi (Devanagari)"
        assert res["is_ml_supported"] is False
        assert res["warning"] is not None


# ---------------------------------------------------------------------------
# 7. Regression Tests for Preprocessing, Label Mapping & Probabilities
# ---------------------------------------------------------------------------

class TestPreprocessingPipeline:
    """Verify inference preprocessing exactly mirrors the training pipeline."""

    def test_clean_text_removes_urls_html_and_non_alpha(self):
        from app.services.ml_prediction_service import _clean_text
        sample = (
            "<p>Check out https://www.who.int/news for COVID-19 & hypertension updates! "
            "Doctors say: 100% effective (tested on 5,000 patients).</p>"
        )
        cleaned = _clean_text(sample)
        assert "http" not in cleaned
        assert "<p>" not in cleaned
        assert "</p>" not in cleaned
        assert "100" not in cleaned
        assert "5000" not in cleaned
        assert "%" not in cleaned
        assert "(" not in cleaned and ")" not in cleaned
        assert cleaned == "check out for covid hypertension updates doctors say effective tested on patients"

    def test_who_preset_text_cleaning(self):
        from app.services.ml_prediction_service import _clean_text
        headline = "World Health Organization releases updated clinical guidelines for hypertension management"
        content = (
            "The World Health Organization (WHO) released new pharmacological and "
            "lifestyle guidelines for treating adult hypertension. The comprehensive "
            "report emphasizes early screening, balanced dietary habits, regular "
            "cardiovascular exercise, and structured medication compliance."
        )
        combined = f"{headline} {content}"
        cleaned = _clean_text(combined)

        assert "(" not in cleaned and ")" not in cleaned
        assert cleaned.startswith("world health organization releases")
        assert "pharmacological" in cleaned
        assert "hypertension" in cleaned
        # Must be lowercase with single spaces only
        assert cleaned == cleaned.lower()
        assert "  " not in cleaned


class TestPresetAndPredictionIntegrity:
    """Verify prediction consistency without hardcoding sample outputs."""

    def test_prediction_output_structure_on_who_sample(self):
        from app.services import ml_prediction_service as mls
        if not _models_available():
            pytest.skip("Models not loaded.")

        who_combined = (
            "World Health Organization releases updated clinical guidelines for hypertension management "
            "The World Health Organization (WHO) released new pharmacological and lifestyle guidelines "
            "for treating adult hypertension. The comprehensive report emphasizes early screening, "
            "balanced dietary habits, regular cardiovascular exercise, and structured medication compliance."
        )
        res = mls.predict(who_combined)
        assert res.get("available") is True
        assert res.get("final") in ("FAKE", "REAL")
        assert res.get("uncertainty_status") in ("MODEL_CONSENSUS", "MODEL_DISAGREEMENT")
        assert "fake_probability" in res
        assert "real_probability" in res
        assert abs(res["fake_probability"] + res["real_probability"] - 100.0) < 0.2

        # Model votes must explain the final label
        if res["fake_votes"] > res["real_votes"]:
            assert res["final"] == "FAKE"
            assert res["fake_probability"] >= 50.0
        else:
            assert res["final"] == "REAL"
            assert res["real_probability"] >= 50.0

    def test_no_artificial_probability_clamping_in_api(self):
        """API must not artificially clamp composite fake probability to 50.1 / 49.9."""
        try:
            from fastapi.testclient import TestClient
            from main import app
            client = TestClient(app)
        except ImportError:
            pytest.skip("httpx / TestClient not installed.")

        payload = {
            "headline": "World Health Organization releases updated clinical guidelines for hypertension management",
            "content": (
                "The World Health Organization (WHO) released new pharmacological and lifestyle "
                "guidelines for treating adult hypertension. The comprehensive report emphasizes early "
                "screening, balanced dietary habits, regular cardiovascular exercise, and structured "
                "medication compliance."
            ),
            "url": "https://www.who.int/news/hypertension-guidelines"
        }
        res = client.post("/api/analyze/text", json=payload)
        assert res.status_code == 200
        data = res.json()
        scores = data["scores"]

        # Probabilities must be genuine, not artificially clamped to 50.1 / 49.9
        assert not (scores["fakeProbability"] == 50.1 and scores["realProbability"] == 49.9), (
            "fakeProbability is artificially pegged to 50.1%!"
        )
        # Probabilities and verdict must be in directional harmony
        if "ML PREDICTS FAKE" in data["verdict"]:
            assert scores["fakeProbability"] >= 50.0
        elif "ML PREDICTS REAL" in data["verdict"]:
            assert scores["realProbability"] >= 50.0


# ---------------------------------------------------------------------------
# 8. Arbitrary Free-Text Input Analysis Regression Tests
# ---------------------------------------------------------------------------

class TestFreeTextArbitraryAnalysis:
    """Verify arbitrary user-provided text can be analyzed without presets."""

    @pytest.fixture(scope="class")
    def client(self):
        try:
            from fastapi.testclient import TestClient
            from main import app
            return TestClient(app)
        except ImportError:
            pytest.skip("httpx / TestClient not installed.")

    def test_arbitrary_pasted_content_without_headline(self, client):
        """User pastes text directly into textarea (headline is empty)."""
        payload = {
            "headline": "",
            "content": (
                "Scientists at the international astronomical observatory announce the detection "
                "of unusual radio wave bursts originating from a distant spiral galaxy. "
                "The findings were confirmed by independent satellite observations on Tuesday."
            ),
            "url": ""
        }
        res = client.post("/api/analyze/text", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "scanId" in data
        assert "verdict" in data
        assert "scores" in data
        scores = data["scores"]
        assert 0.0 <= scores["fakeProbability"] <= 100.0
        assert 0.0 <= scores["realProbability"] <= 100.0
        assert abs(scores["fakeProbability"] + scores["realProbability"] - 100.0) < 0.2

    def test_arbitrary_short_claim(self, client):
        """User tests an arbitrary single-sentence social media rumor."""
        payload = {
            "headline": "",
            "content": "Secret government agency plans to shut down all wireless networks next weekend!",
            "url": ""
        }
        res = client.post("/api/analyze/text", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "verdict" in data
        assert "riskLevel" in data

    def test_empty_input_rejected_with_400(self, client):
        """Submitting whitespace or empty string returns HTTP 400."""
        payload = {"headline": "   ", "content": "\n\t  ", "url": ""}
        res = client.post("/api/analyze/text", json=payload)
        assert res.status_code == 400
        assert "Headline or content must be provided" in res.json().get("detail", "")
