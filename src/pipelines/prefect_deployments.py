"""
Prefect Deployment Configuration for ML Pipeline with Kafka

This module contains deployment configurations for various Prefect flows
with advanced scheduling, monitoring, and orchestration features.
"""

from prefect import serve
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule, IntervalSchedule
from prefect.filesystems import LocalFileSystem
from prefect.blocks.system import Secret
from prefect.blocks.notifications import SlackWebhook
import os
from datetime import timedelta

# Import flows
from src.pipelines.kafka_ml_pipeline import (
    complete_ml_pipeline_flow,
    model_retraining_pipeline_flow,
    kafka_ml_pipeline_demo_flow
)
from flows.kafka_drift_detection_flow import kafka_drift_detection_flow
from flows.psi_drift_detection_flow import psi_drift_detection_flow

def create_deployments():
    """Create all Prefect deployments"""
    
    # Create storage block
    storage = LocalFileSystem(basepath="/tmp/prefect")
    
    # Create deployments
    deployments = []
    
    # 1. Daily Drift Monitoring Deployment
    daily_drift_deployment = Deployment.build_from_flow(
        flow=psi_drift_detection_flow,
        name="daily-drift-monitoring",
        version="1.0.0",
        work_queue_name="drift-monitoring",
        storage=storage,
        schedule=CronSchedule(cron="0 9 * * *", timezone="UTC"),  # Daily at 9 AM UTC
        tags=["drift-monitoring", "daily", "production"],
        description="Daily drift monitoring with PSI calculation",
        parameters={},
        infra_overrides={
            "env": {
                "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092",
                "SLACK_WEBHOOK_URL": "{{ $SLACK_WEBHOOK_URL }}"
            }
        }
    )
    deployments.append(daily_drift_deployment)
    
    # 2. Real-time Kafka Drift Detection
    kafka_drift_deployment = Deployment.build_from_flow(
        flow=kafka_drift_detection_flow,
        name="kafka-real-time-drift",
        version="1.0.0",
        work_queue_name="kafka-drift",
        storage=storage,
        schedule=IntervalSchedule(interval=timedelta(minutes=30)),  # Every 30 minutes
        tags=["kafka", "real-time", "drift-detection"],
        description="Real-time drift detection using Kafka streams",
        parameters={
            "test_data_samples": 1000,
            "detection_duration": 10,
            "enable_prometheus": True
        },
        infra_overrides={
            "env": {
                "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092",
                "KAFKA_TOPIC": "drift-data",
                "DRIFT_WINDOW_SIZE": "1000"
            }
        }
    )
    deployments.append(kafka_drift_deployment)
    
    # 3. Complete ML Pipeline
    ml_pipeline_deployment = Deployment.build_from_flow(
        flow=complete_ml_pipeline_flow,
        name="complete-ml-pipeline",
        version="1.0.0",
        work_queue_name="ml-pipeline",
        storage=storage,
        schedule=CronSchedule(cron="0 2 * * 0", timezone="UTC"),  # Weekly on Sunday at 2 AM
        tags=["ml-pipeline", "training", "deployment"],
        description="Complete ML pipeline with training, deployment, and monitoring",
        parameters={
            "data_path": "data/train.csv",
            "model_name": "production_model",
            "predictions_count": 5000,
            "drift_monitoring_duration": 15
        },
        infra_overrides={
            "env": {
                "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092",
                "MLFLOW_TRACKING_URI": "sqlite:///mlflow.db"
            }
        }
    )
    deployments.append(ml_pipeline_deployment)
    
    # 4. Model Retraining Pipeline
    retraining_deployment = Deployment.build_from_flow(
        flow=model_retraining_pipeline_flow,
        name="model-retraining-pipeline",
        version="1.0.0",
        work_queue_name="retraining",
        storage=storage,
        schedule=IntervalSchedule(interval=timedelta(hours=6)),  # Every 6 hours
        tags=["retraining", "automated", "mlops"],
        description="Automated model retraining based on drift detection",
        parameters={
            "retrain_threshold": 0.15,
            "data_path": "data/train.csv"
        },
        infra_overrides={
            "env": {
                "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092",
                "DRIFT_CHECK_INTERVAL": "50"
            }
        }
    )
    deployments.append(retraining_deployment)
    
    # 5. Demo Pipeline (Manual trigger only)
    demo_deployment = Deployment.build_from_flow(
        flow=kafka_ml_pipeline_demo_flow,
        name="kafka-ml-demo",
        version="1.0.0",
        work_queue_name="demo",
        storage=storage,
        tags=["demo", "testing"],
        description="Demo pipeline for Kafka ML integration",
        parameters={},
        infra_overrides={
            "env": {
                "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092"
            }
        }
    )
    deployments.append(demo_deployment)
    
    return deployments

def create_notification_blocks():
    """Create notification blocks for alerts"""
    
    # Slack notification block
    try:
        slack_webhook = SlackWebhook(
            url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
        )
        slack_webhook.save(name="drift-alerts")
        print("✅ Slack notification block created")
    except Exception as e:
        print(f"⚠️ Could not create Slack block: {e}")
    
    # Secret block for sensitive data
    try:
        kafka_secret = Secret(value="your-kafka-secret-here")
        kafka_secret.save(name="kafka-credentials")
        print("✅ Kafka secret block created")
    except Exception as e:
        print(f"⚠️ Could not create secret block: {e}")

def create_work_queues():
    """Create work queues for different types of work"""
    
    from prefect.server.schemas.core import WorkQueue
    
    queues = [
        "drift-monitoring",
        "kafka-drift", 
        "ml-pipeline",
        "retraining",
        "demo"
    ]
    
    for queue_name in queues:
        try:
            work_queue = WorkQueue(name=queue_name)
            work_queue.save()
            print(f"✅ Work queue '{queue_name}' created")
        except Exception as e:
            print(f"⚠️ Could not create work queue '{queue_name}': {e}")

def deploy_all():
    """Deploy all flows and create necessary infrastructure"""
    
    print("🚀 Setting up Prefect deployments...")
    
    # Create notification blocks
    create_notification_blocks()
    
    # Create work queues
    create_work_queues()
    
    # Create and apply deployments
    deployments = create_deployments()
    
    for deployment in deployments:
        try:
            deployment.apply()
            print(f"✅ Deployed: {deployment.name}")
        except Exception as e:
            print(f"❌ Failed to deploy {deployment.name}: {e}")
    
    print("🎉 Deployment setup completed!")

def serve_flows():
    """Serve flows for development and testing"""
    
    print("🚀 Starting Prefect server with flows...")
    
    # Serve all flows
    serve(
        complete_ml_pipeline_flow,
        model_retraining_pipeline_flow,
        kafka_ml_pipeline_demo_flow,
        kafka_drift_detection_flow,
        psi_drift_detection_flow,
        name="drift-monitoring-flows",
        port=4200
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Prefect Deployment Manager")
    parser.add_argument("--action", choices=["deploy", "serve"], 
                       default="deploy", help="Action to perform")
    
    args = parser.parse_args()
    
    if args.action == "deploy":
        deploy_all()
    elif args.action == "serve":
        serve_flows() 