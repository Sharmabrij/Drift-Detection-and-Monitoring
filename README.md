#  ML Pipeline with Kafka Integration & Grafana Monitoring

A comprehensive **Machine Learning Pipeline** with real-time **drift detection**, **Kafka streaming**, **Grafana monitoring**, and **Prefect orchestration**. This project demonstrates a production-ready ML system with automated model training, deployment, monitoring, and alerting.

##  Features

### **Core ML Pipeline**
- **Automated Model Training** with MLflow tracking
- **Real-time Drift Detection** using PSI (Population Stability Index)
- **Model Registry** with versioning and deployment tracking
- **Automated Retraining** based on drift thresholds

### **Kafka Integration**
- **Real-time Data Streaming** with Apache Kafka
- **Producer/Consumer Architecture** for scalable data processing
- **Message Queuing** for reliable data delivery
- **Topic Management** for different data types

### **Monitoring & Observability**
- **Grafana Dashboards** for real-time visualization
- **Prometheus Metrics** collection and storage
- **AlertManager** for automated alerting
- **Comprehensive Metrics** for ML pipeline health

### **Orchestration & Workflows**
- **Prefect Flows** for pipeline orchestration
- **Scheduled Deployments** with cron and interval triggers
- **Work Queues** for different pipeline types
- **Environment Management** (dev/staging/prod)

### **Interactive Interfaces**
- **Streamlit Dashboard** for pipeline control
- **MLflow UI** for experiment tracking
- **Kafka UI** for message monitoring
- **Grafana UI** for metrics visualization

## 📊 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   ML Pipeline   │    │   Monitoring    │
│                 │    │                 │    │                 │
│ • CSV Files     │───▶│ • Prefect Flows │───▶│ • Grafana       │
│ • APIs          │    │ • MLflow        │    │ • Prometheus    │
│ • Databases     │    │ • Model Registry│    │ • AlertManager  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Kafka Stream  │
                       │                 │
                       │ • Producers     │
                       │ • Consumers     │
                       │ • Topics        │
                       └─────────────────┘
```

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **ML Pipeline** | Prefect + MLflow | Orchestration & Experiment Tracking |
| **Streaming** | Apache Kafka | Real-time Data Processing |
| **Monitoring** | Grafana + Prometheus | Metrics & Visualization |
| **Alerting** | AlertManager | Automated Notifications |
| **Dashboard** | Streamlit | Interactive Pipeline Control |
| **Model Registry** | Custom + MLflow | Model Versioning |
| **Containerization** | Docker + Docker Compose | Infrastructure |

## 📦 Installation

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Git

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/drift-monitoring.git
cd drift-monitoring
```

2. **Start the complete infrastructure**
```bash
docker-compose -f docker-compose.grafana.yml up -d
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Access the services**
- **Streamlit Dashboard**: http://localhost:8501
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Kafka UI**: http://localhost:8080
- **MLflow**: http://localhost:5000
- **Prefect**: http://localhost:4200

## 🎯 Usage

### **1. Run Complete ML Pipeline**

```python
from src.pipelines.kafka_ml_pipeline import complete_ml_pipeline_flow

# Run the complete pipeline
result = complete_ml_pipeline_flow(
    data_path="data/train.csv",
    model_name="production_model",
    predictions_count=1000,
    drift_monitoring_duration=10
)
```

### **2. Start Real-time Drift Monitoring**

```python
from src.kafka import DriftDataConsumer

# Initialize consumer
consumer = DriftDataConsumer(
    bootstrap_servers="localhost:9092",
    topic="drift-data",
    group_id="drift-monitor"
)

# Start monitoring
consumer.start_background_consuming()
```

### **3. Use Model Registry**

```python
from src.ml.model_registry import create_model_registry

# Register a model
registry = create_model_registry()
metadata = registry.register_model(
    model=trained_model,
    model_name="my_model",
    accuracy=0.95,
    features=["feature1", "feature2"]
)

# Deploy model
registry.deploy_model("my_model", "1.0.0", "production")
```

### **4. Deploy Prefect Flows**

```bash
# Deploy all flows
python src/pipelines/prefect_deployments.py --action deploy

