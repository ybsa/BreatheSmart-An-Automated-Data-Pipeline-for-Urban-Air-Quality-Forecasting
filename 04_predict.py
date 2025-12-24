import pandas as pd
import xgboost as xgb
import joblib
import os
import logging
from datetime import timedelta

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
    return df.tail(30) # Load extra just in case

def prepare_input(df, feature_names):
    last_row = df.iloc[-1]
    last_time = df.index[-1]
    next_time = last_time + timedelta(hours=1)
    
    # Calculate features for next_time
    input_data = {}
    
    # 1. Target Lags (The lag_1h for T+1 is the value at T, etc.)
    input_data['pm25_lag_1h'] = df.iloc[-1]['pm25']
    input_data['pm25_lag_2h'] = df.iloc[-2]['pm25']
    input_data['pm25_lag_3h'] = df.iloc[-3]['pm25']
    input_data['pm25_lag_24h'] = df.iloc[-24]['pm25']
    
    # 2. Rolling Stats (Rolling window ending at T is the input for T+1's prediction context? 
    # Actually, we need to be careful with definition.
    # In training: rolling_mean at T is calculated from T-23 to T.
    # So for predicting T+1, we need rolling mean from T-22 to T+1? No, we don't have T+1.
    # Usually, we use the rolling stats *available at decision time*.
    # Let's assume standard autoregressive: features at T are used to predict T.
    # Wait, in feature engineering we did: df['pm25_lag_1h'] = df['pm25'].shift(1)
    # So at row T, 'pm25_lag_1h' is value at T-1.
    # And we train to predict Value at T using Lag variable (T-1).
    # So to predict T+1, we need input features corresponding to T+1.
    # For T+1, 'pm25_lag_1h' should be value at T.
    
    # Rolling mean: In training: df['rolling'] = df['pm25'].rolling(24).mean()
    # At row T, this includes value at T.
    # This is a "leakage" if we use it to predict T!
    # Let's check 02_feature_engineering.py
    # df['pm25_rolling_mean_24h'] = df['pm25'].rolling(window=24).mean()
    # YES. This includes current time T. 
    # If we are effectively predicting T, we cannot use feature calculated from T.
    # BUT, did we shift the rolling features? 
    # Inspecting 02_feature_engineering.py:
    # We did NOT shift rolling features. 
    # This means `pm25_rolling_mean_24h` at row T contains info from T.
    # If we used this to predict T (target is `pm25` column), then the model learned Identity mapping!
    # CHECK THIS. 
    
    # If the model learned Identity, then RMSE would be 0.
    # Our RMSE was 2.8. So it's not perfect identity.
    # Ah, `rolling(24).mean()` includes T. So `pm25` is 1/24th of the feature.
    # This is still leakage. 
    # Ideally, we should have shifted rolling features too.
    
    # CORRECT FIX for Prediction:
    # If we want to be consistent with how we trained (even if it was slightly leaky), 
    # we must construct the feature exactly as we did in training.
    # Feature inputs for predicting T+1:
    # We need "feature set at T+1".
    # `pm25_lag_1h` at T+1 = Value at T.
    # `pm25_rolling_mean_24h` at T+1 = Mean(T-22...T+1). We don't have T+1.
    # This confirms the previous script might have had leakage issues for rolling features, 
    # OR we intended to predict T using T's rolling mean (which implies we know T... circular).
    
    # WAIT. Standard practice:
    # Features at row T are "Past info".
    # Target at row T is "Future info".
    # In my script 02: 
    # df['pm25_lag_1h'] = shift(1). Correct, relies on T-1.
    # df['pm25_rolling_mean_24h'] = rolling(24).mean(). Relies on T.
    
    # If I train X=Rolling(T), y=PM2.5(T)... leakage!
    # I should have done: rolling().shift(1).
    
    # CRITICAL DECISION:
    # 1. Retrain model with corrected features (Shift rolling features).
    # 2. Proceed (but know results are artificially good on test set, but impossible to create for future without guessing).
    
    # Since we are "completing fast", I might have to hack this:
    # To predict T+1, I *need* Rolling Mean at T+1.
    # Rolling Mean at T+1 requires value at T+1 (unknown).
    # I can use Rolling Mean at T (shifted) as a proxy, OR...
    # The only valid way is to fix the training.
    
    # Let's Fix Training quickly in Phase 5 implicitly? 
    # Or just admit the leakage and fix 02_feature_engineering.py first?
    # Fixing 02 is safer.
    
    pass 
