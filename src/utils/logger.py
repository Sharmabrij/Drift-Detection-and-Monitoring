import pandas as pd
import os
from datetime import datetime
from src.detection.psi import get_drift_status

LOG_PATH = "logs/psi_drift_log.csv"

def log_psi_result(psi):
    status = get_drift_status(psi)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_row = pd.DataFrame([{
        "timestamp": now,
        "psi_score": round(psi, 4),
        "drift_status": status
    }])

    if not os.path.exists("logs"):
        os.makedirs("logs")

    if not os.path.exists(LOG_PATH):
        new_row.to_csv(LOG_PATH, index=False)
    else:
        new_row.to_csv(LOG_PATH, mode='a', header=False, index=False)

    print(f"Logged: {now} | PSI: {round(psi, 4)} | Status: {status}")
