# ML Pipeline with Kafka Integration - Complete Setup Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Dependencies & Software](#dependencies--software)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [File Structure](#file-structure)
6. [Running the Project](#running-the-project)
7. [Troubleshooting](#troubleshooting)
8. [Useful Links](#useful-links)

---

## System Requirements

### Minimum System Specifications
- **Operating System**: Windows 10/11, macOS 10.15+, or Ubuntu 18.04+
- **RAM**: 8GB (16GB recommended)
- **Storage**: 10GB free space
- **CPU**: 4 cores (8 cores recommended)
- **Network**: Internet connection for downloading dependencies

### Software Requirements
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Python**: Version 3.9+
- **Git**: Version 2.30+

---

## Dependencies & Software

### 1. Docker & Docker Compose
- **Download Link**: https://www.docker.com/products/docker-desktop
- **Purpose**: Containerization and orchestration of all services
- **Installation**: Download Docker Desktop for your OS

### 2. Python 3.9+
- **Download Link**: https://www.python.org/downloads/
- **Purpose**: Main programming language for ML pipeline
- **Installation**: Download and install from python.org

### 3. Git
- **Download Link**: https://git-scm.com/downloads
- **Purpose**: Version control and repository management
- **Installation**: Download for your OS

### 4. Code Editor (Optional but Recommended)
- **VS Code**: https://code.visualstudio.com/
- **PyCharm**: https://www.jetbrains.com/pycharm/
- **Purpose**: Code editing and development

---

## Installation Steps

### Step 1: Install Docker Desktop
```bash
# Download Docker Desktop from https://www.docker.com/products/docker-desktop
# Install and start Docker Desktop
# Verify installation
docker --version
docker-compose --version
```

### Step 2: Install Python
```bash
# Download Python 3.9+ from https://www.python.org/downloads/
# Install with pip and add to PATH
# Verify installation
python --version
pip --version
```

### Step 3: Install Git
```bash
# Download Git from https://git-scm.com/downloads
# Install with default settings
# Verify installation
git --version
```

### Step 4: Clone the Repository
```bash
# Clone the project
git clone https://github.com/yourusername/drift-monitoring.git
cd drift-monitoring

# Verify repository structure
ls -la
```

### Step 5: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Verify activation
which python  # Should show venv path
```

### Step 6: Install Python Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

---

## Configuration

### Environment Variables Setup
Create a `.env` file in the project root:

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

# Grafana Configuration
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin

# Prometheus Configuration
PROMETHEUS_RETENTION_TIME=200h
```

### Docker Configuration
The project uses `docker-compose.grafana.yml` which includes:
- Kafka and Zookeeper
- Grafana and Prometheus
- MLflow and Prefect
- AlertManager and monitoring tools

---

## File Structure

### Root Directory Structure
```
drift-monitoring/
├── 📁 .github/                    # GitHub workflows and CI/CD
├── 📁 config/                     # Configuration files
├── 📁 data/                       # Data files and datasets
├── 📁 flows/                      # Prefect workflow definitions
├── 📁 grafana/                    # Grafana dashboards and provisioning
├── 📁 reports/                    # Generated reports and outputs
├── 📁 src/                        # Source code directory
├── 📁 tests/                      # Test files and test data
├── 📁 venv/                       # Python virtual environment
├── 📄 .gitignore                  # Git ignore rules
├── 📄 .prefectignore              # Prefect ignore rules
├── 📄 alertmanager.yml            # AlertManager configuration
├── 📄 alerts.yml                  # Prometheus alert rules
├── 📄 docker-compose.grafana.yml  # Complete Docker infrastructure
├── 📄 prefect.yaml                # Prefect configuration
├── 📄 prometheus.yml              # Prometheus configuration
├── 📄 README.md                   # Project documentation
├── 📄 requirements.txt            # Python dependencies
├── 📄 run_kafka_demo.py           # Demo script
└── 📄 streamlit_ml_pipeline_app.py # Main Streamlit application
```

### Detailed File Descriptions

#### Configuration Files
- **`alertmanager.yml`**: AlertManager configuration for routing alerts to different channels (Slack, email, webhooks)
- **`alerts.yml`**: Prometheus alert rules defining when to trigger alerts based on metrics
- **`docker-compose.grafana.yml`**: Complete Docker Compose file defining all services (Kafka, Grafana, Prometheus, etc.)
- **`prometheus.yml`**: Prometheus configuration for metrics collection and storage
- **`prefect.yaml`**: Prefect configuration for workflow orchestration

#### Source Code (`src/` directory)
```
src/
├── 📁 app/                        # Application-specific code
├── 📁 detection/                  # Drift detection algorithms
├── 📁 drift/                      # Drift monitoring utilities
├── 📁 kafka/                      # Kafka integration components
│   ├── __init__.py               # Package initialization
│   ├── config.py                 # Kafka configuration management
│   ├── consumer.py               # Kafka consumer implementation
│   └── producer.py               # Kafka producer implementation
├── 📁 ml/                         # Machine learning components
│   └── model_registry.py         # Model registry and versioning
├── 📁 monitoring/                 # Monitoring and metrics
│   └── grafana_metrics.py        # Grafana metrics collection
├── 📁 pipelines/                  # ML pipeline definitions
│   ├── kafka_ml_pipeline.py      # Main ML pipeline with Kafka
│   └── prefect_deployments.py    # Prefect deployment configurations
├── 📁 psi_drift/                  # PSI drift detection
├── 📁 utils/                      # Utility functions
└── 📁 monitor/                    # Monitoring utilities
```

#### Grafana Configuration (`grafana/` directory)
```
grafana/
├── 📁 dashboards/                 # Grafana dashboard definitions
│   └── ml_pipeline_dashboard.json # Main ML pipeline dashboard
└── 📁 provisioning/               # Grafana provisioning
    ├── 📁 dashboards/             # Dashboard provisioning
    │   └── dashboard.yml          # Dashboard configuration
    └── 📁 datasources/            # Data source provisioning
        └── prometheus.yml         # Prometheus data source config
```

#### Flows (`flows/` directory)
```
flows/
├── __init__.py                   # Package initialization
├── kafka_drift_detection_flow.py # Kafka-based drift detection flow
└── psi_drift_detection_flow.py   # PSI-based drift detection flow
```

#### Tests (`tests/` directory)
```
tests/
└── test_kafka_integration.py     # Kafka integration tests
```

---

## Running the Project

### Step 1: Start Infrastructure
```bash
# Start all Docker services
docker-compose -f docker-compose.grafana.yml up -d

# Verify all services are running
docker-compose -f docker-compose.grafana.yml ps

# Check service logs if needed
docker-compose -f docker-compose.grafana.yml logs -f
```

### Step 2: Verify Services
```bash
# Check if all services are accessible
curl http://localhost:3000  # Grafana
curl http://localhost:9090  # Prometheus
curl http://localhost:8080  # Kafka UI
curl http://localhost:5000  # MLflow
curl http://localhost:4200  # Prefect
```

### Step 3: Deploy Prefect Flows
```bash
# Deploy all Prefect flows
python src/pipelines/prefect_deployments.py --action deploy

# Or serve flows for development
python src/pipelines/prefect_deployments.py --action serve
```

### Step 4: Start Streamlit Dashboard
```bash
# Start the main Streamlit application
streamlit run streamlit_ml_pipeline_app.py

# Or run the demo
python run_kafka_demo.py
```

### Step 5: Access Web Interfaces
Open your browser and navigate to:
- **Streamlit Dashboard**: http://localhost:8501
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Kafka UI**: http://localhost:8080
- **MLflow**: http://localhost:5000
- **Prefect**: http://localhost:4200
- **AlertManager**: http://localhost:9093

---

## Service Ports and URLs

| Service | Port | URL | Default Credentials |
|---------|------|-----|-------------------|
| **Streamlit** | 8501 | http://localhost:8501 | None |
| **Grafana** | 3000 | http://localhost:3000 | admin/admin |
| **Prometheus** | 9090 | http://localhost:9090 | None |
| **Kafka** | 9092 | localhost:9092 | None |
| **Kafka UI** | 8080 | http://localhost:8080 | None |
| **MLflow** | 5000 | http://localhost:5000 | None |
| **Prefect** | 4200 | http://localhost:4200 | None |
| **AlertManager** | 9093 | http://localhost:9093 | None |
| **Zookeeper** | 2181 | localhost:2181 | None |
| **Redis** | 6379 | localhost:6379 | None |
| **PostgreSQL** | 5432 | localhost:5432 | admin/admin123 |

---

## Python Dependencies

### Core Dependencies (requirements.txt)
```
# ML and Data Processing
pandas>=1.5.0
numpy>=1.21.0
scikit-learn>=1.1.0
mlflow>=2.0.0

# Kafka Integration
kafka-python>=2.0.0
confluent-kafka>=1.9.0

# Monitoring and Metrics
prometheus-client>=0.14.0
psutil>=5.9.0

# Workflow Orchestration
prefect>=2.0.0

# Web Dashboard
streamlit>=1.25.0
plotly>=5.15.0

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0

# Utilities
python-dotenv>=0.19.0
pyyaml>=6.0
```

### Installation Commands
```bash
# Install all dependencies
pip install -r requirements.txt

# Install specific packages if needed
pip install pandas numpy scikit-learn
pip install kafka-python confluent-kafka
pip install prometheus-client psutil
pip install prefect streamlit plotly
pip install pytest pytest-cov
```

---

## Common Commands

### Docker Commands
```bash
# Start all services
docker-compose -f docker-compose.grafana.yml up -d

# Stop all services
docker-compose -f docker-compose.grafana.yml down

# View logs
docker-compose -f docker-compose.grafana.yml logs -f

# Restart specific service
docker-compose -f docker-compose.grafana.yml restart grafana

# Check service status
docker-compose -f docker-compose.grafana.yml ps
```

### Python Commands
```bash
# Run ML pipeline
python src/pipelines/kafka_ml_pipeline.py

# Run drift detection
python flows/psi_drift_detection_flow.py

# Run tests
pytest tests/

# Start metrics collection
python src/monitoring/grafana_metrics.py
```

### Prefect Commands
```bash
# Deploy flows
python src/pipelines/prefect_deployments.py --action deploy

# Serve flows
python src/pipelines/prefect_deployments.py --action serve

# Start Prefect server
prefect server start

# View Prefect UI
prefect server start --host 0.0.0.0 --port 4200
```

### Streamlit Commands
```bash
# Run main app
streamlit run streamlit_ml_pipeline_app.py

# Run with specific port
streamlit run streamlit_ml_pipeline_app.py --server.port 8501

# Run in development mode
streamlit run streamlit_ml_pipeline_app.py --server.runOnSave true
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Docker Services Not Starting
```bash
# Check Docker is running
docker --version
docker-compose --version

# Check available ports
netstat -an | grep :3000
netstat -an | grep :9090

# Restart Docker Desktop
# Then restart services
docker-compose -f docker-compose.grafana.yml down
docker-compose -f docker-compose.grafana.yml up -d
```

#### 2. Python Dependencies Issues
```bash
# Recreate virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### 3. Kafka Connection Issues
```bash
# Check Kafka is running
docker-compose -f docker-compose.grafana.yml ps kafka

# Check Kafka logs
docker-compose -f docker-compose.grafana.yml logs kafka

# Test Kafka connection
python -c "from kafka import KafkaProducer; p = KafkaProducer(bootstrap_servers=['localhost:9092']); print('Kafka connected')"
```

#### 4. Grafana Dashboard Issues
```bash
# Check Grafana is running
curl http://localhost:3000/api/health

# Check Prometheus data source
curl http://localhost:9090/api/v1/status/targets

# Restart Grafana
docker-compose -f docker-compose.grafana.yml restart grafana
```

#### 5. Prefect Flow Issues
```bash
# Check Prefect server
curl http://localhost:4200/api/health

# Restart Prefect server
docker-compose -f docker-compose.grafana.yml restart prefect-server

# Check flow logs
prefect flow-run logs <flow-run-id>
```

---

## Useful Links

### Official Documentation
- **Docker**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **Python**: https://docs.python.org/
- **Kafka**: https://kafka.apache.org/documentation/
- **Grafana**: https://grafana.com/docs/
- **Prometheus**: https://prometheus.io/docs/
- **Prefect**: https://docs.prefect.io/
- **MLflow**: https://mlflow.org/docs/
- **Streamlit**: https://docs.streamlit.io/

### GitHub Repositories
- **Project Repository**: https://github.com/yourusername/drift-monitoring
- **Docker Images**: https://hub.docker.com/
- **Python Packages**: https://pypi.org/

### Community Resources
- **Stack Overflow**: https://stackoverflow.com/
- **GitHub Issues**: https://github.com/yourusername/drift-monitoring/issues
- **Discord/Slack**: Community channels for each tool

### Monitoring and Debugging
- **Grafana Dashboards**: http://localhost:3000
- **Prometheus Targets**: http://localhost:9090/targets
- **Kafka UI**: http://localhost:8080
- **MLflow UI**: http://localhost:5000
- **Prefect UI**: http://localhost:4200

---

## Support and Maintenance

### Regular Maintenance Tasks
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Clean Docker images
docker system prune -a

# Update Docker Compose
docker-compose -f docker-compose.grafana.yml pull

# Backup data
docker-compose -f docker-compose.grafana.yml exec postgres pg_dump -U admin drift_monitoring > backup.sql
```

### Monitoring Health Checks
```bash
# Check all services health
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:9090/-/healthy   # Prometheus
curl http://localhost:4200/api/health  # Prefect
curl http://localhost:5000/health      # MLflow
```

### Log Management
```bash
# View all logs
docker-compose -f docker-compose.grafana.yml logs

# View specific service logs
docker-compose -f docker-compose.grafana.yml logs grafana
docker-compose -f docker-compose.grafana.yml logs kafka
docker-compose -f docker-compose.grafana.yml logs prometheus
```

---

## Conclusion

This setup guide provides everything needed to run the ML Pipeline with Kafka Integration project. Follow the steps in order, and refer to the troubleshooting section if you encounter any issues. The project is designed to be production-ready with comprehensive monitoring and alerting capabilities.

For additional support, please refer to the project's GitHub repository or create an issue for specific problems. 