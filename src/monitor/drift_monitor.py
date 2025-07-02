import pandas as pd
import json
from evidently import Report
from evidently.presets import DataDriftPreset
from slack_sdk.webhook import WebhookClient
import os

# === CONFIGURATION ===
reference_csv_path = "c:/Users/Administrator/Desktop/drift-monitoring/data/batch_normal.csv"
current_csv_path = "c:/Users/Administrator/Desktop/drift-monitoring/data/test_normal.csv"
report_path = "c:/Users/Administrator/Desktop/drift-monitoring/reports/drift_report.html"
slack_webhook_url = "https://hooks.slack.com/services/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"  # <-- Replace with your actual webhook URL

# === LOAD DATA ===
reference_data = pd.read_csv(reference_csv_path)
current_data = pd.read_csv(current_csv_path)

# === ALIGN COLUMNS ===
common_columns = reference_data.columns.intersection(current_data.columns)
reference_data = reference_data[common_columns]
current_data = current_data[common_columns]


# === RUN DRIFT REPORT ===
my_eval = Report(metrics=[DataDriftPreset()])
my_eval= my_eval.run(reference_data=reference_data, current_data=current_data)

# === Save HTML report ===

report_path = "./reports/drift_report.html"
my_eval.save_html(report_path)

print(f" Drift report saved to {report_path}")

# === Extract drift result from JSON ===
report_json = my_eval.json()
report_dict = json.loads(report_json)

# Access first metric (DataDriftPreset)
try:
    drift_detected = report_dict.get("metrics", [])[0].get("result", {}).get("dataset_drift", False)
except (IndexError, AttributeError, KeyError):
    drift_detected = False

# === SEND SLACK ALERT IF DRIFT DETECTED ===
if drift_detected:
    print(" Drift detected — sending Slack alert...")

    message = f":rotating_light: *Data drift detected!*\n [View Report]({report_path.replace(' ', '%20')})"

    try:
        webhook = WebhookClient(slack_webhook_url)
        response = webhook.send(text=message)
        if response.status_code == 200:
            print(" Slack alert sent.")
        else:
            print(f" Failed to send Slack alert: {response.status_code}")
    except Exception as e:
        print(f"Error sending Slack message: {e}")
else:
    print(" No drift detected.")
