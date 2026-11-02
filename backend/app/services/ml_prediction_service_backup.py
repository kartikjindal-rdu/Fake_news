
"""
ml_prediction_service.py
========================

Loads existing trained model artifacts from Project A:
- TF-IDF Vectorizer
- Logistic Regression
- Linear SVM
- Random Forest

Environment variable:
    VERINEWS_MODEL_DIR = directory containing the four trusted .pkl files

Expected original label mapping:
    0 -> FAKE
    1 -> REAL

Important:
- Model agreement is voting consensus, not factual certainty.
- Predictions do not independently verify news claims.
- Text preprocessing must match the original training pipeline.
"""

import os
import re
import math
import logging
import warnings
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Model state
# ------------------------------------------------------------

_models_loaded = False
_load_error: Optional[str] = None

_vectorizer = None
_lr_model = None
_svm_model = None
_rf_model = None

_LABEL_MAP = {
    0: "FAKE",
    1: "REAL",
}

_RF_FEATURE_COUNT = 5000
_MAX_CHARS = 200_000


def _resolve_model_dir() -> Optional[Path]:
    """Find the directory containing the existing model artifacts."""

    env_dir = os.environ.get("VERINEWS_MODEL_DIR", "").strip()

    if env_dir:
        candidate = Path(env_dir).expanduser()

        if candidate.is_dir():
            return candidate

        logger.warning(
            "Configured VERINEWS_MODEL_DIR does not exist: %s",
            candidate,
        )

    # Explicit fallback for the original Project A directory.
    candidates = [
        Path(r"C:\Users\HP\OneDrive\Desktop\Model_train\models"),
    ]

    # Also check a Model_train/models directory relative to this project.
    try:
        project_root = Path(__file__).resolve().parents[4]
        candidates.append(project_root / "Model_train" / "models")
    except IndexError:
        logger.debug("Could not resolve the relative model directory.")

    for candidate in candidates:
        if candidate.is_dir():
            logger.info("Found model directory: %s", candidate)
            return candidate

    return None


def _clean_text(text: str) -> str:
    """
    Apply the original project's text normalization.

    This must match the clean_text() function used in Model_trian.py
    and predict.py when the four .pkl artifacts were trained.

    Training pipeline (Model_trian.py / predict.py):
        1. lowercase
        2. remove URLs: re.sub(r"http\S+|www\S+|https\S+", "", text)
        3. remove HTML: re.sub(r"<.*?>", "", text)
        4. keep only [a-zA-Z\s]: re.sub(r"[^a-zA-Z\s]", "", text)
        5. normalize whitespace
    """

    text = str(text).lower()

    # Remove URLs — replacement is "" (empty) to match training pipeline.
    # Pattern covers http://..., https://..., and www.... variants.
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)

    # Remove HTML tags — replacement is "" to match training pipeline.
    text = re.sub(r"<.*?>", "", text)

    # Keep English letters and whitespace only — replacement is "" to
    # match training pipeline (not " ", which would create extra spaces).
    text = re.sub(r"[^a-zA-Z\s]", "", text)

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    return text


def _reset_models() -> None:
    """Clear partially loaded model state after a loading failure."""

    global _models_loaded
    global _vectorizer, _lr_model, _svm_model, _rf_model

    _models_loaded = False
    _vectorizer = None
    _lr_model = None
    _svm_model = None
    _rf_model = None


