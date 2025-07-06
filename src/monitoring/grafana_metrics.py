"""
Grafana Metrics Integration for ML Pipeline

This module provides comprehensive metrics collection and monitoring
for the ML pipeline with Kafka integration, designed to work with
Grafana and Prometheus.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass, asdict
import json
import os

# Prometheus metrics
try:
    from prometheus_client import (
        Counter, Gauge, Histogram, Summary, 
        generate_latest, CONTENT_TYPE_LATEST,
        start_http_server, CollectorRegistry
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus client not available. Metrics will be disabled.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Metric data point structure"""
    timestamp: float
    value: float
    labels: Dict[str, str]

class MLPipelineMetrics:
    """Comprehensive metrics collection for ML Pipeline"""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.registry = CollectorRegistry()
        self.metrics = {}
        self.metric_history = {}
        self.running = False
        
        if PROMETHEUS_AVAILABLE:
            self._setup_prometheus_metrics()
            self._start_metrics_server()
        else:
            logger.warning("Prometheus not available. Using internal metrics only.")
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics"""
        
        # Kafka metrics
        self.metrics['kafka_producer_messages_total'] = Counter(
            'kafka_producer_messages_total',
            'Total messages sent by Kafka producer',
            ['topic', 'status'],
            registry=self.registry
        )
        
        self.metrics['kafka_consumer_messages_total'] = Counter(
            'kafka_consumer_messages_total',
            'Total messages consumed by Kafka consumer',
            ['topic', 'group_id'],
            registry=self.registry
        )
        
        self.metrics['kafka_message_latency_seconds'] = Histogram(
            'kafka_message_latency_seconds',
            'Message processing latency in seconds',
            ['topic', 'operation'],
            registry=self.registry
        )
        
        # Drift detection metrics
        self.metrics['drift_detection_psi_score'] = Gauge(
            'drift_detection_psi_score',
            'Current PSI score for drift detection',
            ['feature', 'model_name'],
            registry=self.registry
        )
        
        self.metrics['drift_detection_alerts_total'] = Counter(
            'drift_detection_alerts_total',
            'Total drift detection alerts',
            ['severity', 'model_name'],
            registry=self.registry
        )
        
        self.metrics['feature_drift_psi_score'] = Gauge(
            'feature_drift_psi_score',
            'PSI score for individual features',
            ['feature_name', 'model_name'],
            registry=self.registry
        )
        
        # Model performance metrics
        self.metrics['model_accuracy'] = Gauge(
            'model_accuracy',
            'Model accuracy score',
            ['model_name', 'version'],
            registry=self.registry
        )
        
        self.metrics['model_prediction_latency_seconds'] = Histogram(
            'model_prediction_latency_seconds',
            'Model prediction latency in seconds',
            ['model_name', 'version'],
            registry=self.registry
        )
        
        self.metrics['model_confidence_score'] = Gauge(
            'model_confidence_score',
            'Model confidence score',
            ['model_name', 'version'],
            registry=self.registry
        )
        
        self.metrics['model_predictions_total'] = Counter(
            'model_predictions_total',
            'Total predictions made by model',
            ['model_name', 'version', 'status'],
            registry=self.registry
        )
        
        # Pipeline execution metrics
        self.metrics['prefect_flow_runs_total'] = Counter(
            'prefect_flow_runs_total',
            'Total Prefect flow runs',
            ['flow_name', 'status'],
            registry=self.registry
        )
        
        self.metrics['prefect_flow_duration_seconds'] = Histogram(
            'prefect_flow_duration_seconds',
            'Prefect flow execution duration',
            ['flow_name'],
            registry=self.registry
        )
        
        self.metrics['pipeline_stage_duration_seconds'] = Histogram(
            'pipeline_stage_duration_seconds',
            'Pipeline stage execution duration',
            ['stage_name', 'pipeline_name'],
            registry=self.registry
        )
        
        # Model registry metrics
        self.metrics['model_registry_total_models'] = Gauge(
            'model_registry_total_models',
            'Total models in registry',
            ['status'],
            registry=self.registry
        )
        
        self.metrics['model_registry_operations_total'] = Counter(
            'model_registry_operations_total',
            'Total model registry operations',
            ['operation', 'status'],
            registry=self.registry
        )
        
        # System metrics
        self.metrics['process_cpu_seconds_total'] = Counter(
            'process_cpu_seconds_total',
            'Total CPU time used by process',
            registry=self.registry
        )
        
        self.metrics['process_resident_memory_bytes'] = Gauge(
            'process_resident_memory_bytes',
            'Resident memory usage in bytes',
            registry=self.registry
        )
        
        # Custom business metrics
        self.metrics['data_quality_score'] = Gauge(
            'data_quality_score',
            'Data quality score',
            ['dataset', 'metric'],
            registry=self.registry
        )
        
        self.metrics['business_impact_score'] = Gauge(
            'business_impact_score',
            'Business impact score',
            ['metric', 'model_name'],
            registry=self.registry
        )
    
    def _start_metrics_server(self):
        """Start Prometheus metrics server"""
        try:
            start_http_server(self.port, registry=self.registry)
            logger.info(f"✅ Prometheus metrics server started on port {self.port}")
        except Exception as e:
            logger.error(f"❌ Failed to start metrics server: {e}")
    
    def record_kafka_message(self, topic: str, operation: str, status: str = "success", 
                           latency: float = None, group_id: str = None):
        """Record Kafka message metrics"""
        if operation == "produce":
            self.metrics['kafka_producer_messages_total'].labels(topic=topic, status=status).inc()
        elif operation == "consume":
            self.metrics['kafka_consumer_messages_total'].labels(topic=topic, group_id=group_id or "default").inc()
        
        if latency is not None:
            self.metrics['kafka_message_latency_seconds'].labels(topic=topic, operation=operation).observe(latency)
    
    def record_drift_detection(self, psi_score: float, feature: str = "overall", 
                              model_name: str = "default", severity: str = None):
        """Record drift detection metrics"""
        self.metrics['drift_detection_psi_score'].labels(feature=feature, model_name=model_name).set(psi_score)
        
        if feature != "overall":
            self.metrics['feature_drift_psi_score'].labels(feature_name=feature, model_name=model_name).set(psi_score)
        
        if severity:
            self.metrics['drift_detection_alerts_total'].labels(severity=severity, model_name=model_name).inc()
    
    def record_model_performance(self, model_name: str, version: str, accuracy: float = None,
                               confidence: float = None, latency: float = None, 
                               prediction_status: str = "success"):
        """Record model performance metrics"""
        if accuracy is not None:
            self.metrics['model_accuracy'].labels(model_name=model_name, version=version).set(accuracy)
        
        if confidence is not None:
            self.metrics['model_confidence_score'].labels(model_name=model_name, version=version).set(confidence)
        
        if latency is not None:
            self.metrics['model_prediction_latency_seconds'].labels(model_name=model_name, version=version).observe(latency)
        
        self.metrics['model_predictions_total'].labels(model_name=model_name, version=version, status=prediction_status).inc()
    
    def record_prefect_flow(self, flow_name: str, status: str, duration: float = None):
        """Record Prefect flow metrics"""
        self.metrics['prefect_flow_runs_total'].labels(flow_name=flow_name, status=status).inc()
        
        if duration is not None:
            self.metrics['prefect_flow_duration_seconds'].labels(flow_name=flow_name).observe(duration)
    
    def record_pipeline_stage(self, stage_name: str, pipeline_name: str, duration: float):
        """Record pipeline stage metrics"""
        self.metrics['pipeline_stage_duration_seconds'].labels(stage_name=stage_name, pipeline_name=pipeline_name).observe(duration)
    
    def record_model_registry_operation(self, operation: str, status: str, model_count: int = None):
        """Record model registry metrics"""
        self.metrics['model_registry_operations_total'].labels(operation=operation, status=status).inc()
        
        if model_count is not None:
            self.metrics['model_registry_total_models'].labels(status=status).set(model_count)
    
    def record_data_quality(self, dataset: str, metric: str, score: float):
        """Record data quality metrics"""
        self.metrics['data_quality_score'].labels(dataset=dataset, metric=metric).set(score)
    
    def record_business_impact(self, metric: str, model_name: str, score: float):
        """Record business impact metrics"""
        self.metrics['business_impact_score'].labels(metric=metric, model_name=model_name).set(score)
    
    def update_system_metrics(self):
        """Update system metrics"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics['process_cpu_seconds_total'].inc(cpu_percent / 100)
            
            # Memory usage
            memory_info = psutil.virtual_memory()
            self.metrics['process_resident_memory_bytes'].set(memory_info.used)
            
        except ImportError:
            logger.warning("psutil not available. System metrics disabled.")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary for Grafana"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "kafka": {
                "producer_messages": self._get_counter_value('kafka_producer_messages_total'),
                "consumer_messages": self._get_counter_value('kafka_consumer_messages_total'),
                "avg_latency": self._get_histogram_avg('kafka_message_latency_seconds')
            },
            "drift_detection": {
                "current_psi": self._get_gauge_value('drift_detection_psi_score'),
                "alerts": self._get_counter_value('drift_detection_alerts_total')
            },
            "model_performance": {
                "accuracy": self._get_gauge_value('model_accuracy'),
                "confidence": self._get_gauge_value('model_confidence_score'),
                "predictions": self._get_counter_value('model_predictions_total')
            },
            "pipeline": {
                "flow_runs": self._get_counter_value('prefect_flow_runs_total'),
                "avg_duration": self._get_histogram_avg('prefect_flow_duration_seconds')
            },
            "registry": {
                "total_models": self._get_gauge_value('model_registry_total_models'),
                "operations": self._get_counter_value('model_registry_operations_total')
            }
        }
        
        return summary
    
    def _get_counter_value(self, metric_name: str) -> int:
        """Get counter metric value"""
        if metric_name in self.metrics:
            return self.metrics[metric_name]._value.get()
        return 0
    
    def _get_gauge_value(self, metric_name: str) -> float:
        """Get gauge metric value"""
        if metric_name in self.metrics:
            return self.metrics[metric_name]._value.get()
        return 0.0
    
    def _get_histogram_avg(self, metric_name: str) -> float:
        """Get histogram average value"""
        if metric_name in self.metrics:
            # This is a simplified version - in practice you'd use proper histogram quantiles
            return 0.0
        return 0.0
    
    def start_background_metrics_collection(self):
        """Start background metrics collection"""
        self.running = True
        
        def collect_metrics():
            while self.running:
                try:
                    self.update_system_metrics()
                    time.sleep(30)  # Update every 30 seconds
                except Exception as e:
                    logger.error(f"Error in background metrics collection: {e}")
        
        thread = threading.Thread(target=collect_metrics, daemon=True)
        thread.start()
        logger.info("✅ Background metrics collection started")
    
    def stop_metrics_collection(self):
        """Stop background metrics collection"""
        self.running = False
        logger.info("🛑 Background metrics collection stopped")

