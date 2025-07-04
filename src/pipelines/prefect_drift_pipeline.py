from prefect import flow, task
import pandas as pd
import json
from evidently import Report
from evidently.presets import DataDriftPreset
import os


@task
def load_data(path):
    return pd.read_csv(path)


@task
def align_columns(ref, curr):
    common = ref.columns.intersection(curr.columns)
    return ref[common], curr[common]


@task
def run_drift_monitor(reference_data, current_data, report_path):
    my_eval = Report(metrics=[DataDriftPreset()])
    my_eval = my_eval.run(reference_data=reference_data, current_data=current_data)

    # Save report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    my_eval.save_html(report_path)

    print(f"📄 Drift report saved to {report_path}")

    # Determine if drift detected
    report_json = my_eval.json()
    report_dict = json.loads(report_json)
    try:
        return (
            report_dict.get("metrics", [])[0]
            .get("result", {})
            .get("dataset_drift", False)
        )
    except Exception:
        return False


@flow(name="ML Drift Monitoring Pipeline")
def drift_monitor_flow():
    reference_path = "data/batch_normal.csv"
    current_path = "data/test_normal.csv"
    report_path = "reports/drift_report.html"

    ref = load_data(reference_path)
    curr = load_data(current_path)
    ref, curr = align_columns(ref, curr)

    drift_detected = run_drift_monitor(ref, curr, report_path)
    if drift_detected:
        print("⚠️  Drift detected!")
    else:
        print("✅ No drift detected.")


if __name__ == "__main__":
    drift_monitor_flow()
