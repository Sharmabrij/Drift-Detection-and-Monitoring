from prefect import flow
from src.psi_drift.compute_psi import calculate_psi
from src.psi_drift.load_data import load_reference_data, load_current_data

@flow(name="PSI Drift Check")
def psi_drift_detection_flow():
    ref_df = load_reference_data()
    curr_df = load_current_data()

    psi_value = calculate_psi(ref_df["feature"], curr_df["feature"])
    print(f"PSI between reference and current data: {psi_value:.4f}")

    if psi_value > 0.25:
        print("⚠️ Significant data drift detected!")
    elif psi_value > 0.1:
        print("⚠️ Moderate data drift detected.")
    else:
        print("✅ No significant drift detected.")

if __name__ == "__main__":
    psi_drift_detection_flow()
