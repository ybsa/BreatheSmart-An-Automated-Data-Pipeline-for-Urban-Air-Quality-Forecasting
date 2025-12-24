import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import config

# Page Config
st.set_page_config(
    page_title="BreatheSmart Dashboard",
    page_icon="🌍",
    layout="wide"
)

# Load Data
@st.cache_data
def load_data():
    # History
    history_path = config.PROCESSED_DATA_PATH / "training_data.csv"
    if history_path.exists():
        df_hist = pd.read_csv(history_path, parse_dates=['date_utc'])
        df_hist = df_hist.sort_values('date_utc')
    else:
        df_hist = pd.DataFrame()

    # Predictions
    preds_path = config.BASE_DIR / "data/predictions.csv"
    if preds_path.exists():
        df_pred = pd.read_csv(preds_path, parse_dates=['prediction_date', 'generated_at'])
        try:
            # Clean up: Latest prediction for each target time
            df_pred = df_pred.sort_values('generated_at').drop_duplicates('prediction_date', keep='last')
            df_pred = df_pred.sort_values('prediction_date')
        except KeyError:
            pass # Handle potential empty or malformed csv
    else:
        df_pred = pd.DataFrame()
        
    return df_hist, df_pred

df_hist, df_pred = load_data()

# Header
st.title("🌍 BreatheSmart Air Quality Dashboard")
st.markdown(f"**City:** {config.TARGET_CITY} | **Parameter:** {config.PRIMARY_PARAMETER.upper()} (µg/m³)")

st.divider()

# Metrics Area
col1, col2, col3, col4 = st.columns(4)

current_val = 0
if not df_hist.empty:
    current_val = df_hist.iloc[-1][config.PRIMARY_PARAMETER]
    last_time = df_hist.iloc[-1]['date_utc']
    
    col1.metric(
        "Current Level", 
        f"{current_val:.1f} µg/m³", 
        f"Last Updated: {last_time.strftime('%H:%M')}"
    )

next_forecast = 0
if not df_pred.empty and not df_hist.empty:
    # Ensure comparisons are timezone-aware if needed, but assuming UTC for simplicity in this dataset
    # Filter for future predictions
    latest_hist = df_hist.iloc[-1]['date_utc']
    future_preds = df_pred[df_pred['prediction_date'] > latest_hist]
    
    if not future_preds.empty:
        next_forecast = future_preds.iloc[0]['predicted_pm25']
        delta = next_forecast - current_val
        
        col2.metric(
            "Next Forecast (1h)", 
            f"{next_forecast:.1f} µg/m³", 
            f"{delta:+.1f} vs Current",
            delta_color="inverse"
        )
    else:
        col2.metric("Next Forecast", "Waiting for data...")
else:
    col2.metric("Next Forecast", "No Data")

# Status Logic
def get_aqi_status(pm25):
    if pm25 <= 12: return "Good", "✅" 
    elif pm25 <= 35.4: return "Moderate", "⚠️"
    elif pm25 <= 55.4: return "Unhealthy for Sensitive Groups", "🟠"
    elif pm25 <= 150.4: return "Unhealthy", "🔴"
    elif pm25 <= 250.4: return "Very Unhealthy", "🟣"
    else: return "Hazardous", "☠️"

status_text, icon = get_aqi_status(current_val)
col3.metric("Air Quality Status", status_text)
col4.metric("Status Icon", icon)

st.divider()

# Master Chart
st.subheader("📈 Trends & Forecast")

if not df_hist.empty:
    # View Window: Last 7 days to Future
    view_start = df_hist['date_utc'].max() - pd.Timedelta(days=7)
    chart_hist = df_hist[df_hist['date_utc'] >= view_start]
    
    fig = go.Figure()
    
    # Historical Line
    fig.add_trace(go.Scatter(
        x=chart_hist['date_utc'], 
        y=chart_hist[config.PRIMARY_PARAMETER],
        mode='lines',
        name='Observed',
        line=dict(color='#2ecc71', width=2),
        fill='tozeroy',
        fillcolor='rgba(46, 204, 113, 0.1)'
    ))
    
    # Prediction Scatter/Line
    if not df_pred.empty:
        # Filter relevant predictions
        chart_pred = df_pred[df_pred['prediction_date'] >= view_start]
        
        fig.add_trace(go.Scatter(
            x=chart_pred['prediction_date'],
            y=chart_pred['predicted_pm25'],
            mode='lines+markers',
            name='Forecast',
            line=dict(color='#e74c3c', width=2, dash='dash'),
            marker=dict(symbol='circle', size=6)
        ))
        
    fig.update_layout(
        xaxis_title="Time (UTC)",
        yaxis_title="PM2.5 (µg/m³)",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=0, r=0, t=10, b=0),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No historical data available. Run the data ingestor first.")

# Data Tables
col_hist, col_pred = st.columns(2)

with col_hist:
    st.subheader("📜 Recent History")
    if not df_hist.empty:
        st.dataframe(
            df_hist[['pm25', 'pm10', 'no2', 'o3']].iloc[::-1].style.format("{:.1f}"), 
            use_container_width=True,
            height=300
        )

with col_pred:
    st.subheader("🔮 Forecast Log")
    if not df_pred.empty:
        st.dataframe(
            df_pred[['prediction_date', 'predicted_pm25', 'generated_at']].sort_values('prediction_date', ascending=False),
            use_container_width=True,
            height=300
        )
