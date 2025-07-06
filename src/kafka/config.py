"""
Kafka configuration for drift monitoring
"""

import os
from typing import Dict, Any

# Default Kafka configuration
DEFAULT_KAFKA_CONFIG = {
    'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    'topic': os.getenv('KAFKA_TOPIC', 'drift-data'),
    'group_id': os.getenv('KAFKA_GROUP_ID', 'drift-monitor-group'),
    'producer_config': {
        'acks': 'all',
        'retries': 3,
        'batch_size': 16384,
        'linger_ms': 10,
        'buffer_memory': 33554432,
    },
    'consumer_config': {
        'auto_offset_reset': 'earliest',
        'enable_auto_commit': True,
        'auto_commit_interval_ms': 1000,
        'session_timeout_ms': 30000,
        'heartbeat_interval_ms': 3000,
    }
}

# Drift detection configuration
DRIFT_CONFIG = {
    'window_size': int(os.getenv('DRIFT_WINDOW_SIZE', '1000')),
    'check_interval': int(os.getenv('DRIFT_CHECK_INTERVAL', '100')),
    'min_samples': int(os.getenv('DRIFT_MIN_SAMPLES', '100')),
    'psi_thresholds': {
        'no_drift': float(os.getenv('PSI_NO_DRIFT_THRESHOLD', '0.1')),
        'possible_drift': float(os.getenv('PSI_POSSIBLE_DRIFT_THRESHOLD', '0.25')),
    }
}

# Prometheus metrics configuration
METRICS_CONFIG = {
    'port': int(os.getenv('PROMETHEUS_PORT', '8000')),
    'host': os.getenv('PROMETHEUS_HOST', '0.0.0.0'),
}

def get_kafka_config() -> Dict[str, Any]:
    """Get Kafka configuration with environment variable overrides"""
    config = DEFAULT_KAFKA_CONFIG.copy()
    
    # Override with environment variables if present
    if os.getenv('KAFKA_BOOTSTRAP_SERVERS'):
        config['bootstrap_servers'] = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
    if os.getenv('KAFKA_TOPIC'):
        config['topic'] = os.getenv('KAFKA_TOPIC')
    if os.getenv('KAFKA_GROUP_ID'):
        config['group_id'] = os.getenv('KAFKA_GROUP_ID')
    
    return config

def get_drift_config() -> Dict[str, Any]:
    """Get drift detection configuration"""
    return DRIFT_CONFIG.copy()

def get_metrics_config() -> Dict[str, Any]:
    """Get Prometheus metrics configuration"""
    return METRICS_CONFIG.copy() 