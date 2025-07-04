import pandas as pd
import numpy as np


def load_reference_data():
    np.random.seed(42)
    return pd.DataFrame({"feature": np.random.normal(loc=0, scale=1, size=1000)})


def load_current_data():
    np.random.seed(43)
    return pd.DataFrame({"feature": np.random.normal(loc=1.5, scale=1, size=1000)})
