import numpy as np
import pandas as pd

def calculate_psi(expected, actual, buckets=10):
    def scale_range(data, n_bins):
        return pd.qcut(data.rank(method="first"), q=n_bins, labels=False)

    expected, actual = np.array(expected), np.array(actual)
    expected_bins = scale_range(pd.Series(expected), buckets)
    actual_bins = scale_range(pd.Series(actual), buckets)

    psi_total = 0
    for i in range(buckets):
        expected_pct = (expected_bins == i).mean()
        actual_pct = (actual_bins == i).mean()
        
        if expected_pct == 0:
            expected_pct = 0.0001
        if actual_pct == 0:
            actual_pct = 0.0001
            
        psi = (expected_pct - actual_pct) * np.log(expected_pct / actual_pct)
        psi_total += psi

    return psi_total
