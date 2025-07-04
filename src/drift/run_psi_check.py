import pandas as pd
from psi_calculator import calculate_psi

# Load datasets
reference_df = pd.read_csv("data/reference.csv")
current_df = pd.read_csv("data/current.csv")

# Compare PSI
psi_score = calculate_psi(reference_df["value"], current_df["value"])
print(f"PSI Score: {psi_score:.4f}")

if psi_score < 0.1:
    print("No significant drift.")
elif psi_score < 0.25:
    print("Moderate drift detected.")
else:
    print("Significant drift detected!")
