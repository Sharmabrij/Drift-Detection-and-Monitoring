import numpy as np
import pandas as pd


def simulate_data(seed=42):
    np.random.seed(seed)

    # Reference: Normal distribution
    reference = pd.DataFrame(
        {
            "timestamp": pd.date_range(start="2023-01-01", periods=100, freq="D"),
            "value": np.random.normal(loc=50, scale=5, size=100),
        }
    )

    # Current: Drifted distribution (mean shift)
    current = pd.DataFrame(
        {
            "timestamp": pd.date_range(start="2023-05-01", periods=100, freq="D"),
            "value": np.random.normal(loc=60, scale=5, size=100),
        }
    )

    reference.to_csv("data/reference.csv", index=False)
    current.to_csv("data/current.csv", index=False)


if __name__ == "__main__":
    simulate_data()