# Global metrics instance
_metrics_instance = None

def get_metrics() -> MLPipelineMetrics:
    """Get global metrics instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MLPipelineMetrics()
    return _metrics_instance

def record_metric(metric_type: str, **kwargs):
    """Convenience function to record metrics"""
    metrics = get_metrics()
    
    if metric_type == "kafka":
        metrics.record_kafka_message(**kwargs)
    elif metric_type == "drift":
        metrics.record_drift_detection(**kwargs)
    elif metric_type == "model":
        metrics.record_model_performance(**kwargs)
    elif metric_type == "flow":
        metrics.record_prefect_flow(**kwargs)
    elif metric_type == "pipeline":
        metrics.record_pipeline_stage(**kwargs)
    elif metric_type == "registry":
        metrics.record_model_registry_operation(**kwargs)
    elif metric_type == "data_quality":
        metrics.record_data_quality(**kwargs)
    elif metric_type == "business_impact":
        metrics.record_business_impact(**kwargs)

# Decorator for automatic metrics collection
def with_metrics(metric_type: str, **metric_kwargs):
    """Decorator to automatically collect metrics"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Record success metrics
                if metric_type == "flow":
                    record_metric("flow", flow_name=func.__name__, status="completed", 
                                duration=time.time() - start_time)
                elif metric_type == "pipeline":
                    record_metric("pipeline", stage_name=func.__name__, 
                                pipeline_name="ml_pipeline", duration=time.time() - start_time)
                
                return result
                
            except Exception as e:
                # Record failure metrics
                if metric_type == "flow":
                    record_metric("flow", flow_name=func.__name__, status="failed")
                elif metric_type == "pipeline":
                    record_metric("pipeline", stage_name=func.__name__, 
                                pipeline_name="ml_pipeline", duration=time.time() - start_time)
                
                raise
        
        return wrapper
    return decorator

if __name__ == "__main__":
    # Example usage
    metrics = get_metrics()
    metrics.start_background_metrics_collection()
    
    # Record some example metrics
    metrics.record_kafka_message("drift-data", "produce", "success", 0.1)
    metrics.record_drift_detection(0.15, "feature_1", "model_v1", "medium")
    metrics.record_model_performance("model_v1", "1.0.0", accuracy=0.95, confidence=0.88)
    
    print("Metrics server running. Visit http://localhost:8000/metrics")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        metrics.stop_metrics_collection()
        print("Metrics collection stopped.") 