import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os
from streamlit_autorefresh import st_autorefresh

#  Import the flow function
from flows.psi_drift_detection_flow import psi_drift_detection_flow

LOG_PATH = "logs/psi_drift_log.csv"

# Streamlit page config
st.set_page_config(page_title="Drift Monitoring Dashboard", layout="wide")
st.title("📊 PSI Drift Monitoring Dashboard")

# Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, limit=None, key="auto_refresh")

# Run PSI Drift Check on button click
if st.button("🔄 Run PSI Drift Check Now"):
    with st.spinner("Running PSI drift detection..."):
        psi_drift_detection_flow()
        st.success("Drift check complete!")
        st.experimental_rerun()

# Load and display PSI log if available
if os.path.exists(LOG_PATH):
    try:
        df = pd.read_csv(LOG_PATH)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['rolling_avg'] = df['psi_score'].rolling(window=7).mean()

        #  Summary panel with latest result
        latest = df.sort_values(by='timestamp', ascending=False).iloc[0]
        st.subheader("🧾 Latest Drift Check Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("📈 PSI Score", f"{latest['psi_score']:.3f}")
        col2.metric("⚠️ Drift Status", latest['drift_status'])
        col3.metric("🕒 Timestamp", latest['timestamp'].strftime("%Y-%m-%d %H:%M:%S"))

        # 📊 PSI Chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['psi_score'],
            mode='lines+markers',
            name='PSI Score',
            line=dict(color='blue'),
            marker=dict(size=6)
        ))

        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['rolling_avg'],
            mode='lines',
            name='7-Point Rolling Avg',
            line=dict(color='green', dash='dot')
        ))

        fig.add_hline(
            y=0.1,
            line=dict(color='orange', dash='dash'),
            annotation_text="Possible Drift (0.1)",
            annotation_position="top left"
        )
        fig.add_hline(
            y=0.25,
            line=dict(color='red', dash='dash'),
            annotation_text="Likely Drift (0.25)",
            annotation_position="top left"
        )

        fig.update_layout(
            title="PSI Score Over Time",
            xaxis_title="Timestamp",
            yaxis_title="PSI Score",
            height=500,
        )

        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df.sort_values(by='timestamp', ascending=False), use_container_width=True)

    except pd.errors.EmptyDataError:
        st.warning("Drift log exists but is empty. Run the flow to generate data.")
    except Exception as e:
        st.error(f"An error occurred while loading the log: {e}")
else:
    st.warning("No drift log file found. Please run the detection flow first.")
