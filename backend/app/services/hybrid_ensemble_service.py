"""
hybrid_ensemble_service.py
==========================
Orchestrates the VeriNews AI 2.0 Hybrid Architecture:
Branch A: Primary Source-Neutral Traditional ML Ensemble (TF-IDF + LR, Linear SVM, Random Forest)
Branch B: Semantic Transformer (BERT / RoBERTa / DistilBERT sequence classifier)

Fusion & Consensus Strategy:
- Traditional three-model voting consensus percentages (0.0%, 33.3%, 66.7%, 100.0%)
  are preserved as consensus scores, NOT converted into artificial calibrated probabilities.
- Semantic Transformer provides an independent linguistic representation signal when available.
- Principled consensus evaluation across all active classifier decisions.
- Automatic, seamless fallback to the source-neutral 3-model ensemble if Transformer is offline.
- Zero fabricated predictions or synthetic probability blending.
"""

import os
import logging
from typing import Dict, Any, Tuple

from app.services import transformer_service

logger = logging.getLogger(__name__)

# Default fusion weights: traditional vs semantic transformer
DEFAULT_TRADITIONAL_WEIGHT = 0.45
DEFAULT_TRANSFORMER_WEIGHT = 0.55


def _get_ensemble_weights() -> Tuple[float, float]:
    """Retrieve validated ensemble weights from environment or defaults."""
    try:
        tw_env = os.environ.get("VERINEWS_TRANSFORMER_WEIGHT", "").strip()
        if tw_env:
            w_trans = float(tw_env)
            w_trans = max(0.05, min(0.95, w_trans))
            w_trad = round(1.0 - w_trans, 3)
            return w_trad, w_trans
    except (ValueError, TypeError):
        pass

    return DEFAULT_TRADITIONAL_WEIGHT, DEFAULT_TRANSFORMER_WEIGHT


