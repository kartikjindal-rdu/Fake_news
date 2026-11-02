
"""
VeriNews AI 2.0 - Final Source-Neutral Model Service

Loads the final trained package:
- TF-IDF Vectorizer
- Logistic Regression
- Linear SVM
- Random Forest
- Hybrid Ensemble

Label mapping:
0 = FAKE
1 = REAL
"""

import logging
import re
from pathlib import Path

import joblib

logger = logging.getLogger(__name__)

# Model state
_package = None
_vectorizer = None
_models = {}
_load_error = None

LABEL_MAP = {
    0: "FAKE",
    1: "REAL",
}


def _source_neutral_clean(text: str) -> str:
    """Must match the research training preprocessing."""

    text = str(text)

    source_patterns = {
        "Reuters": r"\breuters\b",
        "Associated Press": r"\bassociated press\b|\bap news\b",
        "BBC": r"\bbbc\b",
        "CNN": r"\bcnn\b",
        "AFP": r"\bafp\b",
        "New York Times": r"\bnew york times\b",
        "Washington Post": r"\bwashington post\b",
    }

    for pattern in source_patterns.values():
        text = re.sub(pattern, " ", text, flags=re.I)

    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)

    text = re.sub(
        r"\b[A-Z][A-Z\s,.-]{2,40}\s*\([A-Z][a-zA-Z\s]+\)\s*[-:]\s*",
        " ",
        text
    )

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def load_final_models():
    """Load the final trained model package."""

    global _package, _vectorizer, _models, _load_error

    if _package is not None:
        return True

    try:
        backend_root = Path(__file__).resolve().parents[2]

        model_path = (
            backend_root / "Model" / "final_verinews_model_package.pkl"
        )

        if not model_path.exists():
            raise FileNotFoundError(
                f"Final model package not found: {model_path}"
            )

        package = joblib.load(model_path)

        required_keys = {
            "vectorizer",
            "models",
            "label_mapping",
            "preprocessing",
            "training_features",
        }

        missing = required_keys - set(package.keys())

        if missing:
            raise ValueError(
                f"Model package is missing keys: {missing}"
            )

        if package["preprocessing"] != "final_source_clean":
            raise ValueError(
                "Unexpected preprocessing configuration."
            )

        required_models = {
            "Logistic Regression",
            "Linear SVM",
            "Random Forest",
            "Hybrid Ensemble",
        }

        missing_models = required_models - set(package["models"].keys())

        if missing_models:
            raise ValueError(
                f"Missing trained models: {missing_models}"
            )

        _package = package
        _vectorizer = package["vectorizer"]
        _models = package["models"]
        _load_error = None

        logger.info("Final source-neutral models loaded successfully.")

        return True

    except Exception as exc:
        _load_error = str(exc)
        logger.exception("Could not load final model package.")
        return False


def _get_label(prediction):
    """Convert model output to FAKE or REAL."""

    return LABEL_MAP.get(int(prediction), "UNKNOWN")


def predict_final(text: str) -> dict:
    """Run prediction using the final source-neutral model package."""

    if not isinstance(text, str) or not text.strip():
        return {
            "available": False,
            "error": "Please provide valid news text.",
        }

    if len(text) > 200_000:
        return {
            "available": False,
            "error": "Text exceeds the maximum length of 200,000 characters.",
        }

    if not load_final_models():
        return {
            "available": False,
            "error": _load_error or "Final models are unavailable.",
        }

    try:
        cleaned = _source_neutral_clean(text)

        if not cleaned:
            return {
                "available": False,
                "error": "No usable text remained after preprocessing.",
            }

        tfidf = _vectorizer.transform([cleaned])

        # Individual model predictions
        lr_raw = _models["Logistic Regression"].predict(tfidf)[0]
        svm_raw = _models["Linear SVM"].predict(tfidf)[0]
        rf_raw = _models["Random Forest"].predict(tfidf)[0]

        lr_label = _get_label(lr_raw)
        svm_label = _get_label(svm_raw)
        rf_label = _get_label(rf_raw)

        # Final trained VotingClassifier prediction
        hybrid_raw = _models["Hybrid Ensemble"].predict(tfidf)[0]
        final_label = _get_label(hybrid_raw)

        predictions = [lr_label, svm_label, rf_label]

        fake_votes = predictions.count("FAKE")
        real_votes = predictions.count("REAL")

        winning_votes = max(fake_votes, real_votes)

        model_agreement = round(
            winning_votes / len(predictions) * 100,
            1
        )

        # Consensus score, not a calibrated probability.
        fake_score = round(fake_votes / 3 * 100, 1)
        real_score = round(real_votes / 3 * 100, 1)

        uncertainty_status = (
            "MODEL_CONSENSUS"
            if winning_votes == 3
            else "MODEL_DISAGREEMENT"
        )

        return {
            "available": True,
            "error": None,
            "cleaned_text_len": len(cleaned),

            "lr": lr_label,
            "svm": svm_label,
            "rf": rf_label,
            "final": final_label,

            "fake_votes": fake_votes,
            "real_votes": real_votes,
            "winning_votes": winning_votes,
            "model_agreement": model_agreement,

            "fake_probability": fake_score,
            "real_probability": real_score,

            "uncertainty_status": uncertainty_status,

            "architecture": "Final Source-Neutral Hybrid Ensemble",
            "model_version": "VeriNews AI 2.0",

            "note": (
                "Scores represent three-model voting consensus, "
                "not calibrated probabilities or factual certainty. "
                "The model does not independently verify news claims."
            ),
        }

    except Exception as exc:
        logger.exception("Final model prediction failed.")

        return {
            "available": False,
            "error": f"Prediction failed: {str(exc)}",
        }


def get_final_model_status() -> dict:
    """Return final model loading status."""

    loaded = load_final_models()

    return {
        "available": loaded,
        "model_version": "VeriNews AI 2.0",
        "model_names": list(_models.keys()) if loaded else [],
        "preprocessing": (
            _package.get("preprocessing") if loaded else None
        ),
        "error": _load_error,
    }
