import pandas as pd
import numpy as np

# Load reference dataset
reference_path = "data/batch_normal.csv"
output_path = "data/test_normal.csv"

df = pd.read_csv(reference_path)

# Introduce artificial drift to some columns
df["feature1"] = df["feature1"] + 50  # strong shift
df["feature2"] = np.random.normal(1000, 10, size=len(df))  # completely new distribution

# Save drifted dataset
df.to_csv(output_path, index=False)
print("✅ Drifted test data saved.")

