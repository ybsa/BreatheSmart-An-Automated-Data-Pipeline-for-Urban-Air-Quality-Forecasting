"""
BreatheSmart Prediction Engine
------------------------------
Generates PM2.5 forecasts for the next hour using the trained XGBoost model.

Process:
1. Loads the latest available data from `data/processed/training_data.csv`.
2. Constructs the feature vector for T+1 (next hour).
    - Lags are derived from T, T-1, ...
    - Rolling stats are calculated from T-23 to T.
3. Loads the saved model artifacts.
4. Generates and logs the prediction.

Usage:
    python src/prediction.py

Output:
    data/predictions.csv (appended)
    Console output
"""
import pandas as pd
import xgboost as xgb
import joblib
import os
import logging
from datetime import timedelta
import numpy as np

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("logs", "prediction.log")),
        logging.StreamHandler()
    ]
)

MODEL_PATH = "models/xgboost_pm25.json"
FEATURES_PATH = "models/model_features.pkl"
DATA_PATH = "data/processed/training_data.csv"
PREDICTIONS_PATH = "data/predictions.csv"

def load_artifacts():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(FEATURES_PATH):
        raise FileNotFoundError("Model artifacts not found. Run 03_model_training.py first.")
    
    model = xgb.XGBRegressor()
    model.load_model(MODEL_PATH)
    features = joblib.load(FEATURES_PATH)
    return model, features

def get_latest_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("Processed data not found.")
    
    # We need at least the last 24 rows to calculate features
    df = pd.read_csv(DATA_PATH, parse_dates=['date_utc'], index_col='date_utc')
    return df.tail(48) # Load extra just in case

def predict_next_hour():
    try:
        logging.info("Starting prediction pipeline...")
        
        # 1. Load Resources
        model, feature_names = load_artifacts()
        df = get_latest_data()
        
        if len(df) < 24:
            logging.error("Insufficient data for rolling features (need >= 24 hours).")
            return

        # 2. Prepare Input for T+1
        last_time = df.index[-1]
        next_time = last_time + timedelta(hours=1)
        
        logging.info(f"Latest data point: {last_time}")
        logging.info(f"Forecasting for: {next_time}")
        
        input_data = {}
        
        # Lags
        # Lag 1h for T+1 is the value at T (iloc[-1])
        input_data['pm25_lag_1h'] = df['pm25'].iloc[-1] 
        input_data['pm25_lag_2h'] = df['pm25'].iloc[-2]
        input_data['pm25_lag_3h'] = df['pm25'].iloc[-3]
        input_data['pm25_lag_24h'] = df['pm25'].iloc[-24]
        
        # Rolling Stats
        # Feature 'rolling_mean_24h' for T+1 is calculated using data T-23...T
        # This corresponds to .rolling(24).mean() at index T
        rolling_mean = df['pm25'].rolling(window=24).mean().iloc[-1]
        rolling_std = df['pm25'].rolling(window=24).std().iloc[-1]
        
        input_data['pm25_rolling_mean_24h'] = rolling_mean
        input_data['pm25_rolling_std_24h'] = rolling_std
        
        # Temporal Features for T+1
        input_data['hour'] = next_time.hour
        input_data['day_of_week'] = next_time.dayofweek
        input_data['month'] = next_time.month
        
        # Create DataFrame ensuring correct column order
        X_input = pd.DataFrame([input_data])
        
        # Ensure columns match model features
        # If model expects columns in specific order, reorder them
        missing_feats = set(feature_names) - set(X_input.columns)
        if missing_feats:
            logging.warning(f"Missing features in input: {missing_feats}")
            # If we missed any, fill 0 or handle error. 
            # Based on 02_feature_engineering, we shouldn't miss any if logic matches.
        
        X_input = X_input[feature_names]
        
        # 3. Predict
        prediction = model.predict(X_input)[0]
        prediction = max(0.0, prediction) # PM2.5 cannot be negative
        
        logging.info(f"Predicted PM2.5: {prediction:.2f} µg/m³")
        print(f"Forecast for {next_time}: {prediction:.2f} µg/m³")
        
        # 4. Save Prediction
        result_row = {
            'prediction_date': next_time,
            'predicted_pm25': prediction,
            'generated_at': pd.Timestamp.now()
        }
        
        result_df = pd.DataFrame([result_row])
        
        header = not os.path.exists(PREDICTIONS_PATH)
        result_df.to_csv(PREDICTIONS_PATH, mode='a', header=header, index=False)
        logging.info(f"Prediction saved to {PREDICTIONS_PATH}")
        
    except Exception as e:
        logging.error(f"Prediction failed: {e}")
        # print(e) # Optional: print to stderr

if __name__ == "__main__":
    predict_next_hour()
