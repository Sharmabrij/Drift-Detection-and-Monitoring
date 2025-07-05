import os
import pandas as pd
import numpy as np
from datetime import datetime
from flows.psi_drift_detection_flow import calculate_psi, get_drift_status, log_psi_result, LOG_PATH

def test_calculate_psi_returns_float():
    ref = np.random.normal(0, 1, 1000)
    prod = np.random.normal(0.2, 1, 1000)
    psi = calculate_psi(ref, prod)
    assert isinstance(psi, float)
    assert psi >= 0

def test_get_drift_status_thresholds():
    assert get_drift_status(0.05) == "No Drift"
    assert get_drift_status(0.15) == "Possible Drift"
    assert get_drift_status(0.3) == "Likely Drift"

def test_log_psi_result_creates_log_file(tmp_path):
    """Test that a log file is created and contains correct content"""
    test_log_path = tmp_path / "test_log.csv"
    test_psi = 0.123
    test_status = get_drift_status(test_psi)
    # Temporarily override log path
    original_path = LOG_PATH
    try:
        from flows import psi_drift_detection_flow
        psi_drift_detection_flow.LOG_PATH = str(test_log_path)
        log_psi_result(test_psi, test_status)
        assert test_log_path.exists()
        df = pd.read_csv(test_log_path)
        assert not df.empty
        assert "timestamp" in df.columns
        assert "psi_score" in df.columns
        assert "drift_status" in df.columns
    finally:
        psi_drift_detection_flow.LOG_PATH = original_path
