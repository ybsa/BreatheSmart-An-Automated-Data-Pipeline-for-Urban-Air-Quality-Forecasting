"""
BreatheSmart Data Visualization
-------------------------------
Generates a visualization of recent PM2.5 trends and forecast points.

Usage:
    python src/visualization.py

Output:
    reports/pm25_trend_forecast.png
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data/processed/training_data.csv"
PREDS_PATH = BASE_DIR / "data/predictions.csv"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

def plot_trends():
    print("🎨 Generating visualization...")
    
    # 1. Load Historical Data
    if not DATA_PATH.exists():
        print("❌ Training data not found.")
        return

    df = pd.read_csv(DATA_PATH, parse_dates=['date_utc'], index_col='date_utc')
    
    # Plot last 7 days of data
    last_date = df.index.max()
    start_date = last_date - pd.Timedelta(days=7)
    recent_df = df[df.index >= start_date]

    if recent_df.empty:
        print("⚠️ Not enough data to plot history.")
        return

    # 2. Load Predictions
    preds_df = pd.DataFrame()
    if PREDS_PATH.exists():
        preds_df = pd.read_csv(PREDS_PATH, parse_dates=['prediction_date'])

    # 3. Create Plot
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="darkgrid")

    # Plot History
    plt.plot(recent_df.index, recent_df['pm25'], label='Actual PM2.5', color='#2ecc71', linewidth=2)

    # Plot Predictions
    if not preds_df.empty:
        # Filter predictions that are relevant (e.g., future or recent)
        # For visualization, we just plot all of them that are within the view or future
        # Since predictions might be in the future relative to training data, we ensure x-axis covers it.
        
        # We only want to plot the LATEST prediction for any given timestamp to avoid clutter if multiple runs happened
        latest_preds = preds_df.sort_values('generated_at').drop_duplicates('prediction_date', keep='last')
        
        plt.scatter(latest_preds['prediction_date'], latest_preds['predicted_pm25'], 
                    color='#e74c3c', s=100, label='Forecast', zorder=5, marker='X')
        
    plt.title('Abu Dhabi Air Quality: PM2.5 Trends & Forecast (Last 7 Days)', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('PM2.5 Concentration (µg/m³)', fontsize=12)
    plt.legend()
    plt.tight_layout()

    # 4. Save
    output_path = REPORTS_DIR / "pm25_trend_forecast.png"
    plt.savefig(output_path)
    print(f"✅ Visualization saved to: {output_path}")

if __name__ == "__main__":
    plot_trends()
