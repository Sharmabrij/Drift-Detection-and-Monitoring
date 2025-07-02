import os
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from evidently import DataDefinition
from evidently import Report
from evidently.presets import DataDriftPreset, DataSummaryPreset

# ---------------------------------------
# Generate synthetic classification data
# ---------------------------------------

def generate_data(n_samples=1000, drift=False):
    if drift:
        X, y = make_classification(
            n_samples=n_samples,
            n_features=5,
            n_informative=3,
            n_redundant=1,
            random_state=42
        )
        X += np.random.normal(0.5, 0.5, X.shape)  # Induce drift
    else:
        X, y = make_classification(
            n_samples=n_samples,
            n_features=5,
            n_informative=3,
            n_redundant=1,
            random_state=42
        )
    
    df = pd.DataFrame(X, columns=[f"feature{i}" for i in range(1, 6)])
    df["target"] = y
    return df

# ---------------------------------------
# Save datasets
# ---------------------------------------

def save_datasets():
    os.makedirs("data", exist_ok=True)
    train = generate_data(n_samples=1000)
    test_normal = generate_data(n_samples=500)
    test_drifted = generate_data(n_samples=500, drift=True)

    train.to_csv("data/train.csv", index=False)
    test_normal.to_csv("data/test_normal.csv", index=False)
    test_drifted.to_csv("data/test_drifted.csv", index=False)

    print(" Datasets saved to /data")

# ---------------------------------------
# Generate and save drift report
# ---------------------------------------

def save_drift_report():
    os.makedirs("reports", exist_ok=True)

    reference = pd.read_csv("data/train.csv")
    current = pd.read_csv("data/test_drifted.csv")

    # Define the data schema
    data_def = DataDefinition(
        numerical_columns=[col for col in reference.columns if col.startswith("feature")],
        
    )

    report = Report(metrics=[DataDriftPreset()])
    my_eval = report.run(reference_data=reference, current_data=current)
    my_report = "reports/drift_report.html"
    my_eval.save_html(my_report)

    print("Drift report saved to /reports")

# ---------------------------------------
# Main
# ---------------------------------------

if __name__ == "__main__":
    save_datasets()
    save_drift_report()
