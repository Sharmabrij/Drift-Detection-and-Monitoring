import pandas as pd
import numpy as np
import json
from evidently import Report
from evidently.presets import DataDriftPreset
from slack_sdk.webhook import WebhookClient
import os

# === CONFIG ===
reference_path = "data/batch_normal.csv"
drifted_path = "data/test_normal.csv"
report_path = "reports/drift_report.html"
slack_webhook_url = "https://hooks.slack.com/services/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"  # <-- replace this

# === Step 1: Load and drift data ===
reference_data = pd.read_csv(reference_path)
drifted_data = reference_data.copy()

# Introduce strong drift
drifted_data["feature1"] += 100
drifted_data["feature2"] = np.random.uniform(1000, 2000, size=len(drifted_data))

# Save drifted test data
os.makedirs("data", exist_ok=True)
drifted_data.to_csv(drifted_path, index=False)
print("✅ Drifted test data saved.")

# === Step 2: Run Drift Report ===
my_eval = Report(metrics=[DataDriftPreset()])
my_eval = my_eval.run(reference_data=reference_data, current_data=drifted_data)

# Save HTML report
os.makedirs("reports", exist_ok=True)
my_eval.save_html(report_path)
print(f"📄 Drift report saved to {report_path}")

# === Step 3: Check for drift ===
report_json = my_eval.json()
report_dict = json.loads(report_json)

try:
    drift_detected = (
        report_dict.get("metrics", [])[0].get("result", {}).get("dataset_drift", False)
    )
except (IndexError, AttributeError, KeyError):
    drift_detected = True

# === Step 4: Alert ===
if drift_detected:
    print("🚨 Drift detected!")
    message = f":rotating_light: *Data drift detected!*\n[View Report]({report_path.replace(' ', '%20')})"
    try:
        webhook = WebhookClient(slack_webhook_url)
        response = webhook.send(text=message)
        print(
            "📢 Slack alert sent."
            if response.status_code == 200
            else f"❌ Failed: {response.status_code}"
        )
    except Exception as e:
        print(f"⚠️ Slack Error: {e}")
else:
    print("✅ No drift detected.")
