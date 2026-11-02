"""
ml_prediction_service.py
========================

Primary traditional ML prediction service for VeriNews AI 2.0.
Integrates the final source-neutral trained model package:
- TF-IDF Vectorizer
- Logistic Regression
- Linear SVM
- Random Forest
- Hybrid Ensemble (VotingClassifier)

Features:
- Source-neutral text preprocessing matching research training.
- Multi-model consensus voting scores (0.0%, 33.3%, 66.7%, 100.0%).
- Compatible exports for explainability service (_vectorizer, _lr_model).
- Telemetry recording for model drift & quality monitoring.
"""

import os
import re
import logging
from typing import Optional

from app.services import final_model_service

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Model state & compatibility references
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

_MAX_CHARS = 200_000


def _clean_text(text: str) -> str:
    """
    Apply source-neutral text preprocessing matching the final model package.
    Used for both prediction and explainability consistency.
    """
    return final_model_service._source_neutral_clean(text)


def _reset_models() -> None:
    """Clear partially loaded model state after a loading failure."""
    global _models_loaded, _load_error
    global _vectorizer, _lr_model, _svm_model, _rf_model

    _models_loaded = False
    _vectorizer = None
    _lr_model = None
    _svm_model = None
    _rf_model = None


def load_models() -> dict:
    """
    Load the final trained source-neutral model package as the primary
    traditional ML prediction source.
    """
    global _models_loaded, _load_error
    global _vectorizer, _lr_model, _svm_model, _rf_model

    if _models_loaded and _vectorizer is not None and _lr_model is not None:
        feature_count = (
            len(_vectorizer.get_feature_names_out())
            if hasattr(_vectorizer, "get_feature_names_out")
            else 50000
        )
        return {"status": "already_loaded", "feature_count": feature_count}

    _load_error = None

    try:
        success = final_model_service.load_final_models()
        if not success:
            _load_error = (
                final_model_service._load_error
                or "Failed to load final source-neutral model package."
            )
            logger.error("Final model loading failed: %s", _load_error)
            return {"status": "error", "detail": _load_error}

        _vectorizer = final_model_service._vectorizer
        _lr_model = final_model_service._models.get("Logistic Regression")
        _svm_model = final_model_service._models.get("Linear SVM")
        _rf_model = final_model_service._models.get("Random Forest")
        _models_loaded = True
        _load_error = None

        feature_count = (
            len(_vectorizer.get_feature_names_out())
            if hasattr(_vectorizer, "get_feature_names_out")
            else 50000
        )
        logger.info(
            "Primary source-neutral model package loaded successfully. Features: %d",
            feature_count,
        )

        # Initialize optional semantic Transformer branch if available
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

    except Exception as exc:
        _reset_models()
        _load_error = (
            f"Model loading or compatibility validation failed: {str(exc)}"
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

    final_status = final_model_service.get_final_model_status()
    is_available = _models_loaded or final_status.get("available", False)

    if is_available:
        return {
            "available": True,
            "error": None,
            "traditional_available": True,
            "transformer_available": t_status.get("available", False),
            "transformer_device": t_status.get("device"),
            "transformer_source": t_status.get("model_source"),
            "transformer_error": t_status.get("error"),
            "model_version": final_status.get("model_version", "VeriNews AI 2.0"),
        }

    return {
        "available": False,
        "error": _load_error or final_status.get("error") or "Models have not been loaded.",
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
    Run prediction using the final source-neutral model package via final_model_service.
    """
    if not isinstance(text, str) or not text.strip():
        return {
            "available": False,
            "error": "Input text is empty or invalid.",
        }

    if len(text) > _MAX_CHARS:
        text = text[:_MAX_CHARS]
        logger.warning("Input truncated to configured maximum length.")

    # Execute source-neutral inference
    res = final_model_service.predict_final(text)
    if not res.get("available"):
        return res

    # Synchronize module-level references if loaded on demand
    global _models_loaded, _vectorizer, _lr_model, _svm_model, _rf_model
    if not _models_loaded and final_model_service._package is not None:
        _models_loaded = True
        _vectorizer = final_model_service._vectorizer
        _lr_model = final_model_service._models.get("Logistic Regression")
        _svm_model = final_model_service._models.get("Linear SVM")
        _rf_model = final_model_service._models.get("Random Forest")

    return res


def predict(text: str) -> dict:
    """
    Run hybrid prediction fusing the traditional source-neutral ML ensemble
    with the semantic Transformer branch. If the Transformer is unavailable,
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
