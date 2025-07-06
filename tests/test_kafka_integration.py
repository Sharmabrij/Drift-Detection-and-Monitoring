import pytest
import time
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from kafka import DriftDataProducer, DriftDataConsumer
from kafka.config import get_kafka_config, get_drift_config

class TestKafkaIntegration:
    """Test Kafka integration components"""
    
    def test_kafka_config(self):
        """Test Kafka configuration loading"""
        config = get_kafka_config()
        
        assert 'bootstrap_servers' in config
        assert 'topic' in config
        assert 'group_id' in config
        assert 'producer_config' in config
        assert 'consumer_config' in config
        
        # Test default values
        assert config['bootstrap_servers'] == 'localhost:9092'
        assert config['topic'] == 'drift-data'
        assert config['group_id'] == 'drift-monitor-group'
    
    def test_drift_config(self):
        """Test drift detection configuration"""
        config = get_drift_config()
        
        assert 'window_size' in config
        assert 'check_interval' in config
        assert 'min_samples' in config
        assert 'psi_thresholds' in config
        
        # Test default values
        assert config['window_size'] == 1000
        assert config['check_interval'] == 100
        assert config['min_samples'] == 100
        assert config['psi_thresholds']['no_drift'] == 0.1
        assert config['psi_thresholds']['possible_drift'] == 0.25
    
    @patch('kafka.KafkaProducer')
    def test_producer_initialization(self, mock_kafka_producer):
        """Test Kafka producer initialization"""
        mock_producer_instance = Mock()
        mock_kafka_producer.return_value = mock_producer_instance
        
        producer = DriftDataProducer(
            bootstrap_servers='localhost:9092',
            topic='test-topic'
        )
        
        assert producer.bootstrap_servers == 'localhost:9092'
        assert producer.topic == 'test-topic'
        assert producer.producer is not None
    
    @patch('kafka.KafkaConsumer')
    def test_consumer_initialization(self, mock_kafka_consumer):
        """Test Kafka consumer initialization"""
        mock_consumer_instance = Mock()
        mock_kafka_consumer.return_value = mock_consumer_instance
        
        consumer = DriftDataConsumer(
            bootstrap_servers='localhost:9092',
            topic='test-topic',
            group_id='test-group',
            window_size=500,
            check_interval=50
        )
        
        assert consumer.bootstrap_servers == 'localhost:9092'
        assert consumer.topic == 'test-topic'
        assert consumer.group_id == 'test-group'
        assert consumer.window_size == 500
        assert consumer.check_interval == 50
        assert consumer.consumer is not None
    
    def test_producer_data_generation(self):
        """Test synthetic data generation in producer"""
        with patch('kafka.KafkaProducer'):
            producer = DriftDataProducer(
                bootstrap_servers='localhost:9092',
                topic='test-topic'
            )
            
            # Test normal data generation
            sent, total = producer.generate_and_send_synthetic_data(
                n_samples=10, 
                drift=False
            )
            
            assert sent >= 0
            assert total == 10
            
            # Test drifted data generation
            sent, total = producer.generate_and_send_synthetic_data(
                n_samples=10, 
                drift=True
            )
            
            assert sent >= 0
            assert total == 10
    
    def test_consumer_status(self):
        """Test consumer status reporting"""
        with patch('kafka.KafkaConsumer'):
            consumer = DriftDataConsumer(
                bootstrap_servers='localhost:9092',
                topic='test-topic',
                group_id='test-group'
            )
            
            status = consumer.get_status()
            
            assert 'running' in status
            assert 'message_count' in status
            assert 'window_size' in status
            assert 'last_drift_check' in status
            assert 'reference_data_size' in status
    
    def test_producer_send_data_point(self):
        """Test sending individual data points"""
        with patch('kafka.KafkaProducer') as mock_kafka_producer:
            mock_producer_instance = Mock()
            mock_future = Mock()
            mock_future.get.return_value = Mock(partition=0, offset=1)
            mock_producer_instance.send.return_value = mock_future
            mock_kafka_producer.return_value = mock_producer_instance
            
            producer = DriftDataProducer(
                bootstrap_servers='localhost:9092',
                topic='test-topic'
            )
            
            # Test sending data point
            data = {
                'feature1': 0.5,
                'feature2': 1.2,
                'feature3': -0.3,
                'feature4': 0.8,
                'feature5': 0.1,
                'target': 1
            }
            
            result = producer.send_data_point(data)
            assert result is True
    
    def test_consumer_window_management(self):
        """Test consumer sliding window management"""
        with patch('kafka.KafkaConsumer'):
            consumer = DriftDataConsumer(
                bootstrap_servers='localhost:9092',
                topic='test-topic',
                window_size=5
            )
            
            # Test window size limit
            for i in range(10):
                data = {
                    'feature1': i,
                    'feature2': i * 2,
                    'feature3': i * 3,
                    'feature4': i * 4,
                    'feature5': i * 5,
                    'target': i % 2,
                    'timestamp': f'2024-01-01T{i:02d}:00:00'
                }
                consumer.current_window.append(data)
            
            # Window should be limited to 5 items
            assert len(consumer.current_window) == 5
    
    def test_psi_calculation_integration(self):
        """Test PSI calculation integration with consumer"""
        with patch('kafka.KafkaConsumer'):
            consumer = DriftDataConsumer(
                bootstrap_servers='localhost:9092',
                topic='test-topic',
                window_size=100
            )
            
            # Add some test data to window
            for i in range(50):
                data = {
                    'feature1': np.random.normal(0, 1),
                    'feature2': np.random.normal(0, 1),
                    'feature3': np.random.normal(0, 1),
                    'feature4': np.random.normal(0, 1),
                    'feature5': np.random.normal(0, 1),
                    'target': np.random.randint(0, 2),
                    'timestamp': f'2024-01-01T{i:02d}:00:00'
                }
                consumer.current_window.append(data)
            
            # Test drift check (should not fail with test data)
            try:
                consumer._check_drift()
                # If no exception, test passes
                assert True
            except Exception as e:
                # If exception occurs, it should be handled gracefully
                assert "reference data" in str(e).lower() or "empty" in str(e).lower()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 