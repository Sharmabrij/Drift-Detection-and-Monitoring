import json
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from kafka import KafkaConsumer
from collections import deque
from typing import Dict, Any, List, Optional
import logging
from prometheus_client import Gauge, Counter, Histogram
import threading

# Import drift detection functions
from src.detection.psi import calculate_psi, get_drift_status
from src.utils.logger import log_psi_result

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
kafka_messages_consumed = Counter('kafka_messages_consumed_total', 'Total messages consumed from Kafka')
kafka_consumer_lag = Gauge('kafka_consumer_lag', 'Consumer lag for drift data topic')
psi_calculation_duration = Histogram('psi_calculation_duration_seconds', 'Time spent calculating PSI')
real_time_psi_score = Gauge('real_time_psi_score', 'Real-time PSI score from streaming data')
drift_detection_events = Counter('drift_detection_events_total', 'Total drift detection events', ['status'])

class DriftDataConsumer:
    """
    Kafka consumer for real-time drift detection
    """
    
    def __init__(self, 
                 bootstrap_servers: str = 'localhost:9092',
                 topic: str = 'drift-data',
                 group_id: str = 'drift-monitor-group',
                 window_size: int = 1000,
                 check_interval: int = 100):
        """
        Initialize Kafka consumer
        
        Args:
            bootstrap_servers: Kafka broker addresses
            topic: Kafka topic to consume from
            group_id: Consumer group ID
            window_size: Number of data points to keep in sliding window
            check_interval: Check for drift every N messages
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.window_size = window_size
        self.check_interval = check_interval
        
        self.consumer = None
        self.reference_data = None
        self.current_window = deque(maxlen=window_size)
        self.message_count = 0
        self.last_drift_check = datetime.now()
        
        # Threading for background processing
        self.running = False
        self.processing_thread = None
        
        self._connect()
        self._load_reference_data()
    
    def _connect(self):
        """Establish connection to Kafka"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                key_deserializer=lambda x: x.decode('utf-8') if x else None,
                consumer_timeout_ms=1000
            )
            logger.info(f"✅ Connected to Kafka topic: {self.topic}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Kafka: {e}")
            raise
    
    def _load_reference_data(self):
        """Load reference data for drift comparison"""
        try:
            # Load reference data from file
            reference_path = "data/batch_normal.csv"
            self.reference_data = pd.read_csv(reference_path)
            logger.info(f"✅ Loaded reference data: {len(self.reference_data)} samples")
        except Exception as e:
            logger.warning(f"⚠️ Could not load reference data: {e}")
            # Generate synthetic reference data
            self.reference_data = pd.DataFrame(
                np.random.normal(0, 1, (1000, 5)),
                columns=[f'feature{i}' for i in range(1, 6)]
            )
            logger.info("✅ Generated synthetic reference data")
    
    def _process_message(self, message):
        """Process a single Kafka message"""
        try:
            # Extract data from message
            data = message.value
            
            # Convert to DataFrame row
            features = {f'feature{i}': data.get(f'feature{i}', 0) for i in range(1, 6)}
            features['target'] = data.get('target', 0)
            features['timestamp'] = data.get('timestamp', datetime.now().isoformat())
            
            # Add to current window
            self.current_window.append(features)
            self.message_count += 1
            kafka_messages_consumed.inc()
            
            # Check for drift periodically
            if self.message_count % self.check_interval == 0:
                self._check_drift()
                
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
    
    def _check_drift(self):
        """Check for drift using current window data"""
        if len(self.current_window) < 100:  # Need minimum data points
            return
        
        try:
            # Convert window to DataFrame
            current_df = pd.DataFrame(list(self.current_window))
            
            # Extract feature columns
            feature_cols = [f'feature{i}' for i in range(1, 6)]
            ref_features = self.reference_data[feature_cols]
            curr_features = current_df[feature_cols]
            
            # Calculate PSI for each feature
            psi_scores = []
            for col in feature_cols:
                with psi_calculation_duration.time():
                    psi = calculate_psi(ref_features[col], curr_features[col])
                    psi_scores.append(psi)
            
            # Use average PSI score
            avg_psi = np.mean(psi_scores)
            status = get_drift_status(avg_psi)
            
            # Update metrics
            real_time_psi_score.set(avg_psi)
            drift_detection_events.labels(status=status).inc()
            
            # Log result
            log_psi_result(avg_psi)
            
            # Log detailed results
            logger.info(f"📊 Drift Check - PSI: {avg_psi:.4f}, Status: {status}")
            logger.info(f"📊 Feature PSI scores: {dict(zip(feature_cols, [f'{p:.4f}' for p in psi_scores]))}")
            
            # Alert if drift detected
            if status != "No Drift":
                logger.warning(f"⚠️ DRIFT DETECTED! PSI: {avg_psi:.4f}, Status: {status}")
            
            self.last_drift_check = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Error checking drift: {e}")
    
    def start_consuming(self):
        """Start consuming messages from Kafka"""
        self.running = True
        logger.info(f"🚀 Starting to consume from topic: {self.topic}")
        
        try:
            for message in self.consumer:
                if not self.running:
                    break
                
                self._process_message(message)
                
                # Update consumer lag metric
                partitions = self.consumer.assignment()
                if partitions:
                    for partition in partitions:
                        end_offset = self.consumer.end_offsets([partition])[partition]
                        current_offset = self.consumer.position([partition])[partition]
                        lag = end_offset - current_offset
                        kafka_consumer_lag.set(lag)
                
        except Exception as e:
            logger.error(f"❌ Error in consumer loop: {e}")
        finally:
            self.stop_consuming()
    
    def start_background_consuming(self):
        """Start consuming in a background thread"""
        if self.processing_thread and self.processing_thread.is_alive():
            logger.warning("⚠️ Consumer already running")
            return
        
        self.processing_thread = threading.Thread(target=self.start_consuming)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        logger.info("🚀 Started background consumer thread")
    
    def stop_consuming(self):
        """Stop consuming messages"""
        self.running = False
        if self.consumer:
            self.consumer.close()
        logger.info("🛑 Stopped consuming messages")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current consumer status"""
        return {
            'running': self.running,
            'message_count': self.message_count,
            'window_size': len(self.current_window),
            'last_drift_check': self.last_drift_check.isoformat(),
            'reference_data_size': len(self.reference_data) if self.reference_data is not None else 0
        }


def main():
    """Example usage of the DriftDataConsumer"""
    consumer = DriftDataConsumer()
    
    try:
        print("🚀 Starting Kafka consumer for drift detection...")
        consumer.start_consuming()
    except KeyboardInterrupt:
        print("\n🛑 Stopping consumer...")
    finally:
        consumer.stop_consuming()


if __name__ == "__main__":
    main() 