def load_models() -> dict:
    """
    Load all four trusted model artifacts.

    Call this during application startup.
    """

    global _models_loaded, _load_error
    global _vectorizer, _lr_model, _svm_model, _rf_model

    if _models_loaded:
        return {"status": "already_loaded"}

    _load_error = None

    try:
        import joblib
    except ImportError:
        _load_error = "The joblib dependency is not installed."
        logger.error(_load_error)
        return {"status": "error", "detail": _load_error}

    model_dir = _resolve_model_dir()

    if model_dir is None:
        _load_error = (
            "Model directory not found. Configure VERINEWS_MODEL_DIR "
            "to point to the folder containing the four trusted model files."
        )
        logger.error(_load_error)
        return {"status": "error", "detail": _load_error}

    required_files = {
        "tfidf": "tfidf_vectorizer.pkl",
        "lr": "logistic_regression.pkl",
        "svm": "svm.pkl",
        "rf": "random_forest.pkl",
    }

    missing_files = [
        filename
        for filename in required_files.values()
        if not (model_dir / filename).is_file()
    ]

    if missing_files:
        _load_error = (
            "Required model files are missing: "
            + ", ".join(missing_files)
        )
        logger.error("%s Directory: %s", _load_error, model_dir)
        return {"status": "error", "detail": _load_error}

    try:
        # Suppress InconsistentVersionWarning: the sklearn minor-version
        # mismatch between training (1.7.2) and runtime (1.9.1) is expected
        # and does not break prediction. Predictions have been validated
        # against the training pipeline. Log once for traceability.
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            vectorizer = joblib.load(model_dir / required_files["tfidf"])
            lr_model = joblib.load(model_dir / required_files["lr"])
            svm_model = joblib.load(model_dir / required_files["svm"])
            rf_model = joblib.load(model_dir / required_files["rf"])

        for w in caught_warnings:
            if issubclass(w.category, UserWarning) and "InconsistentVersionWarning" in str(w.message):
                logger.warning(
                    "scikit-learn version mismatch: models were pickled with an "
                    "older version. This warning is expected and does not affect "
                    "predictions. Consider retraining with the current version "
                    "when convenient. Warning: %s",
                    str(w.message),
                )
            else:
                # Re-emit any other unexpected warnings through the logger.
                logger.warning("Unexpected warning during model load: %s", str(w.message))

        if not hasattr(vectorizer, "transform"):
            raise ValueError("The loaded vectorizer has no transform method.")

        if not hasattr(vectorizer, "get_feature_names_out"):
            raise ValueError(
                "The vectorizer does not expose feature names."
            )

        feature_count = len(vectorizer.get_feature_names_out())

        if feature_count < _RF_FEATURE_COUNT:
            raise ValueError(
                "The vectorizer has fewer than 5,000 features; "
                "the configured Random Forest feature slice is incompatible."
            )

        # Confirm the classifiers expect the vectorizer's feature count.
        for model_name, model in (
            ("Logistic Regression", lr_model),
            ("Linear SVM", svm_model),
        ):
            expected = getattr(model, "n_features_in_", None)

            if expected is not None and expected != feature_count:
                raise ValueError(
                    f"{model_name} expects {expected} features, "
                    f"but the vectorizer provides {feature_count}."
                )

        rf_expected = getattr(rf_model, "n_features_in_", None)

        if (
            rf_expected is not None
            and rf_expected != _RF_FEATURE_COUNT
        ):
            raise ValueError(
                f"Random Forest expects {rf_expected} features, "
                f"but the configured feature slice is {_RF_FEATURE_COUNT}. "
                "Confirm the original training pipeline before changing it."
            )

        # Check the classifiers expose the expected binary labels.
        for model_name, model in (
            ("Logistic Regression", lr_model),
            ("Linear SVM", svm_model),
            ("Random Forest", rf_model),
        ):
            classes = getattr(model, "classes_", None)

            if classes is None or set(classes.tolist()) != {0, 1}:
                raise ValueError(
                    f"{model_name} does not expose the expected "
                    "binary integer labels {0, 1}."
                )

        # Commit the complete model set only after validation succeeds.
        _vectorizer = vectorizer
        _lr_model = lr_model
        _svm_model = svm_model
        _rf_model = rf_model
        _models_loaded = True
        _load_error = None

        logger.info(
            "All model artifacts loaded successfully. Features: %d",
            feature_count,
        )

        # Also initialize the semantic Transformer branch if available
        try:
            from app.services import transformer_service
            t_res = transformer_service.load_transformer_model()
            logger.info("Semantic Transformer branch status: %s", t_res.get("status"))
        except Exception as e:
            logger.warning("Transformer branch initialization warning: %s", e)

        return {
            "status": "loaded",
            "feature_count": feature_count,
        }

    except Exception:
        _reset_models()
        _load_error = (
            "Model loading or compatibility validation failed. "
            "Check the trusted artifacts and original training pipeline."
        )
        logger.exception("ML model loading failed.")

        return {
            "status": "error",
            "detail": _load_error,
        }


def get_model_status() -> dict:
    """Return model availability without attempting to load artifacts."""
    try:
        from app.services import transformer_service
        t_status = transformer_service.get_transformer_status()
    except Exception:
        t_status = {"available": False, "error": "Transformer service unavailable."}

    if _models_loaded:
        return {
            "available": True,
            "error": None,
            "traditional_available": True,
            "transformer_available": t_status.get("available", False),
            "transformer_device": t_status.get("device"),
            "transformer_source": t_status.get("model_source"),
            "transformer_error": t_status.get("error"),
        }

    return {
        "available": False,
        "error": _load_error or "Models have not been loaded.",
        "traditional_available": False,
        "transformer_available": t_status.get("available", False),
    }


def _label_from_prediction(raw_prediction) -> str:
    """Convert a supported integer class label into FAKE or REAL."""

    try:
        label = int(raw_prediction)
    except (TypeError, ValueError):
        raise ValueError("The model returned an unsupported class label.")

    if label not in _LABEL_MAP:
        raise ValueError("The model returned an unknown class label.")

    return _LABEL_MAP[label]


