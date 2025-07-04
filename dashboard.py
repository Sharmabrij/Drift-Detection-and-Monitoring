import pandas as pd
import plotly.express as px
import streamlit as st
import os

LOG_PATH = "logs/psi_drift_log.csv"

st.set_page_config(page_title="PSI Drift Dashboard", layout="wide")

st.title("📊 PSI Drift Monitoring Dashboard")

# Check if log file exists
if not os.path.exists(LOG_PATH):
    st.warning("No PSI log file found.")
else:
    df = pd.read_csv(LOG_PATH)

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Show latest drift status
    latest = df.iloc[-1]
    st.metric(label="Latest PSI Score", value=latest["psi_score"], delta=latest["drift_status"])

    # Plot
    fig = px.line(
        df,
        x='timestamp',
        y='psi_score',
        color='drift_status',
        markers=True,
        title="PSI Score Over Time",
        color_discrete_map={
            "No Drift": "green",
            "Possible Drift": "orange",
            "Likely Drift": "red"
        }
    )

fig.add_hline(y=0.1, line_dash="dash", line_color="orange", annotation_text="0.1 - Possible Drift", annotation_position="top left")
fig.add_hline(y=0.25, line_dash="dash", line_color="red", annotation_text="0.25 - Likely Drift", annotation_position="top left")

fig.update_layout(height=500, xaxis_title="Time", yaxis_title="PSI Score")
st.plotly_chart(fig, use_container_width=True)

    # # Optional table view
    # with st.expander("See Log Data"):
    #     st.dataframe(df[::-1], use_container_width=True)
