from prefect import flow
import pandas as pd
import numpy as np
import os
from datetime import datetime

LOG_PATH = "logs/psi_drift_log.csv"

def generate_data():
    """Simulate reference and production data"""
    ref_data = np.random.normal(0, 1, 1000)
    prod_data = np.random.normal(0.5, 1, 1000)  # Simulated drift
    return ref_data, prod_data

def calculate_psi(ref, prod, bins=10):
    """Calculate the PSI score"""
    ref_hist, bin_edges = np.histogram(ref, bins=bins)
    prod_hist, _ = np.histogram(prod, bins=bin_edges)

    ref_perc = ref_hist / len(ref)
    prod_perc = prod_hist / len(prod)

    psi = np.sum((ref_perc - prod_perc) * np.log((ref_perc + 1e-6) / (prod_perc + 1e-6)))
    return psi

def get_drift_status(psi):
    if psi < 0.1:
        return "No Drift"
    elif psi < 0.25:
        return "Possible Drift"
    else:
        return "Likely Drift"

def log_psi_result(psi):
    """Append result to CSV log"""
    status = get_drift_status(psi)
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

    print(f"Logged: {now} | PSI: {round(psi, 4)} | Status: {status}")

@flow(name="PSI Drift Check")
def psi_drift_detection_flow():
    print("Running PSI drift detection...")

    ref_data, prod_data = generate_data()
    psi = calculate_psi(ref_data, prod_data)
    log_psi_result(psi)

if __name__ == "__main__":
    psi_drift_detection_flow()
