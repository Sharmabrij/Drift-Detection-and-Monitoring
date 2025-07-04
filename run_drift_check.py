import pandas as pd
from src.drift_detector import calculate_psi

reference = pd.read_csv("data/reference.csv")
current = pd.read_csv("data/current.csv")

psi_score = calculate_psi(reference["value"], current["value"])
print(f"PSI Score: {psi_score:.4f}")

if psi_score > 0.2:
    print(" Drift detected!")
else:
    print(" No significant drift.")
