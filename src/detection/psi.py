import numpy as np

def calculate_psi(ref, prod, bins=10):
    ref_hist, bin_edges = np.histogram(ref, bins=bins)
    prod_hist, _ = np.histogram(prod, bins=bin_edges)

    ref_perc = ref_hist / len(ref)
    prod_perc = prod_hist / len(prod)

    psi = np.sum((ref_perc - prod_perc) * np.log((ref_perc + 1e-6) / (prod_perc + 1e-6)))
    return psi

def get_drift_status(psi):
    if psi < 0.1:
        return "No Drift"
    elif psi < 0.25:
        return "Possible Drift"
    else:
        return "Likely Drift"
