"""
model_drift_service.py
======================
Monitors machine learning model quality, inference latency, prediction distributions,
and input domain shift for VeriNews AI 3.0.

Drift Safeguards & Integrity Principles:
1. Distinguishes input distribution shift from proven accuracy deterioration.
2. An input distribution change does NOT automatically mean accuracy has declined.
3. Explicitly reports "UNSUPERVISED_MONITORING" when ground-truth labels are unavailable.
4. Uses Population Stability Index (PSI) to detect statistical distribution divergence
   against the verified ISOT held-out test baseline.
5. Does NOT automatically retrain models on live web submissions; any retraining requires
   audited, labeled datasets and a reproducible validation pipeline.
6. Privacy-conscious: stores aggregated telemetry (bins, latencies, votes) rather than raw user submissions.
"""

import math
import time
import threading
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ============================================================================
# BASELINE DISTRIBUTIONS (from ISOT Held-Out Test Set: 8,980 samples)
# ============================================================================
ISOT_BASELINE = {
    "dataset": "ISOT Fake News Benchmark (Held-out Test Split)",
    "sample_count": 8980,
    "class_distribution": {
        "fake_percentage": 52.3,
        "real_percentage": 47.7,
    },
    # Expected probability bins: [0-0.2, 0.2-0.4, 0.4-0.6, 0.6-0.8, 0.8-1.0]
    "confidence_distribution": [0.45, 0.03, 0.04, 0.03, 0.45],
    "disagreement_rate_percentage": 2.1,
    "expected_accuracy_percentage": 99.2,
    "baseline_timestamp": "2026-10-28T00:00:00Z",
}

# In-memory thread-safe telemetry store
_TELEMETRY_LOCK = threading.Lock()
_MAX_HISTORY_ENTRIES = 1000

_LIVE_TELEMETRY: Dict[str, Any] = {
    "total_inferences": 0,
    "predictions": {"FAKE": 0, "REAL": 0},
    "disagreements": 0,
    "latencies_ms": [],
    "confidence_bins": [0, 0, 0, 0, 0],  # [0-0.2, 0.2-0.4, 0.4-0.6, 0.6-0.8, 0.8-1.0]
    "languages": {"English": 0, "Hindi/Hinglish": 0, "Other": 0},
    "start_timestamp": datetime.now(timezone.utc).isoformat(),
}


def record_inference_telemetry(
    prediction: str,
    fake_prob: float,
    has_disagreement: bool,
    latency_ms: float,
    language: str = "English",
) -> None:
    """
    Record privacy-preserving metrics for a single model inference.
    Stores numeric bins and counters only.
    """
    global _LIVE_TELEMETRY
    with _TELEMETRY_LOCK:
        _LIVE_TELEMETRY["total_inferences"] += 1
        
        # Verdict count
        pred_key = "FAKE" if prediction.upper() == "FAKE" else "REAL"
        _LIVE_TELEMETRY["predictions"][pred_key] += 1

        # Disagreement
        if has_disagreement:
            _LIVE_TELEMETRY["disagreements"] += 1

        # Latency (bounded deque)
        _LIVE_TELEMETRY["latencies_ms"].append(round(latency_ms, 2))
        if len(_LIVE_TELEMETRY["latencies_ms"]) > _MAX_HISTORY_ENTRIES:
            _LIVE_TELEMETRY["latencies_ms"] = _LIVE_TELEMETRY["latencies_ms"][-_MAX_HISTORY_ENTRIES:]

        # Confidence bin
        prob_norm = max(0.0, min(1.0, fake_prob / 100.0 if fake_prob > 1.0 else fake_prob))
        bin_idx = min(4, int(prob_norm * 5))
        _LIVE_TELEMETRY["confidence_bins"][bin_idx] += 1

        # Language
        lang_key = "Hindi/Hinglish" if "hindi" in language.lower() or "hinglish" in language.lower() else ("English" if "english" in language.lower() else "Other")
        _LIVE_TELEMETRY["languages"][lang_key] = _LIVE_TELEMETRY["languages"].get(lang_key, 0) + 1


def calculate_psi(baseline_dist: List[float], live_counts: List[int]) -> float:
    """
    Calculate Population Stability Index (PSI) between baseline probabilities
    and observed live distribution:
    PSI = sum((Actual% - Expected%) * ln(Actual% / Expected%))
    """
    total_live = sum(live_counts)
    if total_live < 10:
        return 0.0  # Insufficient sample size for reliable PSI

    psi = 0.0
    epsilon = 1e-4

    for expected_p, count in zip(baseline_dist, live_counts):
        actual_p = count / total_live
        # Smooth zero counts
        actual_p = max(epsilon, actual_p)
        expected_p = max(epsilon, expected_p)

        term = (actual_p - expected_p) * math.log(actual_p / expected_p)
        psi += term

    return round(psi, 4)