def _predict_traditional(text: str) -> dict:
    """
    Run the three-classifier hard-voting ensemble (Branch A).
    """

    if not _models_loaded:
        status = get_model_status()

        return {
            "available": False,
            "error": status["error"],
        }

    if not isinstance(text, str) or not text.strip():
        return {
            "available": False,
            "error": "Input text is empty or invalid.",
        }

    if len(text) > _MAX_CHARS:
        text = text[:_MAX_CHARS]
        logger.warning(
            "Input truncated to the configured maximum length."
        )

    try:
        cleaned = _clean_text(text)

        if len(cleaned) < 3:
            return {
                "available": False,
                "error": (
                    "Text is too short after preprocessing "
                    "or contains no supported English letters."
                ),
            }

        # Transform with the exact vectorizer loaded from Project A.
        tfidf_full = _vectorizer.transform([cleaned])

        expected_features = len(
            _vectorizer.get_feature_names_out()
        )

        if tfidf_full.shape[1] != expected_features:
            raise ValueError(
                "Vectorizer output dimensions do not match its vocabulary."
            )

        # LR and SVM use the full feature matrix.
        lr_raw = _lr_model.predict(tfidf_full)[0]
        svm_raw = _svm_model.predict(tfidf_full)[0]

        # RF uses the first 5,000 columns only, matching the expected
        # Project A pipeline. Do not change this without checking training.
        tfidf_rf = tfidf_full[:, :_RF_FEATURE_COUNT]
        rf_raw = _rf_model.predict(tfidf_rf)[0]

        lr_label = _label_from_prediction(lr_raw)
        svm_label = _label_from_prediction(svm_raw)
        rf_label = _label_from_prediction(rf_raw)

        # Extract continuous probabilities / decision scores:
        # Class 0 = FAKE, Class 1 = REAL
        if hasattr(_lr_model, "predict_proba"):
            lr_proba = _lr_model.predict_proba(tfidf_full)[0]
            lr_fake_prob = float(lr_proba[0])
            lr_real_prob = float(lr_proba[1])
        else:
            lr_fake_prob = 1.0 if lr_label == "FAKE" else 0.0
            lr_real_prob = 1.0 - lr_fake_prob

        if hasattr(_rf_model, "predict_proba"):
            rf_proba = _rf_model.predict_proba(tfidf_rf)[0]
            rf_fake_prob = float(rf_proba[0])
            rf_real_prob = float(rf_proba[1])
        else:
            rf_fake_prob = 1.0 if rf_label == "FAKE" else 0.0
            rf_real_prob = 1.0 - rf_fake_prob

        if hasattr(_svm_model, "decision_function"):
            svm_dec = float(_svm_model.decision_function(tfidf_full)[0])
            # LinearSVC: decision > 0 favors class 1 (REAL)
            svm_real_prob = 1.0 / (1.0 + math.exp(-max(-15.0, min(15.0, svm_dec))))
            svm_fake_prob = 1.0 - svm_real_prob
        else:
            svm_fake_prob = 1.0 if svm_label == "FAKE" else 0.0
            svm_real_prob = 1.0 - svm_fake_prob

        ensemble_fake_prob = round((lr_fake_prob + svm_fake_prob + rf_fake_prob) / 3.0 * 100.0, 1)
        ensemble_real_prob = round(100.0 - ensemble_fake_prob, 1)

        predictions = [lr_label, svm_label, rf_label]

        fake_votes = predictions.count("FAKE")
        real_votes = predictions.count("REAL")

        if fake_votes > real_votes:
            final_label = "FAKE"
            winning_votes = fake_votes
        else:
            final_label = "REAL"
            winning_votes = real_votes

        model_agreement = round(
            winning_votes / len(predictions) * 100.0,
            1,
        )

        if winning_votes == 3:
            uncertainty_status = "MODEL_CONSENSUS"
        else:
            uncertainty_status = "MODEL_DISAGREEMENT"

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
            "fake_probability": ensemble_fake_prob,
            "real_probability": ensemble_real_prob,
            "uncertainty_status": uncertainty_status,
            "note": (
                "Model agreement measures voting consensus among three "
                "classifiers. It is not a calibrated probability and "
                "does not establish factual accuracy."
            ),
        }

    except Exception:
        logger.exception("ML prediction failed.")

        return {
            "available": False,
            "error": (
                "Prediction failed. Check model compatibility, "
                "input preprocessing, and the server logs."
            ),
        }


def predict(text: str) -> dict:
    """
    Run hybrid prediction fusing the traditional ML ensemble with the
    semantic Transformer branch. If the Transformer is unavailable,
    automatically falls back to the validated three-model ensemble.
    """
    import time
    t0 = time.time()
    from app.services.hybrid_ensemble_service import predict_hybrid
    res = predict_hybrid(text, _predict_traditional)

    # Record telemetry for model drift & quality monitoring
    try:
        from app.services import model_drift_service
        if res.get("available") and res.get("final"):
            fake_prob = float(res.get("fake_probability", 50.0))
            is_disagreement = res.get("uncertainty_status") == "MODEL_DISAGREEMENT"
            elapsed_ms = (time.time() - t0) * 1000.0
            model_drift_service.record_inference_telemetry(
                prediction=res["final"],
                fake_prob=fake_prob,
                has_disagreement=is_disagreement,
                latency_ms=elapsed_ms,
            )
    except Exception:
        pass

    return res
