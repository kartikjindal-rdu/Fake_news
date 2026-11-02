
"""
explainability_service.py
=========================

Provides feature-level explanations for the Logistic Regression
classifier using TF-IDF values and learned model coefficients.

DISCLAIMER:
These features represent statistical patterns learned from training
data. They are not factual evidence and do not prove whether an article
is real or fake.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

_DISCLAIMER = (
    "These features show statistical patterns learned from training data. "
    "They indicate model associations, not proof of deception or factual "
    "accuracy. Always verify claims using reliable independent sources."
)


def _safe_import():
    """Return the loaded TF-IDF vectorizer and Logistic Regression model."""
    try:
        from app.services import ml_prediction_service as mls

        if (
            getattr(mls, "_models_loaded", False)
            and getattr(mls, "_vectorizer", None) is not None
            and getattr(mls, "_lr_model", None) is not None
        ):
            return mls._vectorizer, mls._lr_model

    except Exception:
        logger.exception("Could not access loaded ML models.")

    return None, None


def get_influential_features(
    cleaned_text: str,
    top_n: int = 10
) -> Dict[str, Any]:
    """
    Calculate coefficient × TF-IDF contributions for the supplied text.

    Returns:
        status: "ok" or "unavailable"
        reason: Explanation availability details
        features: List of words and their contribution directions
        disclaimer: Explanation limitations
    """

    unavailable_result = {
        "status": "unavailable",
        "reason": None,
        "features": [],
        "disclaimer": _DISCLAIMER,
    }

    if not isinstance(cleaned_text, str) or not cleaned_text.strip():
        unavailable_result["reason"] = "No text available to explain."
        return unavailable_result

    if not isinstance(top_n, int) or isinstance(top_n, bool) or top_n < 1:
        unavailable_result["reason"] = "top_n must be a positive integer."
        return unavailable_result

    vectorizer, lr_model = _safe_import()

    if vectorizer is None or lr_model is None:
        unavailable_result["reason"] = "ML models are not loaded."
        return unavailable_result

    try:
        if not hasattr(lr_model, "coef_"):
            unavailable_result["reason"] = (
                "Logistic Regression model does not expose coefficients."
            )
            return unavailable_result

        coef_matrix = lr_model.coef_

        # This explanation implementation supports binary classification.
        if getattr(coef_matrix, "ndim", 0) != 2 or coef_matrix.shape[0] != 1:
            unavailable_result["reason"] = (
                "Only binary Logistic Regression explanations are supported."
            )
            return unavailable_result

        coefficients = coef_matrix[0]
        feature_names = vectorizer.get_feature_names_out()
        tfidf_vector = vectorizer.transform([cleaned_text])

        # Ensure the model and vectorizer use compatible feature dimensions.
        if len(coefficients) != len(feature_names):
            unavailable_result["reason"] = (
                "Model coefficients and vectorizer features do not match."
            )
            return unavailable_result

        if tfidf_vector.shape[1] != len(coefficients):
            unavailable_result["reason"] = (
                "Input vector has an incompatible feature dimension."
            )
            return unavailable_result

        tfidf_values = tfidf_vector.toarray()[0]

        # For binary sklearn Logistic Regression, positive contributions
        # push the decision toward classes_[1]; negative toward classes_[0].
        contributions = coefficients * tfidf_values

        import numpy as np

        nonzero_indices = np.flatnonzero(np.abs(contributions) > 1e-8)

        if len(nonzero_indices) == 0:
            unavailable_result["reason"] = (
                "No significant vocabulary features were found in this text."
            )
            return unavailable_result

        # Select the strongest positive and negative contributions by magnitude.
        ranked_indices = nonzero_indices[
            np.argsort(np.abs(contributions[nonzero_indices]))[::-1]
        ][:top_n]

        classes = getattr(lr_model, "classes_", None)

        if classes is None or len(classes) != 2:
            unavailable_result["reason"] = (
                "Could not determine the classifier's binary class labels."
            )
            return unavailable_result

        features: List[Dict[str, Any]] = []

        for idx in ranked_indices:
            contribution = float(contributions[idx])

            # Derive direction from the actual trained model's class order.
            # classes_ = [0, 1] where 0=FAKE, 1=REAL in the Project A pipeline.
            target_class = classes[1] if contribution > 0 else classes[0]
            # Map integer label to human-readable direction.
            _label_map = {0: "FAKE", 1: "REAL"}
            direction = _label_map.get(int(target_class), str(target_class).upper())

            features.append({
                "word": str(feature_names[idx]),
                "direction": direction,
                "contribution_score": round(abs(contribution), 6),
            })

        if not features:
            unavailable_result["reason"] = (
                "No significant contributing features were found."
            )
            return unavailable_result

        return {
            "status": "ok",
            "reason": None,
            "features": features,
            "disclaimer": _DISCLAIMER,
        }

    except Exception as exc:
        logger.exception("Explainability computation failed.")
        unavailable_result["reason"] = (
            "Explanation could not be computed. Check model and vectorizer "
            "compatibility."
        )
        return unavailable_result
