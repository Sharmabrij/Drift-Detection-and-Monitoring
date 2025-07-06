# 📊 Drift Monitoring with Kafka Integration

A comprehensive machine learning drift monitoring system that uses Apache Kafka for real-time data streaming and drift detection. This project combines the Population Stability Index (PSI) with Kafka to provide real-time monitoring of data drift in ML models.

## 🚀 Features

- **Real-time Drift Detection**: Stream data through Kafka and detect drift in real-time
- **PSI Calculation**: Multiple implementations of Population Stability Index
- **Kafka Integration**: Producer and consumer for streaming data
- **Streamlit Dashboard**: Interactive web interface for monitoring
- **Prefect Workflows**: Automated drift detection pipelines
- **Prometheus Metrics**: Comprehensive monitoring and alerting
- **Slack Notifications**: Real-time alerts when drift is detected
- **Docker Support**: Complete containerized setup with Kafka, Zookeeper, and monitoring tools

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│   Kafka Topic   │───▶│  Drift Consumer │
│   (Producers)   │    │   (drift-data)  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Kafka UI      │    │  PSI Calculator │
                       │   (Port 8080)   │    │                 │
                       └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Prometheus    │◀───│  Streamlit App  │
                       │   (Port 9090)   │    │   (Port 8501)   │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    Grafana      │
                       │   (Port 3000)   │
                       └─────────────────┘
```

## 📦 Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Apache Kafka (provided via Docker)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd drift-monitoring
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Kafka Infrastructure
```bash
docker-compose up -d
```

This will start:
- **Zookeeper** (Port 2181)
- **Kafka** (Port 9092)
- **Kafka UI** (Port 8080) - Web interface for Kafka management
- **Prometheus** (Port 9090) - Metrics collection
- **Grafana** (Port 3000) - Metrics visualization

### 4. Verify Kafka Setup
```bash
# Check if Kafka is running
docker-compose ps

# Access Kafka UI
open http://localhost:8080
```

## 🚀 Quick Start

### Option 1: Streamlit Dashboard (Recommended)
```bash
streamlit run streamlit_kafka_app.py
```
Access the dashboard at: http://localhost:8501

### Option 2: Command Line
```bash
# Start Kafka consumer for drift detection
python src/kafka/consumer.py

# In another terminal, send test data
python src/kafka/producer.py
```

### Option 3: Prefect Flow
```bash
# Run the Kafka drift detection flow
python flows/kafka_drift_detection_flow.py
```

## 📊 Usage

### 1. Kafka Producer
```python
from src.kafka import DriftDataProducer

# Initialize producer
producer = DriftDataProducer(
    bootstrap_servers='localhost:9092',
    topic='drift-data'
)

# Send data
data = {
    'feature1': 0.5,
    'feature2': 1.2,
    'feature3': -0.3,
    'feature4': 0.8,
    'feature5': 0.1,
    'target': 1
}
producer.send_data_point(data)
```

### 2. Kafka Consumer
```python
from src.kafka import DriftDataConsumer

# Initialize consumer
consumer = DriftDataConsumer(
    bootstrap_servers='localhost:9092',
    topic='drift-data',
    window_size=1000,
    check_interval=100
)

# Start consuming and detecting drift
consumer.start_consuming()
```

### 3. Real-time Drift Detection
The system automatically:
- Consumes data from Kafka topics
- Maintains a sliding window of recent data
- Calculates PSI scores against reference data
- Detects drift based on configurable thresholds
- Logs results and sends alerts

## ⚙️ Configuration

### Environment Variables
```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=drift-data
KAFKA_GROUP_ID=drift-monitor-group

# Drift Detection
DRIFT_WINDOW_SIZE=1000
DRIFT_CHECK_INTERVAL=100
DRIFT_MIN_SAMPLES=100

# PSI Thresholds
PSI_NO_DRIFT_THRESHOLD=0.1
PSI_POSSIBLE_DRIFT_THRESHOLD=0.25

# Prometheus
PROMETHEUS_PORT=8000
PROMETHEUS_HOST=0.0.0.0

# Slack (for alerts)
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

### Configuration Files
- `src/kafka/config.py` - Kafka and drift detection settings
- `prometheus.yml` - Prometheus monitoring configuration
- `docker-compose.yml` - Infrastructure setup

## 📈 Monitoring

### Prometheus Metrics
Access Prometheus at: http://localhost:9090

Key metrics:
- `kafka_messages_consumed_total` - Total messages consumed
- `real_time_psi_score` - Current PSI score
- `drift_detection_events_total` - Drift detection events by status
- `kafka_consumer_lag` - Consumer lag
- `psi_calculation_duration_seconds` - PSI calculation time

### Grafana Dashboards
Access Grafana at: http://localhost:3000 (admin/admin)

### Kafka UI
Access Kafka UI at: http://localhost:8080

## 🔧 Development

### Project Structure
```
drift-monitoring/
├── src/
│   ├── kafka/                 # Kafka integration
│   │   ├── producer.py        # Kafka producer
│   │   ├── consumer.py        # Kafka consumer
│   │   └── config.py          # Configuration
│   ├── detection/             # Drift detection algorithms
│   ├── utils/                 # Utility functions
│   └── pipelines/             # Prefect workflows
├── flows/                     # Prefect flows
├── data/                      # Sample datasets
├── logs/                      # Drift detection logs
├── tests/                     # Unit tests
├── streamlit_app.py           # Original Streamlit app
├── streamlit_kafka_app.py     # Kafka-enabled Streamlit app
├── docker-compose.yml         # Infrastructure setup
└── requirements.txt           # Python dependencies
```

### Running Tests
```bash
pytest tests/
```

### Adding New Features
1. Create feature branch
2. Add tests
3. Update documentation
4. Submit pull request

## 🚨 Alerts

The system provides multiple alerting mechanisms:

1. **Slack Notifications**: Real-time alerts when drift is detected
2. **Prometheus Alerts**: Configurable alerting rules
3. **Log Files**: Detailed logging in `logs/psi_drift_log.csv`
4. **Streamlit Dashboard**: Real-time status updates

## 🔍 Troubleshooting

### Common Issues

1. **Kafka Connection Failed**
   ```bash
   # Check if Kafka is running
   docker-compose ps
   
   # Restart Kafka
   docker-compose restart kafka
   ```

2. **Consumer Not Receiving Messages**
   ```bash
   # Check topic exists
   docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
   
   # Check consumer group
   docker exec -it kafka kafka-consumer-groups --bootstrap-server localhost:9092 --list
   ```

3. **Prometheus Metrics Not Available**
   ```bash
   # Check if metrics endpoint is accessible
   curl http://localhost:8000/metrics
   ```

### Logs
- Application logs: Check console output
- Kafka logs: `docker-compose logs kafka`
- Zookeeper logs: `docker-compose logs zookeeper`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Apache Kafka for streaming infrastructure
- Streamlit for the web interface
- Prefect for workflow orchestration
- Prometheus for metrics collection
- Evidently for drift detection algorithms
