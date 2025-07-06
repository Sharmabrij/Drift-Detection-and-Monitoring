import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import json
import os
import mlflow
from typing import Dict, Any, List

# Import custom modules
from src.ml.model_registry import create_model_registry, ModelMetadata
from src.kafka import DriftDataProducer, DriftDataConsumer
from src.kafka.config import get_kafka_config, get_drift_config
from src.pipelines.kafka_ml_pipeline import complete_ml_pipeline_flow, model_retraining_pipeline_flow

# Page configuration
st.set_page_config(
    page_title="ML Pipeline with Kafka Integration",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .pipeline-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .metric-highlight {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #2196f3;
    }
    .status-running { color: #28a745; font-weight: bold; }
    .status-stopped { color: #dc3545; font-weight: bold; }
    .status-pending { color: #ffc107; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'model_registry' not in st.session_state:
    st.session_state.model_registry = create_model_registry()
if 'kafka_producer' not in st.session_state:
    st.session_state.kafka_producer = None
if 'kafka_consumer' not in st.session_state:
    st.session_state.kafka_consumer = None
if 'pipeline_running' not in st.session_state:
    st.session_state.pipeline_running = False

# Main header
st.markdown('<h1 class="main-header">🤖 ML Pipeline with Kafka Integration</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Pipeline Configuration")
    
    # Pipeline type selection
    pipeline_type = st.selectbox(
        "Pipeline Type",
        ["Complete ML Pipeline", "Model Retraining", "Drift Monitoring", "Model Registry"]
    )
    
    # Kafka settings
    st.subheader("📡 Kafka Settings")
    kafka_host = st.text_input("Kafka Bootstrap Servers", value="localhost:9092")
    kafka_topic = st.text_input("Kafka Topic", value="drift-data")
    
    # MLflow settings
    st.subheader("📊 MLflow Settings")
    mlflow_tracking_uri = st.text_input("MLflow Tracking URI", value="sqlite:///mlflow.db")
    
    # Model settings
    st.subheader("🤖 Model Settings")
    model_name = st.text_input("Model Name", value="drift_monitor_model")
    data_path = st.text_input("Data Path", value="data/train.csv")
    
    # Pipeline parameters
    st.subheader("🔧 Pipeline Parameters")
    predictions_count = st.slider("Predictions Count", 100, 5000, 1000)
    monitoring_duration = st.slider("Monitoring Duration (min)", 1, 60, 10)
    retrain_threshold = st.slider("Retrain Threshold", 0.05, 0.5, 0.15, 0.01)

# Main content based on pipeline type
if pipeline_type == "Complete ML Pipeline":
    st.header("🚀 Complete ML Pipeline")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="pipeline-card">
        <h3>Pipeline Steps:</h3>
        <ol>
            <li>📊 Data Loading & Preparation</li>
            <li>🤖 Model Training with MLflow</li>
            <li>📡 Model Deployment to Kafka</li>
            <li>🔄 Real-time Prediction Generation</li>
            <li>🔍 Drift Monitoring</li>
            <li>📄 Report Generation</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Pipeline controls
        if st.button("🚀 Start Complete Pipeline", type="primary"):
            with st.spinner("Running complete ML pipeline..."):
                try:
                    result = complete_ml_pipeline_flow(
                        data_path=data_path,
                        model_name=model_name,
                        predictions_count=predictions_count,
                        drift_monitoring_duration=monitoring_duration
                    )
                    st.session_state.pipeline_running = True
                    st.success("✅ Pipeline completed successfully!")
                    
                    # Display results
                    st.subheader("📊 Pipeline Results")
                    col_metric1, col_metric2, col_metric3 = st.columns(3)
                    
                    with col_metric1:
                        st.metric("Model Accuracy", f"{result['model_info']['accuracy']:.4f}")
                    
                    with col_metric2:
                        st.metric("Predictions Sent", result['predictions_sent'])
                    
                    with col_metric3:
                        st.metric("Drift Events", len(result['drift_results']['drift_events']))
                    
                except Exception as e:
                    st.error(f"❌ Pipeline failed: {e}")
    
    with col2:
        st.subheader("📈 Pipeline Status")
        
        # Pipeline status indicators
        status_col1, status_col2 = st.columns(2)
        
        with status_col1:
            st.metric("Pipeline Status", 
                     "🟢 Running" if st.session_state.pipeline_running else "🔴 Stopped")
        
        with status_col2:
            st.metric("Last Run", datetime.now().strftime("%H:%M:%S"))

elif pipeline_type == "Model Retraining":
    st.header("🔄 Model Retraining Pipeline")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="pipeline-card">
        <h3>Retraining Pipeline:</h3>
        <ul>
            <li>🔍 Check current drift status</li>
            <li>📊 Evaluate if retraining is needed</li>
            <li>🤖 Train new model if drift detected</li>
            <li>📡 Deploy updated model</li>
            <li>📈 Update model registry</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Start Retraining Pipeline", type="primary"):
            with st.spinner("Checking for retraining needs..."):
                try:
                    result = model_retraining_pipeline_flow(
                        retrain_threshold=retrain_threshold,
                        data_path=data_path
                    )
                    
                    if result['retrained']:
                        st.success("✅ Model retraining completed!")
                        st.json(result['new_model_info'])
                    else:
                        st.info(f"ℹ️ {result['reason']}")
                        
                except Exception as e:
                    st.error(f"❌ Retraining failed: {e}")
    
    with col2:
        st.subheader("🔍 Drift Threshold")
        st.metric("Current Threshold", f"{retrain_threshold:.3f}")
        
        # Drift threshold visualization
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=retrain_threshold * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Retrain Threshold (%)"},
            gauge={'axis': {'range': [None, 50]},
                   'bar': {'color': "darkblue"},
                   'steps': [{'range': [0, 10], 'color': "lightgray"},
                            {'range': [10, 25], 'color': "yellow"},
                            {'range': [25, 50], 'color': "red"}]}
        ))
        st.plotly_chart(fig, use_container_width=True)

elif pipeline_type == "Drift Monitoring":
    st.header("🔍 Real-time Drift Monitoring")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Kafka consumer status
        if st.button("📡 Initialize Kafka Consumer"):
            try:
                st.session_state.kafka_consumer = DriftDataConsumer(
                    bootstrap_servers=kafka_host,
                    topic=kafka_topic,
                    group_id="streamlit-drift-monitor"
                )
                st.success("✅ Kafka consumer initialized!")
            except Exception as e:
                st.error(f"❌ Failed to initialize consumer: {e}")
        
        # Consumer controls
        if st.session_state.kafka_consumer:
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("▶️ Start Monitoring"):
                    st.session_state.kafka_consumer.start_background_consuming()
                    st.success("🚀 Drift monitoring started!")
            
            with col_btn2:
                if st.button("⏹️ Stop Monitoring"):
                    st.session_state.kafka_consumer.stop_consuming()
                    st.success("🛑 Drift monitoring stopped!")
            
            # Consumer status
            status = st.session_state.kafka_consumer.get_status()
            
            st.subheader("📊 Consumer Status")
            status_col1, status_col2, status_col3 = st.columns(3)
            
            with status_col1:
                st.metric("Status", "🟢 Running" if status.get('running', False) else "🔴 Stopped")
            
            with status_col2:
                st.metric("Messages", status.get('message_count', 0))
            
            with status_col3:
                st.metric("Window Size", status.get('window_size', 0))
    
    with col2:
        st.subheader("📈 Drift Metrics")
        
        # Simulate drift metrics
        drift_data = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=24, freq='H'),
            'psi_score': [0.05 + 0.1 * i for i in range(24)]
        })
        
        fig = px.line(drift_data, x='timestamp', y='psi_score', 
                     title="PSI Score Over Time")
        fig.add_hline(y=0.1, line_dash="dash", line_color="orange", 
                     annotation_text="Possible Drift")
        fig.add_hline(y=0.25, line_dash="dash", line_color="red", 
                     annotation_text="Likely Drift")
        st.plotly_chart(fig, use_container_width=True)

