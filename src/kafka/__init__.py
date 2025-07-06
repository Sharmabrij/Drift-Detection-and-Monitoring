"""
Kafka integration for drift monitoring

This module provides Kafka producer and consumer classes for real-time
drift detection from streaming data.
"""

from .producer import DriftDataProducer
from .consumer import DriftDataConsumer

__all__ = ['DriftDataProducer', 'DriftDataConsumer'] 