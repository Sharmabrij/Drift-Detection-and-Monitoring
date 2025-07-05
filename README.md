# Drift Monitoring System

A production-grade **PSI (Population Stability Index) drift monitoring** system using **Prefect**, **Streamlit**, and **Slack alerts**. This project continuously evaluates data drift in ML pipelines and notifies stakeholders when significant deviations occur.

---

## 📊 Overview Diagram

```mermaid
graph TD
    A[Reference Data (Parquet)] -->|compared to| B[New Production Data]
    B --> C[Calculate PSI (Prefect Flow)]
    C --> D{PSI Thresholds}
    D -->|< 0.1| E[No Drift]
    D -->|0.1 - 0.25| F[Possible Drift]
    D -->|> 0.25| G[Likely Drift]
    E & F & G --> H[Log to CSV]
    G --> I[Send Slack Alert]
    H --> J[Streamlit Dashboard]
```

---

## 🏃‍️ Features

* PSI drift detection with customizable thresholds
* Prefect for orchestration
* Slack webhook alerts for Likely Drift
* Logs PSI scores to CSV
* Streamlit dashboard to visualize drift over time
* CI/CD with Black, Ruff, Pytest, and Codecov

---

## 👁️ Streamlit Dashboard

![](assets/dashboard-example.png) <!-- Replace with actual image path -->

**Live Features:**

* PSI score chart with threshold lines
* Summary panel with latest status
* Auto-refresh every 60s
* Trigger manual check from UI

---

## ⚙️ Technologies Used

| Tool         | Purpose                         |
| ------------ | ------------------------------- |
| Python       | Core programming language       |
| Prefect      | Workflow orchestration          |
| Streamlit    | Monitoring dashboard            |
| Plotly       | Time-series drift visualization |
| Slack API    | Alerting mechanism              |
| Pytest       | Testing framework               |
| Ruff & Black | Linting + formatting            |

---

## 🎓 How PSI is Calculated

```python
def calculate_psi(ref_data: np.ndarray, prod_data: np.ndarray, buckets: int = 10) -> float:
    ...
```

* PSI is computed for one numerical column
* Uses equal-sized quantile buckets
* Log and compare distributions

---

## 📥 Installation

```bash
git clone https://github.com/yourusername/drift-monitoring.git
cd drift-monitoring
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 🚀 Run the Flow

```bash
prefect deployment run psi-drift-check/manual
```

Or from dashboard:

```bash
streamlit run streamlit_app.py
```

---

## 📡 Slack Integration

* Setup incoming webhook in Slack
* Add `SLACK_WEBHOOK_URL` to `.env`

```python
send_slack_alert("PSI Drift Detected!", webhook_url=os.getenv("SLACK_WEBHOOK_URL"))
```

---

## 📅 CI/CD Pipeline

### `.github/workflows/ci-cd.yml`

```yaml
steps:
  - run: black . --check
  - run: ruff check .
  - run: pytest --cov=. --cov-report=xml
  - uses: codecov/codecov-action@v4
```

---