def predict_hybrid(text: str, traditional_predict_fn) -> Dict[str, Any]:
    """
    Execute hybrid prediction across the source-neutral traditional ML branch
    and the semantic Transformer branch.

    Args:
        text: Input text to analyze.
        traditional_predict_fn: Callable that returns the traditional 3-model prediction dict.

    Returns:
        Structured dictionary matching analysis schema requirements.
    """
    # 1. Evaluate Branch A (Source-Neutral Traditional ML Ensemble)
    trad_res = traditional_predict_fn(text)

    # If traditional models failed or input was invalid, return the error
    if not trad_res.get("available"):
        return trad_res

    # 2. Evaluate Branch B (Semantic Transformer)
    trans_res = transformer_service.predict_semantic(text)

    w_trad, w_trans = _get_ensemble_weights()

    # Extract traditional branch consensus percentages
    trad_fake_prob_pct = float(trad_res.get("fake_probability", 50.0))
    trad_real_prob_pct = float(trad_res.get("real_probability", round(100.0 - trad_fake_prob_pct, 1)))
    trad_final = trad_res.get("final", "UNKNOWN")

    lr_vote = trad_res.get("lr", "UNKNOWN")
    svm_vote = trad_res.get("svm", "UNKNOWN")
    rf_vote = trad_res.get("rf", "UNKNOWN")

    # CASE 1: Transformer is Available -> True Hybrid Architecture
    if trans_res.get("available"):
        trans_fake_prob = float(trans_res.get("fake_prob", 0.5))
        trans_real_prob = float(trans_res.get("real_prob", 0.5))
        trans_vote = trans_res.get("prediction", "UNKNOWN")

        # Consensus tracking across all 4 classifiers
        all_votes = [lr_vote, svm_vote, rf_vote, trans_vote]
        fake_votes = all_votes.count("FAKE")
        real_votes = all_votes.count("REAL")
        winning_votes = max(fake_votes, real_votes)
        model_agreement = round((winning_votes / 4.0) * 100.0, 1)

        # Verdict logic: majority agreement; in 2-2 tie, traditional source-neutral ensemble decides
        if fake_votes > real_votes:
            final_verdict = "FAKE"
        elif real_votes > fake_votes:
            final_verdict = "REAL"
        else:
            final_verdict = trad_final

        if winning_votes == 4:
            uncertainty_status = "MODEL_CONSENSUS"
        elif winning_votes == 3:
            uncertainty_status = "MODEL_MAJORITY"
        else:
            uncertainty_status = "MODEL_DISAGREEMENT"

        return {
            "available": True,
            "error": None,
            "architecture": "Hybrid Source-Neutral Traditional ML + Semantic Transformer",
            "hybrid_strategy": "Source-Neutral Traditional Consensus + Independent Semantic Transformer Signal",
            "transformer_available": True,
            "fallback_active": False,
            "fallback_reason": None,
            "cleaned_text_len": trad_res.get("cleaned_text_len", len(text)),
            # Individual Model Votes
            "lr": lr_vote,
            "svm": svm_vote,
            "rf": rf_vote,
            "transformer": {
                "prediction": trans_vote,
                "confidence": trans_res.get("confidence"),
                "fake_prob": round(trans_fake_prob * 100.0, 1),
                "real_prob": round(trans_real_prob * 100.0, 1),
                "model_source": trans_res.get("model_source"),
                "latency_ms": trans_res.get("latency_ms"),
            },
            # Sub-Branch Summary Verdicts
            "traditional_prediction": trad_final,
            "transformer_prediction": trans_vote,
            # Final Hybrid Synthesis
            "final": final_verdict,
            "final_prediction": final_verdict,
            "fake_votes": fake_votes,
            "real_votes": real_votes,
            "winning_votes": winning_votes,
            "total_models": 4,
            "model_agreement": model_agreement,
            # Consensus probabilities preserved: NO pseudo-calibrated blending
            "fake_probability": trad_fake_prob_pct,
            "real_probability": trad_real_prob_pct,
            "traditional_fake_prob": trad_fake_prob_pct,
            "transformer_fake_prob": round(trans_fake_prob * 100.0, 1),
            "weights_used": {
                "traditional": w_trad,
                "transformer": w_trans,
            },
            "uncertainty_status": uncertainty_status,
            "note": (
                "Scores represent multi-model voting consensus, not calibrated factual probabilities. "
                "The semantic Transformer provides an independent representation signal and does "
                "not overwrite source-neutral voting consensus."
            ),
        }

    # CASE 2: Transformer is Unavailable -> Safe Source-Neutral Fallback
    fallback_reason = trans_res.get("error") or "Semantic Transformer checkpoint not loaded"
    logger.debug("Operating in traditional ensemble fallback mode: %s", fallback_reason)

    fake_votes = trad_res.get("fake_votes", 0)
    real_votes = trad_res.get("real_votes", 0)
    winning_votes = trad_res.get("winning_votes", max(fake_votes, real_votes))

    return {
        "available": True,
        "error": None,
        "architecture": "Hybrid Architecture (Traditional Fallback Mode)",
        "hybrid_strategy": "Fallback Mode: 3-Model Traditional Ensemble",
        "transformer_available": False,
        "fallback_active": True,
        "fallback_reason": fallback_reason,
        "cleaned_text_len": trad_res.get("cleaned_text_len", len(text)),
        # Individual Traditional Votes
        "lr": lr_vote,
        "svm": svm_vote,
        "rf": rf_vote,
        "transformer": None,
        # Sub-Branch Summary Verdicts
        "traditional_prediction": trad_final,
        "transformer_prediction": None,
        # Final Fallback Synthesis (Preserves working ensemble)
        "final": trad_final,
        "final_prediction": trad_final,
        "fake_votes": fake_votes,
        "real_votes": real_votes,
        "winning_votes": winning_votes,
        "total_models": 3,
        "model_agreement": trad_res.get("model_agreement", 66.7),
        "fake_probability": trad_fake_prob_pct,
        "real_probability": trad_real_prob_pct,
        "traditional_fake_prob": trad_fake_prob_pct,
        "transformer_fake_prob": None,
        "weights_used": {
            "traditional": 1.0,
            "transformer": 0.0,
        },
        "uncertainty_status": trad_res.get("uncertainty_status", "MODEL_DISAGREEMENT"),
        "note": (
            "Operating in fallback mode using the validated source-neutral three-model traditional ensemble. "
            "Predictions represent voting consensus scores, not calibrated probabilities."
        ),
    }
