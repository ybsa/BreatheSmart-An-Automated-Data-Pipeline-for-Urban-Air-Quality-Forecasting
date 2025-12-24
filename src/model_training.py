"""
BreatheSmart Model Training
---------------------------
Trains an XGBoost Regressor to predict PM2.5 levels.

Methodology:
- Loads processed training data.
- Splits data into Train (80%) and Test (20%) sets employing Time Series Split.
- Trains an XGBoost model with early stopping.
- Evaluates performance using RMSE, MAE, and R2.
- Saves the model and feature list for the prediction service.

Usage:
    python src/model_training.py

Input:
    data/processed/training_data.csv

Output:
    models/xgboost_pm25.json
    models/model_features.pkl
"""
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
import os
import joblib
import logging

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("logs", "model_training.log")),
        logging.StreamHandler()
    ]
)

DATA_PATH = "data/processed/training_data.csv"
MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODELS_DIR, "xgboost_pm25.json")

def load_data(filepath):
    if not os.path.exists(filepath):
        logging.error(f"Data file not found: {filepath}")
        raise FileNotFoundError(f"Data file not found: {filepath}")
    
    df = pd.read_csv(filepath, parse_dates=['date_utc'], index_col='date_utc')
    logging.info(f"Loaded data shape: {df.shape}")
    return df

def train_model():
    try:
        logging.info("Loading processed data...")
        df = load_data(DATA_PATH)
        
        # Define features and target
        target = 'pm25'
        features = [col for col in df.columns if col != target]
        
        logging.info(f"Features: {features}")
        
        X = df[features]
        y = df[target]
        
        # Time Series Split (No random shuffle!)
        # Train on first 80%, Test on last 20%
        split_idx = int(len(df) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        logging.info(f"Training set: {X_train.index.min()} to {X_train.index.max()} ({len(X_train)} samples)")
        logging.info(f"Test set: {X_test.index.min()} to {X_test.index.max()} ({len(X_test)} samples)")
        
        # XGBoost Regressor
        logging.info("Initializing and training XGBoost model...")
        model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=1000,
            learning_rate=0.05,
            max_depth=6,
            early_stopping_rounds=50,
            n_jobs=-1,
            random_state=42
        )
        
        model.fit(
            X_train, y_train,
            eval_set=[(X_train, y_train), (X_test, y_test)],
            verbose=100
        )
        
        # Evaluation
        logging.info("Evaluating model...")
        predictions = model.predict(X_test)
        
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        logging.info(f"Test RMSE: {rmse:.4f}")
        logging.info(f"Test MAE: {mae:.4f}")
        logging.info(f"Test R2 Score: {r2:.4f}")
        
        # Save Model
        logging.info(f"Saving model to {MODEL_PATH}...")
        model.save_model(MODEL_PATH)
        # Also save feature names for later use
        joblib.dump(features, os.path.join(MODELS_DIR, "model_features.pkl"))
        
        logging.info("Model training completed successfully.")
        
    except Exception as e:
        logging.error(f"Training failed: {e}")
        raise

if __name__ == "__main__":
    train_model()
