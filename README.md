
#  Drift Monitoring System (PSI-Based)

A real-time data drift monitoring tool using **Population Stability Index (PSI)**, powered by **Prefect**, **Slack**, **Streamlit**, and CI/CD integrations.

---

##  Overview

This project monitors feature drift in machine learning systems by comparing **production data** against a **reference dataset** using **PSI**. Alerts are sent via **Slack**, logs are stored in CSV format, and a **Streamlit dashboard** visualizes the drift history.

---

##  Architecture

![Architecture Diagram]![ChatGPT Image Jul 5, 2025, 12_36_35 PM](https://github.com/user-attachments/assets/d5cac1ed-e3ca-44e9-b859-fefa11c5fdda)


**Key Components:**

* **Reference & Production Data**: Ingested via Parquet or CSV/API.
* **Prefect Flow**: Orchestrates PSI calculation, thresholding, logging, and alerting.
* **PSI Thresholds**:

  * `PSI < 0.1`: No Drift
  * `0.1 ≤ PSI ≤ 0.25`: Possible Drift
  * `PSI > 0.25`: Likely Drift
* **Slack Alerts**: Instant notification if drift is detected.
* **Logging**: Drift metrics saved as CSV in `logs/`.
* **Streamlit Dashboard**: Live visualization of PSI scores over time.
* **CI/CD**: GitHub Actions for formatting, linting, testing, and deploying.

---

##  Features

* ✅ PSI Drift Detection
* ✅ Prefect Flow Orchestration
* ✅ Slack Alert Integration
* ✅ Streamlit Dashboard
* ✅ GitHub Actions CI/CD Pipeline
* ✅ Test Coverage with `pytest` & `pytest-cov`

---

## 🧪 Example PSI Status Output

| Timestamp           | PSI Score | Drift Status   |
| ------------------- | --------- | -------------- |
| 2025-07-05 10:01:12 | 0.18      | Possible Drift |
| 2025-07-04 10:01:12 | 0.06      | No Drift       |
| 2025-07-03 10:01:12 | 0.31      | Likely Drift   |

---

## 🛠️ Installation

```bash
git clone https://github.com/your-org/drift-monitoring.git
cd drift-monitoring
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

---

## 📈 Running the Flow

```bash
python flows/psi_drift_detection_flow.py
```

---

## 🧪 Run Tests

```bash
pytest --cov=flows tests/
```

---

## 🧼 Lint & Format

```bash
black src/
ruff check src/ --fix
```

---

## 🌐 Launch Streamlit Dashboard

```bash
streamlit run streamlit_app.py
```

---

## 🔄 CI/CD (GitHub Actions)

`.github/workflows/ci-cd.yml`:

* ✅ Auto-format using `black`
* ✅ Lint with `ruff`
* ✅ Run unit tests
* ✅ Upload coverage
* ✅ (Optional) Deploy to Streamlit Cloud

---

## 📬 Slack Integration

Configure the Slack webhook in `.env`:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
```