def get_model_drift_report() -> Dict[str, Any]:
    """
    Synthesize live telemetry, compare against ISOT baseline, and produce
    an honest model monitoring report.
    """
    with _TELEMETRY_LOCK:
        total = _LIVE_TELEMETRY["total_inferences"]
        preds = dict(_LIVE_TELEMETRY["predictions"])
        disagreements = _LIVE_TELEMETRY["disagreements"]
        latencies = list(_LIVE_TELEMETRY["latencies_ms"])
        bins = list(_LIVE_TELEMETRY["confidence_bins"])
        langs = dict(_LIVE_TELEMETRY["languages"])
        started_at = _LIVE_TELEMETRY["start_timestamp"]

    # Calculate live metrics
    fake_pct = round((preds["FAKE"] / max(1, total)) * 100.0, 1) if total > 0 else 50.0
    real_pct = round((preds["REAL"] / max(1, total)) * 100.0, 1) if total > 0 else 50.0
    disagreement_rate = round((disagreements / max(1, total)) * 100.0, 1) if total > 0 else 0.0

    avg_latency = round(sum(latencies) / max(1, len(latencies)), 2) if latencies else 0.0
    p95_latency = round(sorted(latencies)[int(len(latencies) * 0.95)], 2) if len(latencies) >= 20 else avg_latency

    # Calculate PSI on probability confidence distribution
    psi_score = calculate_psi(ISOT_BASELINE["confidence_distribution"], bins)

    if total < 15:
        drift_status = "INITIALIZING"
        drift_level = "Baseline Accumulation"
        drift_color = "text-slate-400 bg-slate-800"
        drift_explanation = "Accumulating live inference samples to construct statistical distribution."
    elif psi_score < 0.10:
        drift_status = "STABLE"
        drift_level = "Negligible Drift (PSI < 0.10)"
        drift_color = "text-emerald-400 bg-emerald-500/10 border-emerald-500/30"
        drift_explanation = "Current prediction distributions match the training baseline with high statistical fidelity."
    elif psi_score < 0.25:
        drift_status = "MODERATE_SHIFT"
        drift_level = "Moderate Distribution Shift (0.10 <= PSI < 0.25)"
        drift_color = "text-amber-400 bg-amber-500/10 border-amber-500/30"
        drift_explanation = "Input vocabulary or confidence distributions show moderate variation from training data. Continued monitoring advised."
    else:
        drift_status = "SIGNIFICANT_SHIFT"
        drift_level = "Substantial Shift (PSI >= 0.25)"
        drift_color = "text-rose-400 bg-rose-500/10 border-rose-500/30"
        drift_explanation = "Substantial shift in input distribution detected. Text styles or topics diverge noticeably from baseline."

    return {
        "evaluation_status": "UNSUPERVISED_MONITORING",
        "evaluation_notice": (
            "Ground-truth factual labels are unavailable for live web inputs. "
            "Telemetry measures statistical distribution shift and latency stability, "
            "not verified empirical accuracy."
        ),
        "drift_status": drift_status,
        "drift_level": drift_level,
        "drift_color": drift_color,
        "drift_explanation": drift_explanation,
        "psi_score": psi_score,
        "psi_thresholds": {
            "stable": "< 0.10",
            "moderate_shift": "0.10 - 0.25",
            "significant_shift": ">= 0.25",
        },
        "live_telemetry": {
            "total_inferences": total,
            "fake_rate_percentage": fake_pct,
            "real_rate_percentage": real_pct,
            "disagreement_rate_percentage": disagreement_rate,
            "average_latency_ms": avg_latency,
            "p95_latency_ms": p95_latency,
            "language_distribution": langs,
            "confidence_histogram": [
                {"bin": "0.0 - 0.2 (High Real)", "count": bins[0]},
                {"bin": "0.2 - 0.4 (Moderate Real)", "count": bins[1]},
                {"bin": "0.4 - 0.6 (Uncertain)", "count": bins[2]},
                {"bin": "0.6 - 0.8 (Moderate Fake)", "count": bins[3]},
                {"bin": "0.8 - 1.0 (High Fake)", "count": bins[4]},
            ],
            "window_started_at": started_at,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        },
        "baseline_comparison": {
            "dataset": ISOT_BASELINE["dataset"],
            "baseline_samples": ISOT_BASELINE["sample_count"],
            "expected_fake_percentage": ISOT_BASELINE["class_distribution"]["fake_percentage"],
            "expected_real_percentage": ISOT_BASELINE["class_distribution"]["real_percentage"],
            "expected_disagreement_rate": ISOT_BASELINE["disagreement_rate_percentage"],
            "expected_accuracy_held_out": ISOT_BASELINE["expected_accuracy_percentage"],
        },
        "drift_safeguards": [
            "Input distribution shift does not prove accuracy deterioration without labeled ground-truth evaluation data.",
            "Automatic retraining is disabled by design to prevent data poisoning and distribution corruption.",
            "Any future retraining must use an audited, reviewed dataset and reproducible validation pipelines.",
        ],
    }


def reset_telemetry_window() -> Dict[str, Any]:
    """Reset the live monitoring window for a new telemetry period."""
    global _LIVE_TELEMETRY
    with _TELEMETRY_LOCK:
        _LIVE_TELEMETRY = {
            "total_inferences": 0,
            "predictions": {"FAKE": 0, "REAL": 0},
            "disagreements": 0,
            "latencies_ms": [],
            "confidence_bins": [0, 0, 0, 0, 0],
            "languages": {"English": 0, "Hindi/Hinglish": 0, "Other": 0},
            "start_timestamp": datetime.now(timezone.utc).isoformat(),
        }
    return {"status": "SUCCESS", "message": "Telemetry window reset successfully."}
