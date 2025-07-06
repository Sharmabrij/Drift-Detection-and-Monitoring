import json
import time
import pandas as pd
import numpy as np
from datetime import datetime
from kafka import KafkaProducer
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DriftDataProducer:
    """
    Kafka producer for streaming drift monitoring data
    """
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092', topic: str = 'drift-data'):
        """
        Initialize Kafka producer
        
        Args:
            bootstrap_servers: Kafka broker addresses
            topic: Kafka topic to produce to
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3
            )
            logger.info(f"✅ Connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Kafka: {e}")
            raise
    
    def send_data_point(self, data: Dict[str, Any], key: Optional[str] = None):
        """
        Send a single data point to Kafka
        
        Args:
            data: Dictionary containing the data point
            key: Optional message key for partitioning
        """
        if not self.producer:
            logger.error("❌ Producer not connected")
            return False
        
        try:
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().isoformat()
            
            # Send to Kafka
            future = self.producer.send(
                topic=self.topic,
                key=key,
                value=data
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            logger.info(f"📤 Sent data to {self.topic} [partition: {record_metadata.partition}, offset: {record_metadata.offset}]")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send data: {e}")
            return False
    
    def send_batch(self, data_batch: pd.DataFrame, key_column: Optional[str] = None):
        """
        Send a batch of data points to Kafka
        
        Args:
            data_batch: DataFrame containing multiple data points
            key_column: Optional column name to use as message key
        """
        success_count = 0
        total_count = len(data_batch)
        
        for idx, row in data_batch.iterrows():
            data = row.to_dict()
            key = str(data.get(key_column, idx)) if key_column else str(idx)
            
            if self.send_data_point(data, key):
                success_count += 1
        
        logger.info(f"📦 Sent {success_count}/{total_count} records to {self.topic}")
        return success_count, total_count
    
    def generate_and_send_synthetic_data(self, n_samples: int = 100, drift: bool = False):
        """
        Generate synthetic data and send to Kafka
        
        Args:
            n_samples: Number of samples to generate
            drift: Whether to introduce drift in the data
        """
        # Generate synthetic data
        if drift:
            # Generate drifted data
            data = np.random.normal(0.5, 1, (n_samples, 5))  # Shifted mean
        else:
            # Generate normal data
            data = np.random.normal(0, 1, (n_samples, 5))
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=[f'feature{i}' for i in range(1, 6)])
        df['target'] = np.random.randint(0, 2, n_samples)
        df['timestamp'] = pd.Timestamp.now()
        
        # Send to Kafka
        return self.send_batch(df)
    
    def close(self):
        """Close the Kafka producer connection"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("🔌 Kafka producer connection closed")


def main():
    """Example usage of the DriftDataProducer"""
    producer = DriftDataProducer()
    
    try:
        # Send some synthetic data
        print("📊 Generating and sending synthetic data...")
        producer.generate_and_send_synthetic_data(n_samples=50, drift=False)
        
        # Send drifted data
        print("📊 Generating and sending drifted data...")
        producer.generate_and_send_synthetic_data(n_samples=50, drift=True)
        
    finally:
        producer.close()


if __name__ == "__main__":
    main() 