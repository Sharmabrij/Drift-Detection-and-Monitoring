import numpy as np
import pandas as pd

def calculate_psi(expected, actual, buckets=10):
    def scale_range(series, min_val, max_val):
        return (series - series.min()) / (series.max() - series.min()) * (max_val - min_val) + min_val

    expected_percents, bin_edges = np.histogram(expected, bins=buckets)
    actual_percents, _ = np.histogram(actual, bins=bin_edges)

    expected_percents = expected_percents / len(expected)
    actual_percents = actual_percents / len(actual)

    psi = np.sum((expected_percents - actual_percents) * np.log((expected_percents + 1e-8) / (actual_percents + 1e-8)))
    return psi