# Serve flows for development
python src/pipelines/prefect_deployments.py --action serve
```

## 📈 Monitoring & Alerts

### **Grafana Dashboards**

The project includes comprehensive Grafana dashboards:

- **Pipeline Overview**: Key metrics at a glance
- **Real-time PSI Score**: Drift detection visualization
- **Kafka Message Rates**: Throughput monitoring
- **Model Performance**: Accuracy and latency tracking
- **System Resources**: Infrastructure monitoring

### **Alert Rules**

Automated alerts for:

- **High Drift Detected** (PSI > 0.25)
- **Model Performance Degraded** (Accuracy < 0.8)
- **Kafka Producer/Consumer Down**
- **Pipeline Failures**
- **System Resource Issues**

### **Alert Channels**

- **Slack**: Team-specific channels
- **Email**: ML team notifications
- **Webhook**: Custom integrations

## 🔧 Configuration

### **Environment Variables**

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=drift-data
KAFKA_GROUP_ID=drift-monitor-group

# MLflow Configuration
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
MLFLOW_EXPERIMENT_NAME=drift_monitoring

# Pipeline Configuration
DRIFT_WINDOW_SIZE=1000
DRIFT_CHECK_INTERVAL=100
RETRAIN_THRESHOLD=0.15
```

### **Docker Services**

| Service | Port | Purpose |
|---------|------|---------|
| **Kafka** | 9092 | Message streaming |
| **Zookeeper** | 2181 | Kafka coordination |
| **Grafana** | 3000 | Monitoring dashboard |
| **Prometheus** | 9090 | Metrics collection |
| **AlertManager** | 9093 | Alert routing |
| **MLflow** | 5000 | Experiment tracking |
| **Prefect** | 4200 | Pipeline orchestration |
| **Streamlit** | 8501 | Interactive dashboard |
| **Kafka UI** | 8080 | Kafka management |

## 📁 Project Structure

```
drift-monitoring/
├── 📊 grafana/                    # Grafana dashboards & config
│   ├── dashboards/
│   └── provisioning/
├── 🔄 flows/                      # Prefect flows
│   ├── kafka_drift_detection_flow.py
│   └── psi_drift_detection_flow.py
├── 🤖 src/                        # Source code
│   ├── kafka/                     # Kafka integration
│   ├── ml/                        # Model registry
│   ├── monitoring/                # Metrics collection
│   ├── pipelines/                 # ML pipelines
│   └── utils/                     # Utilities
├── 🧪 tests/                      # Test files
├── 📋 reports/                    # Generated reports
├── 📦 data/                       # Data files
├── 🐳 docker-compose.grafana.yml  # Complete infrastructure
├── 📊 prometheus.yml              # Prometheus config
├── 🔔 alertmanager.yml            # AlertManager config
├── 📊 alerts.yml                  # Alert rules
└── 📱 streamlit_ml_pipeline_app.py # Main dashboard
```

## 🚀 Deployment

### **Production Deployment**

1. **Update Configuration**
```bash
# Edit environment variables
cp .env.example .env
# Update with production values
```

2. **Deploy Infrastructure**
```bash
docker-compose -f docker-compose.grafana.yml up -d
```

3. **Deploy Prefect Flows**
```bash
python src/pipelines/prefect_deployments.py --action deploy
```

4. **Start Monitoring**
```bash
python src/monitoring/grafana_metrics.py
```

### **Scaling**

- **Kafka**: Add more brokers for higher throughput
- **Prometheus**: Configure remote storage for long-term metrics
- **Grafana**: Use external database for dashboard persistence
- **Prefect**: Deploy with external database and Redis

## 🧪 Testing

### **Run Tests**
```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_kafka_integration.py

# Run with coverage
pytest --cov=src
```

### **Test Kafka Integration**
```bash
python tests/test_kafka_integration.py
```

## 📊 Metrics & Monitoring

### **Key Metrics Tracked**

- **Drift Detection**: PSI scores, feature drift
- **Model Performance**: Accuracy, confidence, latency
- **Pipeline Health**: Flow execution, stage duration
- **System Resources**: CPU, memory, disk usage
- **Kafka Metrics**: Message rates, latency, errors

### **Custom Metrics**

```python
from src.monitoring.grafana_metrics import record_metric

# Record drift detection
record_metric("drift", psi_score=0.15, feature="feature_1")

# Record model performance
record_metric("model", accuracy=0.95, latency=0.1)
```

## 🔒 Security

### **Best Practices**

- **Environment Variables**: Store secrets in `.env` files
- **Network Security**: Use internal Docker networks
- **Authentication**: Configure Grafana and MLflow auth
- **Data Encryption**: Enable TLS for Kafka
- **Access Control**: Implement RBAC for Prefect

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Submit a pull request**

### **Development Setup**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
python src/pipelines/prefect_deployments.py --action serve
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Apache Kafka** for streaming infrastructure
- **Grafana** for monitoring and visualization
- **Prefect** for workflow orchestration
- **MLflow** for experiment tracking
- **Streamlit** for interactive dashboards


