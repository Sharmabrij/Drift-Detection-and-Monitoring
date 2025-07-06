from prefect import flow, task, get_run_logger
from prefect.artifacts import create_markdown_artifact
from prefect.filesystems import LocalFileSystem
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
import pandas as pd
import numpy as np
import json
import os
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import warnings
warnings.filterwarnings('ignore')

# Import Kafka components
from src.kafka import DriftDataProducer, DriftDataConsumer
from src.kafka.config import get_kafka_config, get_drift_config
from src.detection.psi import calculate_psi, get_drift_status

# MLflow configuration
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("drift_monitoring")

class MLPipelineOrchestrator:
    """Advanced ML Pipeline Orchestrator with Kafka Integration"""
    
    def __init__(self):
        self.kafka_config = get_kafka_config()
        self.drift_config = get_drift_config()
        self.model_registry_path = "models/"
        self.data_path = "data/"
        self.reports_path = "reports/"
        
        # Ensure directories exist
        os.makedirs(self.model_registry_path, exist_ok=True)
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.reports_path, exist_ok=True)

@task(name="load_and_prepare_data")
def load_and_prepare_data(data_path: str) -> pd.DataFrame:
    """Load and prepare training data"""
    logger = get_run_logger()
    logger.info(f"📊 Loading data from {data_path}")
    
    try:
        df = pd.read_csv(data_path)
        logger.info(f"✅ Loaded {len(df)} records with {len(df.columns)} features")
        
        # Basic data validation
        missing_values = df.isnull().sum().sum()
        if missing_values > 0:
            logger.warning(f"⚠️ Found {missing_values} missing values")
            df = df.dropna()
        
        return df
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")
        raise

