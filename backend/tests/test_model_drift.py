"""
test_model_drift.py
===================
Unit tests for VeriNews AI 3.0 Model Drift & Quality Telemetry:
- Telemetry recording and bounded memory queue
- Statistical Population Stability Index (PSI) computation
- Model drift report generation and safeguard warnings
- Resetting observation window
"""

import sys
import os
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.model_drift_service import (
    record_inference_telemetry,
    calculate_psi,
    get_model_drift_report,
    reset_telemetry_window,
    ISOT_BASELINE,
)


class TestModelDriftTelemetry:
    def setup_method(self):
        reset_telemetry_window()

    def test_record_telemetry_accumulates_counts(self):
        record_inference_telemetry(prediction="FAKE", fake_prob=88.5, has_disagreement=False, latency_ms=12.4)
        record_inference_telemetry(prediction="REAL", fake_prob=14.2, has_disagreement=True, latency_ms=15.1)

        rep = get_model_drift_report()
        telemetry = rep["live_telemetry"]
        assert telemetry["total_inferences"] == 2
        assert telemetry["fake_rate_percentage"] == 50.0
        assert telemetry["real_rate_percentage"] == 50.0
        assert telemetry["disagreement_rate_percentage"] == 50.0

    def test_calculate_psi_zero_on_identical_distribution(self):
        baseline = [0.20, 0.20, 0.20, 0.20, 0.20]
        live_counts = [20, 20, 20, 20, 20]
        psi = calculate_psi(baseline, live_counts)
        assert psi < 0.01

    def test_calculate_psi_elevated_on_skewed_distribution(self):
        baseline = [0.45, 0.03, 0.04, 0.03, 0.45]
        # Extremely shifted towards center bin
        live_counts = [2, 5, 80, 5, 8]
        psi = calculate_psi(baseline, live_counts)
        assert psi > 0.25

    def test_drift_report_includes_unsupervised_safeguards(self):
        rep = get_model_drift_report()
        assert rep["evaluation_status"] == "UNSUPERVISED_MONITORING"
        assert any("accuracy deterioration" in s for s in rep["drift_safeguards"])
        assert any("retraining" in s for s in rep["drift_safeguards"])

    def test_reset_window_clears_metrics(self):
        record_inference_telemetry(prediction="FAKE", fake_prob=90.0, has_disagreement=False, latency_ms=10.0)
        reset_res = reset_telemetry_window()
        assert reset_res["status"] == "SUCCESS"

        rep = get_model_drift_report()
        assert rep["live_telemetry"]["total_inferences"] == 0
