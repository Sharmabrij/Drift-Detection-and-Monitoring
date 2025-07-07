from prometheus_client import Gauge, start_http_server
import time 
from prefect import flow
import pandas as pd
import numpy as np
import os
import requests
from datetime import datetime

gauge = Gauge("test_metric", "A test gauge")
# ✅ This must be OUTSIDE any flow or function
start_http_server(8000, addr="0.0.0.0")
print("📡 Prometheus server started on http://localhost:8000/metrics")

# ---- Config ----
LOG_PATH = "logs/psi_drift_log.csv"
import os

# Use env var if available, else fallback to hardcoded (safe for local dev only)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL") or "https://hooks.slack.com/services/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"
 # Set this as an environment variable
# if not SLACK_WEBHOOK_URL:
#     SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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" 
print("SLACK_WEBHOOK_URL =", os.getenv("SLACK_WEBHOOK_URL"))
# ---- Prometheus Metrics ----
psi_metric = Gauge("psi_score", "Population Stability Index (PSI) Score")
drift_status_metric = Gauge("psi_drift_status", "Drift Status: 0=No Drift, 1=Possible Drift, 2=Likely Drift")

# ---- PSI Calculation ----
def calculate_psi(ref, prod, bins=10):
    """Compute PSI between reference and production arrays."""
    if len(ref) == 0 or len(prod) == 0:
        raise ValueError("Input arrays must not be empty.")

    ref_hist, bin_edges = np.histogram(ref, bins=bins)
    prod_hist, _ = np.histogram(prod, bins=bin_edges)

    ref_perc = ref_hist / len(ref)
    prod_perc = prod_hist / len(prod)

    psi = np.sum((ref_perc - prod_perc) * np.log((ref_perc + 1e-6) / (prod_perc + 1e-6)))
    return psi

# ---- Drift Status ----
def get_drift_status(psi):
    if psi < 0.1:
        return "No Drift"
    elif psi < 0.25:
        return "Possible Drift"
    else:
        return "Likely Drift"

# ---- Data Generation ----
def generate_data():
    ref_data = np.random.normal(0, 1, 1000)
    prod_data = np.random.normal(0.5, 1, 1000)
    return ref_data, prod_data

# ---- Logging ----
def log_psi_result(psi, status):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = pd.DataFrame([{
        "timestamp": now,
        "psi_score": round(psi, 4),
        "drift_status": status
    }])
    os.makedirs("logs", exist_ok=True)

    if not os.path.exists(LOG_PATH):
        new_row.to_csv(LOG_PATH, index=False)
    else:
        new_row.to_csv(LOG_PATH, mode='a', header=False, index=False)

    print(f"📊 Logged: {now} | PSI: {round(psi, 4)} | Status: {status}")

# ---- Slack Alert ----
def send_slack_alert(psi, status):
    if status == "No Drift":
        return

    if not SLACK_WEBHOOK_URL:
        print("❌ SLACK_WEBHOOK_URL not set.")
        return

    message = {
        "text": f"⚠️ *PSI Drift Detected*\n• PSI: `{round(psi, 4)}`\n• Status: *{status}*"
    }

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=message)
        if response.status_code != 200:
            print(f"❌ Slack error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Slack alert failed: {e}")

# ---- Prefect Flow ----
@flow(name="PSI Drift Check")
def psi_drift_detection_flow():
    print("🚀 Running PSI drift detection...")

    ref_data, prod_data = generate_data()
    psi = calculate_psi(ref_data, prod_data)
    status = get_drift_status(psi)

    # Log to CSV
    log_psi_result(psi, status)

    # Update Prometheus metrics
    psi_metric.set(psi)
    status_map = {"No Drift": 0, "Possible Drift": 1, "Likely Drift": 2}
    drift_status_metric.set(status_map.get(status, -1))

    # Slack alert if needed
    send_slack_alert(psi, status)

# ---- Main Entrypoint ----
if __name__ == "__main__":
    psi_drift_detection_flow()

while True:
    gauge.set(42)
    time.sleep(2)