@task(name="train_ml_model")
def train_ml_model(data: pd.DataFrame, model_name: str = "drift_monitor_model") -> Dict[str, Any]:
    """Train ML model and log with MLflow"""
    logger = get_run_logger()
    
    try:
        # Prepare features and target
        feature_cols = [col for col in data.columns if col.startswith('feature')]
        X = data[feature_cols]
        y = data['target']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        logger.info(f"📈 Training model with {len(X_train)} samples")
        
        # Train model
        with mlflow.start_run(run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Log metrics
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("training_samples", len(X_train))
            mlflow.log_metric("test_samples", len(X_test))
            
            # Log model
            mlflow.sklearn.log_model(model, "model")
            
            # Save model locally
            model_path = f"models/{model_name}.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            logger.info(f"✅ Model trained with accuracy: {accuracy:.4f}")
            
            return {
                "model_path": model_path,
                "accuracy": accuracy,
                "feature_columns": feature_cols,
                "run_id": mlflow.active_run().info.run_id
            }
    
    except Exception as e:
        logger.error(f"❌ Error training model: {e}")
        raise

@task(name="deploy_model_to_kafka")
def deploy_model_to_kafka(model_info: Dict[str, Any], topic: str = "model-predictions"):
    """Deploy model and start Kafka producer for predictions"""
    logger = get_run_logger()
    
    try:
        # Load the trained model
        with open(model_info["model_path"], 'rb') as f:
            model = pickle.load(f)
        
        # Initialize Kafka producer
        producer = DriftDataProducer(
            bootstrap_servers=get_kafka_config()['bootstrap_servers'],
            topic=topic
        )
        
        logger.info(f"🚀 Model deployed to Kafka topic: {topic}")
        
        return {
            "model": model,
            "producer": producer,
            "feature_columns": model_info["feature_columns"]
        }
    
    except Exception as e:
        logger.error(f"❌ Error deploying model: {e}")
        raise

@task(name="generate_model_predictions")
def generate_model_predictions(deployment_info: Dict[str, Any], n_samples: int = 1000):
    """Generate predictions and send to Kafka"""
    logger = get_run_logger()
    
    try:
        model = deployment_info["model"]
        producer = deployment_info["producer"]
        feature_cols = deployment_info["feature_columns"]
        
        logger.info(f"📊 Generating {n_samples} predictions...")
        
        predictions_sent = 0
        
        for i in range(n_samples):
            # Generate synthetic data
            features = np.random.normal(0, 1, len(feature_cols))
            
            # Make prediction
            prediction = model.predict([features])[0]
            prediction_proba = model.predict_proba([features])[0]
            
            # Create message
            message = {
                "timestamp": datetime.now().isoformat(),
                "prediction": int(prediction),
                "confidence": float(max(prediction_proba)),
                "features": dict(zip(feature_cols, features.tolist())),
                "model_version": "v1.0"
            }
            
            # Send to Kafka
            if producer.send_data_point(message):
                predictions_sent += 1
            
            if i % 100 == 0:
                logger.info(f"📤 Sent {predictions_sent} predictions...")
        
        logger.info(f"✅ Generated and sent {predictions_sent} predictions")
        return predictions_sent
    
    except Exception as e:
        logger.error(f"❌ Error generating predictions: {e}")
        raise

@task(name="monitor_model_drift")
def monitor_model_drift(duration_minutes: int = 10) -> Dict[str, Any]:
    """Monitor model drift in real-time"""
    logger = get_run_logger()
    
    try:
        # Initialize Kafka consumer for drift monitoring
        consumer = DriftDataConsumer(
            bootstrap_servers=get_kafka_config()['bootstrap_servers'],
            topic=get_kafka_config()['topic'],
            group_id="ml-pipeline-drift-monitor",
            window_size=500,
            check_interval=50
        )
        
        logger.info(f"🔍 Starting drift monitoring for {duration_minutes} minutes...")
        
        # Start consumer in background
        consumer.start_background_consuming()
        
        # Monitor for specified duration
        start_time = datetime.now()
        drift_events = []
        
        while (datetime.now() - start_time).total_seconds() < duration_minutes * 60:
            status = consumer.get_status()
            
            # Check for drift events
            if status.get('message_count', 0) > 0 and status.get('message_count', 0) % 100 == 0:
                drift_events.append({
                    'timestamp': datetime.now().isoformat(),
                    'message_count': status.get('message_count', 0),
                    'window_size': status.get('window_size', 0)
                })
            
            # Log status every minute
            if len(drift_events) % 6 == 0:  # Every 6 events (approximately every minute)
                logger.info(f"📊 Drift Monitor Status: {status}")
            
            import time
            time.sleep(10)  # Check every 10 seconds
        
        # Stop consumer
        consumer.stop_consuming()
        
        logger.info(f"✅ Drift monitoring completed. Collected {len(drift_events)} events")
        
        return {
            'drift_events': drift_events,
            'monitoring_duration': duration_minutes,
            'final_status': consumer.get_status()
        }
    
    except Exception as e:
        logger.error(f"❌ Error in drift monitoring: {e}")
        raise

@task(name="generate_ml_pipeline_report")
def generate_ml_pipeline_report(
    model_info: Dict[str, Any],
    drift_results: Dict[str, Any],
    predictions_sent: int
) -> str:
    """Generate comprehensive ML pipeline report"""
    logger = get_run_logger()
    
    try:
        report_content = f"""
# ML Pipeline Execution Report

## Model Training Results
- **Model Accuracy**: {model_info.get('accuracy', 'N/A'):.4f}
- **Training Samples**: {model_info.get('training_samples', 'N/A')}
- **Test Samples**: {model_info.get('test_samples', 'N/A')}
- **MLflow Run ID**: {model_info.get('run_id', 'N/A')}

## Kafka Integration Results
- **Predictions Generated**: {predictions_sent}
- **Drift Monitoring Duration**: {drift_results.get('monitoring_duration', 'N/A')} minutes
- **Drift Events Collected**: {len(drift_results.get('drift_events', []))}

## Pipeline Performance
- **Total Execution Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status**: ✅ Completed Successfully

## Recommendations
1. Monitor model accuracy over time
2. Set up automated retraining triggers
3. Configure alerting for drift detection
4. Scale Kafka infrastructure as needed
        """
        
        # Save report
        report_path = f"reports/ml_pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        # Create Prefect artifact
        create_markdown_artifact(
            key="ml-pipeline-report",
            markdown=report_content,
            description="ML Pipeline Execution Report"
        )
        
        logger.info(f"📄 Report generated: {report_path}")
        return report_path
    
    except Exception as e:
        logger.error(f"❌ Error generating report: {e}")
        raise

@flow(name="Complete ML Pipeline with Kafka")
def complete_ml_pipeline_flow(
    data_path: str = "data/train.csv",
    model_name: str = "drift_monitor_model",
    predictions_count: int = 1000,
    drift_monitoring_duration: int = 5
):
    """
    Complete ML Pipeline with Kafka Integration
    
    This flow demonstrates a full ML pipeline:
    1. Data loading and preparation
    2. Model training with MLflow
    3. Model deployment to Kafka
    4. Real-time prediction generation
    5. Drift monitoring
    6. Report generation
    """
    logger = get_run_logger()
    logger.info("🚀 Starting Complete ML Pipeline with Kafka Integration")
    
    try:
        # Step 1: Load and prepare data
        data = load_and_prepare_data(data_path)
        
        # Step 2: Train ML model
        model_info = train_ml_model(data, model_name)
        
        # Step 3: Deploy model to Kafka
        deployment_info = deploy_model_to_kafka(model_info)
        
        # Step 4: Generate predictions
        predictions_sent = generate_model_predictions(deployment_info, predictions_count)
        
        # Step 5: Monitor drift
        drift_results = monitor_model_drift(drift_monitoring_duration)
        
        # Step 6: Generate report
        report_path = generate_ml_pipeline_report(model_info, drift_results, predictions_sent)
        
        logger.info("✅ Complete ML Pipeline executed successfully!")
        
        return {
            "model_info": model_info,
            "predictions_sent": predictions_sent,
            "drift_results": drift_results,
            "report_path": report_path
        }
    
    except Exception as e:
        logger.error(f"❌ ML Pipeline failed: {e}")
        raise

@flow(name="Model Retraining Pipeline")
def model_retraining_pipeline_flow(
    retrain_threshold: float = 0.1,
    data_path: str = "data/train.csv"
):
    """
    Automated Model Retraining Pipeline
    
    This flow checks for drift and triggers model retraining if needed
    """
    logger = get_run_logger()
    logger.info("🔄 Starting Model Retraining Pipeline")
    
    try:
        # Check current drift status
        consumer = DriftDataConsumer(
            bootstrap_servers=get_kafka_config()['bootstrap_servers'],
            topic=get_kafka_config()['topic'],
            group_id="retraining-monitor"
        )
        
        # Get recent drift status
        status = consumer.get_status()
        
        # Check if retraining is needed
        if status.get('last_psi_score', 0) > retrain_threshold:
            logger.warning(f"⚠️ Drift detected (PSI: {status.get('last_psi_score', 0):.4f}). Triggering retraining...")
            
            # Retrain model
            data = load_and_prepare_data(data_path)
            new_model_info = train_ml_model(data, "retrained_model")
            
            logger.info("✅ Model retraining completed")
            return {"retrained": True, "new_model_info": new_model_info}
        else:
            logger.info("✅ No retraining needed")
            return {"retrained": False, "reason": "No significant drift detected"}
    
    except Exception as e:
        logger.error(f"❌ Retraining pipeline failed: {e}")
        raise

@flow(name="Kafka ML Pipeline Demo")
def kafka_ml_pipeline_demo_flow():
    """Demo flow for Kafka ML Pipeline"""
    logger = get_run_logger()
    logger.info("🎯 Running Kafka ML Pipeline Demo")
    
    return complete_ml_pipeline_flow(
        data_path="data/train.csv",
        model_name="demo_model",
        predictions_count=500,
        drift_monitoring_duration=2
    )

if __name__ == "__main__":
    # Run the demo
    result = kafka_ml_pipeline_demo_flow()
    print(f"🎉 Demo completed: {result}") 