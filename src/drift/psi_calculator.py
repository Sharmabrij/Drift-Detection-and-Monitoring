import numpy as np
import pandas as pd


def calculate_psi(expected: pd.Series, actual: pd.Series, buckets: int = 10) -> float:
    """
    Calculate the Population Stability Index (PSI) between two distributions.

    Args:
        expected (pd.Series): Reference data (e.g., historical).
        actual (pd.Series): Current data.
        buckets (int): Number of quantile buckets to use.

    Returns:
        float: PSI value.
    """
    # Create quantile bins based on expected
    breakpoints = np.percentile(expected, np.linspace(0, 100, buckets + 1))
    breakpoints = np.unique(breakpoints)  # avoid duplicate breakpoints

    if len(breakpoints) - 1 < buckets:
        print("[Warning] Not enough unique breakpoints — reducing bucket count.")

    expected_counts = np.histogram(expected, bins=breakpoints)[0] / len(expected)
    actual_counts = np.histogram(actual, bins=breakpoints)[0] / len(actual)

    # Avoid division by 0 or log(0) by replacing 0s
    expected_counts = np.where(expected_counts == 0, 1e-6, expected_counts)
    actual_counts = np.where(actual_counts == 0, 1e-6, actual_counts)

    psi_values = (expected_counts - actual_counts) * np.log(
        expected_counts / actual_counts
    )
    return np.sum(psi_values)
