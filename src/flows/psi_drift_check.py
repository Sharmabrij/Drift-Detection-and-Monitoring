from prefect import flow, task
from src.utils.psi import calculate_psi
import pandas as pd
import os

@task
def load_data(reference_path: str, current_path: str):
    reference_df = pd.read_csv(reference_path)
    current_df = pd.read_csv(current_path)
    return reference_df, current_df

@task
def check_drift(reference_df, current_df, threshold=0.1):
    psi_score = calculate_psi(reference_df, current_df)
    drift_detected = psi_score > threshold
    return psi_score, drift_detected

@flow(name="PSI Drift Detection Flow")
def psi_drift_detection_flow(reference_path: str, current_path: str, threshold: float = 0.1):
    reference_df, current_df = load_data(reference_path, current_path)
    psi_score, drift_detected = check_drift(reference_df, current_df, threshold)
    print(f"PSI Score: {psi_score}")
    if drift_detected:
        print("⚠️ Drift detected!")
    else:
        print("✅ No significant drift detected.")

if __name__ == "__main__":
    # Default paths
    reference = "data/reference.csv"
    current = "data/current.csv"
    psi_drift_detection_flow(reference, current)
