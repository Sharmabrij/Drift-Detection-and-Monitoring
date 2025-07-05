from prefect import flow
import pandas as pd
import numpy as np
import os
import requests
from datetime import datetime

LOG_PATH = "logs/psi_drift_log.csv"

def calculate_psi(ref, prod, bins=10):
    if len(ref) == 0 or len(prod) == 0:
        raise ValueError("Input arrays must not be empty.")

    ref_hist, bin_edges = np.histogram(ref, bins=bins)
    prod_hist, _ = np.histogram(prod, bins=bin_edges)

    ref_perc = ref_hist / len(ref)
    prod_perc = prod_hist / len(prod)

    psi = np.sum((ref_perc - prod_perc) * np.log((ref_perc + 1e-6) / (prod_perc + 1e-6)))
    return psi
# ---- Slack Config ----
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"  # Replace with your actual webhook

def send_slack_alert(psi, status):
    """Send Slack alert only for drift"""
    if status == "No Drift":
        return  # Skip alert to avoid noise

    webhook_url = os.getenv("SLACK_WEBHOOK_URL")  # Use env var for security
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL not set.")
        return

    message = {
        "text": f"⚠️ PSI Drift Detected\nPSI: `{round(psi, 4)}`\nStatus: *{status}*",
    }

    try:
        response = requests.post(webhook_url, json=message)
        if response.status_code != 200:
            print(f"❌ Slack error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Slack alert failed: {e}")

def generate_data():
    ref_data = np.random.normal(0, 1, 1000)
    prod_data = np.random.normal(0.5, 1, 1000)
    return ref_data, prod_data

def get_drift_status(psi):
    if psi < 0.1:
        return "No Drift"
    elif psi < 0.25:
        return "Possible Drift"
    else:
        return "Likely Drift"

def log_psi_result(psi, status):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = pd.DataFrame([{
        "timestamp": now,
        "psi_score": round(psi, 4),
        "drift_status": status
    }])
    if not os.path.exists("logs"):
        os.makedirs("logs")
    if not os.path.exists(LOG_PATH):
        new_row.to_csv(LOG_PATH, index=False)
    else:
        new_row.to_csv(LOG_PATH, mode='a', header=False, index=False)
    print(f"📊 Logged: {now} | PSI: {round(psi, 4)} | Status: {status}")

@flow(name="PSI Drift Check")
def psi_drift_detection_flow():
    print("🚀 Running PSI drift detection...")

    ref_data, prod_data = generate_data()
    psi = calculate_psi(ref_data, prod_data)
    status = get_drift_status(psi)

    log_psi_result(psi, status)

    if status != "No Drift":
        send_slack_alert(psi, status)

if __name__ == "__main__":
    psi_drift_detection_flow()

