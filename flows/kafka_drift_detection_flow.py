from prefect import flow, task
import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime
from prometheus_client import Gauge, Counter, start_http_server

# Import Kafka components
from src.kafka import DriftDataProducer, DriftDataConsumer
from src.kafka.config import get_kafka_config, get_drift_config, get_metrics_config
from src.detection.psi import calculate_psi, get_drift_status
from src.utils.logger import log_psi_result

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
kafka_flow_runs = Counter('kafka_drift_flow_runs_total', 'Total Kafka drift detection flow runs')
kafka_flow_duration = Gauge('kafka_drift_flow_duration_seconds', 'Duration of Kafka drift detection flow')
kafka_messages_processed = Counter('kafka_messages_processed_total', 'Total messages processed in flow')

@task
def setup_kafka_infrastructure():
    """Setup Kafka producer and consumer"""
    config = get_kafka_config()
    drift_config = get_drift_config()
    
    producer = DriftDataProducer(
        bootstrap_servers=config['bootstrap_servers'],
        topic=config['topic']
    )
    
    consumer = DriftDataConsumer(
        bootstrap_servers=config['bootstrap_servers'],
        topic=config['topic'],
        group_id=config['group_id'],
        window_size=drift_config['window_size'],
        check_interval=drift_config['check_interval']
    )
    
    return producer, consumer

@task
def generate_and_send_test_data(producer: DriftDataProducer, n_samples: int = 1000):
    """Generate and send test data to Kafka"""
    logger.info(f"📊 Generating and sending {n_samples} test data points...")
    
    # Send normal data
    normal_sent, normal_total = producer.generate_and_send_synthetic_data(
        n_samples=n_samples//2, 
        drift=False
    )
    
    # Send drifted data
    drifted_sent, drifted_total = producer.generate_and_send_synthetic_data(
        n_samples=n_samples//2, 
        drift=True
    )
    
    total_sent = normal_sent + drifted_sent
    total_attempted = normal_total + drifted_total
    
    logger.info(f"📦 Sent {total_sent}/{total_attempted} messages to Kafka")
    kafka_messages_processed.inc(total_sent)
    
    return total_sent, total_attempted

@task
def run_real_time_drift_detection(consumer: DriftDataConsumer, duration_seconds: int = 300):
    """Run real-time drift detection for specified duration"""
    logger.info(f"🚀 Starting real-time drift detection for {duration_seconds} seconds...")
    
    start_time = time.time()
    consumer.start_background_consuming()
    
    try:
        # Monitor for specified duration
        while time.time() - start_time < duration_seconds:
            status = consumer.get_status()
            logger.info(f"📊 Consumer Status: {status}")
            time.sleep(10)  # Check status every 10 seconds
            
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
    finally:
        consumer.stop_consuming()
    
    end_time = time.time()
    duration = end_time - start_time
    kafka_flow_duration.set(duration)
    
    logger.info(f"⏱️ Real-time drift detection completed in {duration:.2f} seconds")
    return duration

@task
def cleanup_kafka_connections(producer: DriftDataProducer, consumer: DriftDataConsumer):
    """Cleanup Kafka connections"""
    logger.info("🧹 Cleaning up Kafka connections...")
    
    try:
        producer.close()
        consumer.stop_consuming()
        logger.info("✅ Kafka connections cleaned up successfully")
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")

@flow(name="Kafka Real-Time Drift Detection")
def kafka_drift_detection_flow(
    test_data_samples: int = 1000,
    detection_duration: int = 300,
    enable_prometheus: bool = True
):
    """
    Main flow for Kafka-based real-time drift detection
    
    Args:
        test_data_samples: Number of test data samples to generate and send
        detection_duration: Duration to run drift detection (seconds)
        enable_prometheus: Whether to start Prometheus metrics server
    """
    kafka_flow_runs.inc()
    start_time = time.time()
    
    logger.info("🚀 Starting Kafka-based drift detection flow...")
    
    # Start Prometheus metrics server if enabled
    if enable_prometheus:
        metrics_config = get_metrics_config()
        start_http_server(metrics_config['port'], addr=metrics_config['host'])
        logger.info(f"📡 Prometheus metrics server started on {metrics_config['host']}:{metrics_config['port']}")
    
    try:
        # Setup Kafka infrastructure
        producer, consumer = setup_kafka_infrastructure()
        
        # Generate and send test data
        sent_count, total_count = generate_and_send_test_data(producer, test_data_samples)
        
        # Run real-time drift detection
        detection_duration_actual = run_real_time_drift_detection(consumer, detection_duration)
        
        # Get final status
        final_status = consumer.get_status()
        logger.info(f"📊 Final Consumer Status: {final_status}")
        
        # Cleanup
        cleanup_kafka_connections(producer, consumer)
        
        total_duration = time.time() - start_time
        logger.info(f"✅ Kafka drift detection flow completed in {total_duration:.2f} seconds")
        
        return {
            'sent_messages': sent_count,
            'total_attempted': total_count,
            'detection_duration': detection_duration_actual,
            'total_duration': total_duration,
            'final_status': final_status
        }
        
    except Exception as e:
        logger.error(f"❌ Error in Kafka drift detection flow: {e}")
        raise

@flow(name="Kafka Drift Detection Demo")
def kafka_drift_demo_flow():
    """Demo flow for Kafka drift detection with shorter duration"""
    logger.info("🎯 Running Kafka drift detection demo...")
    
    return kafka_drift_detection_flow(
        test_data_samples=500,
        detection_duration=60,  # 1 minute demo
        enable_prometheus=True
    )

if __name__ == "__main__":
    # Run the demo flow
    result = kafka_drift_demo_flow()
    print(f"🎉 Demo completed: {result}") 