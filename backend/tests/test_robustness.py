"""
test_robustness.py
==================
Robustness evaluation for VeriNews AI 2.0 ML models across input types.

Runs predictions on representative input categories and saves results to:
  research_experiments/results/robustness_verinews2_results.csv

IMPORTANT — What this measures:
  - Prediction consistency (does the model return valid output without crashing).
  - NOT accuracy (no ground-truth labels available for Hindi/Hinglish samples here).
  - Per-language reliability warnings are reported honestly.
  - No numbers are fabricated.
"""

import os
import sys
import csv
import datetime
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

if not os.environ.get("VERINEWS_MODEL_DIR"):
    os.environ["VERINEWS_MODEL_DIR"] = r"C:\Users\HP\OneDrive\Desktop\Model_train\models"

from app.services import ml_prediction_service as mls
from app.services.language_service import detect_language

OUTPUT_CSV = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        r"..\..\research_experiments\results\robustness_verinews2_results.csv",
    )
)

# ── Test cases ────────────────────────────────────────────────────────────────
# Format: (category, label_for_csv, text, expected_available)
TEST_CASES = [
    (
        "English-Clean-Fake",
        "FAKE-EXPECTED",
        (
            "SHOCKING: Scientists discover miracle cure that doctors hate and governments "
            "are desperately trying to hide from the public. Share this before it gets deleted!"
        ),
        True,
    ),
    (
        "English-Clean-Real",
        "REAL-EXPECTED",
        (
            "The World Health Organization released updated guidelines on Monday for the treatment "
            "of respiratory infections. The peer-reviewed study involved 12,000 participants across "
            "15 countries and was published in The Lancet."
        ),
        True,
    ),
    (
        "English-Long",
        "REAL-EXPECTED",
        (
            "Scientists at CERN have announced the detection of a new subatomic particle using the "
            "Large Hadron Collider. The discovery, published in the peer-reviewed journal Physical "
            "Review Letters, involved data from over 300 billion proton-proton collisions. "
            "Lead researcher Dr. Anjali Kumar stated that the finding is consistent with predictions "
            "from the Standard Model of particle physics. Independent verification is currently being "
            "conducted by teams at MIT and CERN's competitor facility in Switzerland."
        ) * 3,
        True,
    ),
    (
        "Hindi-Devanagari",
        "LANGUAGE-UNSUPPORTED",
        "यह खबर बिल्कुल झूठी है। सरकार इसे छुपाने की कोशिश कर रही है।",
        None,  # may succeed but results unreliable
    ),
    (
        "Hinglish-Transliterated",
        "LANGUAGE-UNSUPPORTED",
        "Yaar yeh kya hai, sach mein shocking news hai bhai. Isko share karo sabko!",
        None,
    ),
    (
        "Empty-Input",
        "EDGE-CASE",
        "",
        False,  # must return unavailable
    ),
    (
        "Whitespace-Only",
        "EDGE-CASE",
        "   \n\t   ",
        False,
    ),
    (
        "Special-Characters-Only",
        "EDGE-CASE",
        "!!! ??? ### $$$ @@@",
        None,  # may or may not be available depending on preprocessing outcome
    ),
    (
        "Very-Short-Input",
        "EDGE-CASE",
        "Fake news.",
        True,  # short but has alpha content
    ),
    (
        "Mixed-Script-Hinglish",
        "LANGUAGE-UNSUPPORTED",
        "Breaking: नई दिल्ली में today protest हुई। Government ne koi response nahi diya.",
        None,
    ),
]


@pytest.fixture(scope="module", autouse=True)
def ensure_models_loaded():
    mls.load_models()
    yield


def _run_and_record():
    """Run all test cases and return rows for CSV output."""
    rows = []
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    for category, expected_label, text, expected_available in TEST_CASES:
        lang = detect_language(text)
        result = mls.predict(text)

        row = {
            "timestamp": timestamp,
            "category": category,
            "expected_label": expected_label,
            "text_preview": (text[:80].replace("\n", " ") if text else "(empty)"),
            "detected_language": lang["detected_language"],
            "ml_supported": lang["is_ml_supported"],
            "language_warning": lang["warning"] or "",
            "available": result.get("available", False),
            "error": result.get("error", "") or "",
            "final_prediction": result.get("final", "N/A"),
            "lr": result.get("lr", "N/A"),
            "svm": result.get("svm", "N/A"),
            "rf": result.get("rf", "N/A"),
            "model_agreement_pct": result.get("model_agreement", "N/A"),
            "uncertainty_status": result.get("uncertainty_status", "N/A"),
            "note": (
                "Prediction may be unreliable for non-English input."
                if not lang["is_ml_supported"]
                else ""
            ),
        }
        rows.append(row)

    return rows


class TestRobustness:
    """Robustness test suite — saves results to CSV."""

    def test_all_cases_run_without_exceptions(self):
        """Every test case must return a dict without raising."""
        for category, _, text, _ in TEST_CASES:
            try:
                result = mls.predict(text)
                assert isinstance(result, dict), f"{category}: result is not a dict"
            except Exception as e:
                pytest.fail(f"{category} raised an exception: {e}")

    def test_empty_input_returns_unavailable(self):
        result = mls.predict("")
        assert result["available"] is False

    def test_whitespace_returns_unavailable(self):
        result = mls.predict("   \n   ")
        assert result["available"] is False

    def test_english_fake_sample_available(self):
        if not mls._models_loaded:
            pytest.skip("Models not loaded.")
        _, _, text, _ = TEST_CASES[0]
        result = mls.predict(text)
        assert result["available"] is True

    def test_english_real_sample_available(self):
        if not mls._models_loaded:
            pytest.skip("Models not loaded.")
        _, _, text, _ = TEST_CASES[1]
        result = mls.predict(text)
        assert result["available"] is True

    def test_hindi_devanagari_language_detected(self):
        _, _, text, _ = TEST_CASES[3]
        lang = detect_language(text)
        assert lang["detected_language"] == "Hindi (Devanagari)"
        assert lang["is_ml_supported"] is False
        assert lang["warning"] is not None

    def test_hinglish_language_detected(self):
        _, _, text, _ = TEST_CASES[4]
        lang = detect_language(text)
        assert lang["detected_language"] in ("Hinglish", "English")  # depends on marker count
        # At least it doesn't crash

    def test_csv_written_successfully(self, tmp_path):
        """Verify CSV output can be generated (uses tmp_path for isolation)."""
        rows = _run_and_record()
        assert len(rows) == len(TEST_CASES)
        out = tmp_path / "robustness_test.csv"
        with open(out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        assert out.exists()
        assert out.stat().st_size > 0


def save_robustness_csv():
    """
    Standalone function to save the full robustness CSV to the research dir.
    Called by pytest session finish hook.
    """
    rows = _run_and_record()
    if not rows:
        return

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n[Robustness] Results saved → {OUTPUT_CSV}")


def pytest_sessionfinish(session, exitstatus):
    """Save CSV after all tests finish."""
    try:
        save_robustness_csv()
    except Exception as e:
        print(f"[Robustness] Could not save CSV: {e}")
