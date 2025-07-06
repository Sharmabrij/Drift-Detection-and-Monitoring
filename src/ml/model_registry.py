"""
Model Registry for ML Pipeline Integration

This module provides a comprehensive model registry system that integrates
with MLflow for model versioning and Kafka for deployment tracking.
"""

import mlflow
import mlflow.sklearn
import mlflow.pytorch
import mlflow.tensorflow
import os
import json
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import logging

# Import Kafka components
from src.kafka import DriftDataProducer
from src.kafka.config import get_kafka_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelMetadata:
    """Model metadata structure"""
    model_name: str
    version: str
    model_type: str
    accuracy: float
    training_date: str
    features: List[str]
    hyperparameters: Dict[str, Any]
    model_path: str
    mlflow_run_id: Optional[str] = None
    deployment_status: str = "pending"
    drift_score: Optional[float] = None
    last_evaluation: Optional[str] = None

class ModelRegistry:
    """Advanced Model Registry with MLflow and Kafka Integration"""
    
    def __init__(self, registry_path: str = "models/", experiment_name: str = "drift_monitoring"):
        self.registry_path = registry_path
        self.experiment_name = experiment_name
        self.kafka_config = get_kafka_config()
        
        # Ensure directories exist
        os.makedirs(self.registry_path, exist_ok=True)
        os.makedirs(f"{self.registry_path}/metadata", exist_ok=True)
        os.makedirs(f"{self.registry_path}/artifacts", exist_ok=True)
        
        # Setup MLflow
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        mlflow.set_experiment(experiment_name)
        
        # Initialize Kafka producer for model events
        self.kafka_producer = None
        self._setup_kafka()
    
    def _setup_kafka(self):
        """Setup Kafka producer for model events"""
        try:
            self.kafka_producer = DriftDataProducer(
                bootstrap_servers=self.kafka_config['bootstrap_servers'],
                topic="model-events"
            )
            logger.info("✅ Kafka producer initialized for model events")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize Kafka producer: {e}")
    
    def register_model(self, 
                      model, 
                      model_name: str,
                      model_type: str = "sklearn",
                      accuracy: float = None,
                      features: List[str] = None,
                      hyperparameters: Dict[str, Any] = None,
                      tags: Dict[str, str] = None) -> ModelMetadata:
        """Register a model with comprehensive metadata"""
        
        try:
            # Generate version
            version = self._generate_version(model_name)
            
            # Create model metadata
            metadata = ModelMetadata(
                model_name=model_name,
                version=version,
                model_type=model_type,
                accuracy=accuracy or 0.0,
                training_date=datetime.now().isoformat(),
                features=features or [],
                hyperparameters=hyperparameters or {},
                model_path=f"{self.registry_path}/artifacts/{model_name}_{version}.pkl",
                deployment_status="registered"
            )
            
            # Save model locally
            with open(metadata.model_path, 'wb') as f:
                pickle.dump(model, f)
            
            # Log with MLflow
            with mlflow.start_run(run_name=f"{model_name}_{version}"):
                # Log model
                if model_type == "sklearn":
                    mlflow.sklearn.log_model(model, "model")
                elif model_type == "pytorch":
                    mlflow.pytorch.log_model(model, "model")
                elif model_type == "tensorflow":
                    mlflow.tensorflow.log_model(model, "model")
                
                # Log metrics
                if accuracy is not None:
                    mlflow.log_metric("accuracy", accuracy)
                
                # Log parameters
                if hyperparameters:
                    mlflow.log_params(hyperparameters)
                
                # Log tags
                if tags:
                    mlflow.set_tags(tags)
                
                # Store run ID
                metadata.mlflow_run_id = mlflow.active_run().info.run_id
            
            # Save metadata
            self._save_metadata(metadata)
            
            # Send model event to Kafka
            self._send_model_event("model_registered", metadata)
            
            logger.info(f"✅ Model registered: {model_name} v{version}")
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Error registering model: {e}")
            raise
    
    def load_model(self, model_name: str, version: str = None) -> Any:
        """Load a model from registry"""
        try:
            if version is None:
                version = self._get_latest_version(model_name)
            
            metadata = self._load_metadata(model_name, version)
            
            # Load model
            with open(metadata.model_path, 'rb') as f:
                model = pickle.load(f)
            
            logger.info(f"✅ Model loaded: {model_name} v{version}")
            return model, metadata
            
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            raise
    
    def deploy_model(self, model_name: str, version: str = None, environment: str = "production") -> bool:
        """Deploy a model to specified environment"""
        try:
            if version is None:
                version = self._get_latest_version(model_name)
            
            metadata = self._load_metadata(model_name, version)
            
            # Update deployment status
            metadata.deployment_status = f"deployed_{environment}"
            self._save_metadata(metadata)
            
            # Send deployment event to Kafka
            self._send_model_event("model_deployed", metadata, {"environment": environment})
            
            logger.info(f"✅ Model deployed: {model_name} v{version} to {environment}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deploying model: {e}")
            return False
    
    def evaluate_model_drift(self, model_name: str, version: str, reference_data: pd.DataFrame, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate model drift using multiple metrics"""
        try:
            from src.detection.psi import calculate_psi, get_drift_status
            
            # Load model
            model, metadata = self.load_model(model_name, version)
            
            # Calculate drift metrics for each feature
            drift_results = {}
            feature_cols = [col for col in reference_data.columns if col.startswith('feature')]
            
            for feature in feature_cols:
                psi_score = calculate_psi(reference_data[feature], current_data[feature])
                drift_status = get_drift_status(psi_score)
                
                drift_results[feature] = {
                    "psi_score": psi_score,
                    "drift_status": drift_status
                }
            
            # Calculate average PSI
            avg_psi = np.mean([result["psi_score"] for result in drift_results.values()])
            overall_status = get_drift_status(avg_psi)
            
            # Update metadata
            metadata.drift_score = avg_psi
            metadata.last_evaluation = datetime.now().isoformat()
            self._save_metadata(metadata)
            
            # Send drift evaluation event to Kafka
            self._send_model_event("drift_evaluated", metadata, {
                "avg_psi": avg_psi,
                "overall_status": overall_status,
                "feature_results": drift_results
            })
            
            return {
                "model_name": model_name,
                "version": version,
                "avg_psi": avg_psi,
                "overall_status": overall_status,
                "feature_results": drift_results,
                "evaluation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error evaluating drift: {e}")
            raise
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all registered models"""
        try:
            models = []
            metadata_dir = f"{self.registry_path}/metadata"
            
            if os.path.exists(metadata_dir):
                for filename in os.listdir(metadata_dir):
                    if filename.endswith('.json'):
                        model_name, version = filename.replace('.json', '').split('_v')
                        metadata = self._load_metadata(model_name, version)
                        models.append(asdict(metadata))
            
            return models
            
        except Exception as e:
            logger.error(f"❌ Error listing models: {e}")
            return []
    
    def get_model_history(self, model_name: str) -> List[ModelMetadata]:
        """Get version history for a model"""
        try:
            versions = self._get_model_versions(model_name)
            history = []
            
            for version in versions:
                metadata = self._load_metadata(model_name, version)
                history.append(metadata)
            
            return sorted(history, key=lambda x: x.training_date, reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Error getting model history: {e}")
            return []
    
    def promote_model(self, model_name: str, version: str, promotion_level: str = "staging") -> bool:
        """Promote a model to a higher environment"""
        try:
            metadata = self._load_metadata(model_name, version)
            
            # Update promotion status
            metadata.deployment_status = f"promoted_{promotion_level}"
            self._save_metadata(metadata)
            
            # Send promotion event to Kafka
            self._send_model_event("model_promoted", metadata, {"promotion_level": promotion_level})
            
            logger.info(f"✅ Model promoted: {model_name} v{version} to {promotion_level}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error promoting model: {e}")
            return False
    
    def _generate_version(self, model_name: str) -> str:
        """Generate version number for model"""
        versions = self._get_model_versions(model_name)
        if not versions:
            return "1.0.0"
        
        # Get latest version and increment
        latest_version = max(versions, key=lambda v: [int(x) for x in v.split('.')])
        major, minor, patch = map(int, latest_version.split('.'))
        return f"{major}.{minor}.{patch + 1}"
    
    def _get_model_versions(self, model_name: str) -> List[str]:
        """Get all versions for a model"""
        versions = []
        metadata_dir = f"{self.registry_path}/metadata"
        
        if os.path.exists(metadata_dir):
            for filename in os.listdir(metadata_dir):
                if filename.startswith(f"{model_name}_v") and filename.endswith('.json'):
                    version = filename.replace(f"{model_name}_v", "").replace('.json', '')
                    versions.append(version)
        
        return versions
    
    def _get_latest_version(self, model_name: str) -> str:
        """Get latest version of a model"""
        versions = self._get_model_versions(model_name)
        if not versions:
            raise ValueError(f"No versions found for model: {model_name}")
        
        return max(versions, key=lambda v: [int(x) for x in v.split('.')])
    
    def _save_metadata(self, metadata: ModelMetadata):
        """Save model metadata to file"""
        metadata_path = f"{self.registry_path}/metadata/{metadata.model_name}_v{metadata.version}.json"
        with open(metadata_path, 'w') as f:
            json.dump(asdict(metadata), f, indent=2)
    
    def _load_metadata(self, model_name: str, version: str) -> ModelMetadata:
        """Load model metadata from file"""
        metadata_path = f"{self.registry_path}/metadata/{model_name}_v{version}.json"
        with open(metadata_path, 'r') as f:
            data = json.load(f)
            return ModelMetadata(**data)
    
    def _send_model_event(self, event_type: str, metadata: ModelMetadata, additional_data: Dict[str, Any] = None):
        """Send model event to Kafka"""
        if self.kafka_producer is None:
            return
        
        try:
            event = {
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "model_name": metadata.model_name,
                "version": metadata.version,
                "model_type": metadata.model_type,
                "accuracy": metadata.accuracy,
                "deployment_status": metadata.deployment_status,
                "drift_score": metadata.drift_score
            }
            
            if additional_data:
                event.update(additional_data)
            
            self.kafka_producer.send_data_point(event)
            
        except Exception as e:
            logger.warning(f"⚠️ Could not send model event to Kafka: {e}")

# Utility functions
def create_model_registry(registry_path: str = "models/") -> ModelRegistry:
    """Create and return a model registry instance"""
    return ModelRegistry(registry_path)

def register_trained_model(model, 
                          model_name: str,
                          accuracy: float,
                          features: List[str],
                          hyperparameters: Dict[str, Any] = None) -> ModelMetadata:
    """Convenience function to register a trained model"""
    registry = create_model_registry()
    return registry.register_model(
        model=model,
        model_name=model_name,
        accuracy=accuracy,
        features=features,
        hyperparameters=hyperparameters or {}
    )

if __name__ == "__main__":
    # Example usage
    registry = create_model_registry()
    
    # List all models
    models = registry.list_models()
    print(f"Registered models: {len(models)}")
    
    for model in models:
        print(f"- {model['model_name']} v{model['version']} ({model['deployment_status']})") 