elif pipeline_type == "Model Registry":
    st.header("📚 Model Registry")
    
    # Model registry operations
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Registered Models")
        
        # List models
        models = st.session_state.model_registry.list_models()
        
        if models:
            for model in models:
                with st.expander(f"🤖 {model['model_name']} v{model['version']}"):
                    col_info1, col_info2 = st.columns(2)
                    
                    with col_info1:
                        st.write(f"**Accuracy:** {model['accuracy']:.4f}")
                        st.write(f"**Type:** {model['model_type']}")
                        st.write(f"**Status:** {model['deployment_status']}")
                    
                    with col_info2:
                        st.write(f"**Features:** {len(model['features'])}")
                        st.write(f"**Training Date:** {model['training_date'][:10]}")
                        if model['drift_score']:
                            st.write(f"**Drift Score:** {model['drift_score']:.4f}")
                    
                    # Model actions
                    col_action1, col_action2, col_action3 = st.columns(3)
                    
                    with col_action1:
                        if st.button(f"🚀 Deploy", key=f"deploy_{model['model_name']}_{model['version']}"):
                            success = st.session_state.model_registry.deploy_model(
                                model['model_name'], model['version']
                            )
                            if success:
                                st.success("✅ Model deployed!")
                            else:
                                st.error("❌ Deployment failed!")
                    
                    with col_action2:
                        if st.button(f"📊 Evaluate", key=f"eval_{model['model_name']}_{model['version']}"):
                            st.info("🔍 Drift evaluation feature coming soon!")
                    
                    with col_action3:
                        if st.button(f"📈 Promote", key=f"promote_{model['model_name']}_{model['version']}"):
                            success = st.session_state.model_registry.promote_model(
                                model['model_name'], model['version']
                            )
                            if success:
                                st.success("✅ Model promoted!")
                            else:
                                st.error("❌ Promotion failed!")
        else:
            st.info("📚 No models registered yet. Run a training pipeline to register models.")
    
    with col2:
        st.subheader("📊 Registry Statistics")
        
        if models:
            # Model statistics
            total_models = len(models)
            deployed_models = len([m for m in models if 'deployed' in m['deployment_status']])
            avg_accuracy = sum(m['accuracy'] for m in models) / len(models)
            
            st.metric("Total Models", total_models)
            st.metric("Deployed Models", deployed_models)
            st.metric("Avg Accuracy", f"{avg_accuracy:.4f}")
            
            # Model type distribution
            model_types = [m['model_type'] for m in models]
            type_counts = pd.Series(model_types).value_counts()
            
            fig = px.pie(values=type_counts.values, names=type_counts.index, 
                        title="Model Types Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 No statistics available yet.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🤖 ML Pipeline with Kafka Integration | Built with Streamlit, Prefect, MLflow & Apache Kafka</p>
</div>
""", unsafe_allow_html=True) 