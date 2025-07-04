from prefect import flow

@flow(name="PSI Drift Check")
def psi_drift_detection_flow():
    print("Running PSI drift detection...")

if __name__ == "__main__":
    psi_drift_detection_flow()
