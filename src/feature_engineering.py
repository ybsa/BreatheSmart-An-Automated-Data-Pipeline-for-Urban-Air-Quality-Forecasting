"""
BreatheSmart Feature Engineering
--------------------------------
Transforms raw air quality data into machine-learning-ready features.

Key operations:
1. Aggregation: Resamples raw data to hourly averages.
2. Imputation: Fills missing values using linear interpolation (limit 6h).
3. Feature Creation:
   - Lag features (1h, 2h, 3h, 24h)
   - Rolling statistics (24h mean/std)
   - Temporal features (hour, day of week, month)
4. Cleaning: Removes rows with missing targets or insufficient history.

Usage:
    python src/feature_engineering.py

Input:
    data/raw/abudhabi_*.csv

Output:
    data/processed/training_data.csv
"""
import pandas as pd
import glob
import os
import logging

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("logs", "feature_engineering.log")),
        logging.StreamHandler()
    ]
)

DATA_RAW_DIR = "data/raw"
DATA_PROCESSED_DIR = "data/processed"
os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)

POLLUTANTS = ['pm25', 'pm10', 'no2', 'o3', 'so2', 'co']

def get_latest_file(pollutant):
    """Finds the latest CSV file for a specific pollutant."""
    search_pattern = os.path.join(DATA_RAW_DIR, f"*_{pollutant}_*.csv")
    files = glob.glob(search_pattern)
    if not files:
        logging.warning(f"No files found for {pollutant}")
        return None
    # Sort by modification time (or filename if strict naming used)
    latest_file = max(files, key=os.path.getctime)
    logging.info(f"Latest file for {pollutant}: {latest_file}")
    return latest_file

def load_and_prep_data():
    merged_df = pd.DataFrame()

    for pollutant in POLLUTANTS:
        file_path = get_latest_file(pollutant)
        if file_path:
            df = pd.read_csv(file_path)
            
            # Ensure correct datetime parsing
            if 'date_utc' in df.columns:
                df['date_utc'] = pd.to_datetime(df['date_utc'], utc=True)
                df = df.set_index('date_utc')
                
                # Keep only the value column and rename it
                # Assuming standard OpenAQ v3 structure where value is in 'value' column
                # But waiting, let's check column names. Based on inspect_data output: 'value' is likely the content
                # let's select just the value and rename
                if 'value' in df.columns:
                    series = df['value'].rename(pollutant)
                    
                    # Deduplicate index if necessary
                    series = series[~series.index.duplicated(keep='first')]

                    if merged_df.empty:
                        merged_df = pd.DataFrame(series)
                    else:
                        merged_df = merged_df.join(series, how='outer')
                else:
                    logging.error(f"'value' column not found in {file_path}")
            else:
                logging.error(f"'date_utc' column not found in {file_path}")
    
    logging.info(f"Merged DataFrame shape: {merged_df.shape}")
    
    return merged_df

def process_data(df):
    if df.empty:
        logging.error("No data to process.")
        return df

    
    logging.info(f"Pre-resample shape: {df.shape}")
    logging.info(f"Pre-resample index type: {df.index.dtype}")
    # 1. Resample to hourly frequency (explicitly checking index)
    try:
        df = df.resample('1h').mean()
    except Exception as e:
        logging.error(f"Resampling failed: {e}")
        return pd.DataFrame() # abort

    logging.info(f"Post-resample shape: {df.shape}")
    logging.info(f"Post-resample head:\n{df.head()}")
    logging.info(f"Post-resample PM2.5 nulls: {df['pm25'].isnull().sum()}")
    
    # 2. Impute missing values
    # Linear interpolation for small gaps (up to 6 hours)
    logging.info("Starting interpolation...")
    df_imputed = df.interpolate(method='linear', limit=6)
    logging.info("Interpolation complete.")
    
    # 2.5 Handle Non-Overlapping Columns
    # If a feature column is entirely NaN for the rows where we have PM2.5, we must drop the COLUMN, not the rows.
    target_col = 'pm25'
    if target_col in df_imputed.columns:
        valid_target_indices = df_imputed[df_imputed[target_col].notnull()].index
        
        cols_to_drop = []
        for col in df_imputed.columns:
            if col == target_col:
                continue
            # Check if this column has ANY valid data in the target's valid range
            # Actually, if we want to use it as a feature, it must be mostly present.
            # strict check: if it's all NaN in the valid target range, drop it.
            subset = df_imputed.loc[valid_target_indices, col]
            if subset.isnull().all():
                logging.warning(f"Column '{col}' has no overlap with {target_col}. Dropping column.")
                cols_to_drop.append(col)
        
        if cols_to_drop:
            df_imputed = df_imputed.drop(columns=cols_to_drop)

    # Filter to rows with valid target
    initial_rows = len(df_imputed)
    df_cleaned = df_imputed.dropna(subset=[target_col])
    dropped_rows = initial_rows - len(df_cleaned)
    if dropped_rows > 0:
        logging.info(f"Dropped {dropped_rows} rows due to missing {target_col} target.")

    # 3. Feature Engineering
    # Lag Features
    for lag in [1, 2, 3, 24]:
        col_name = f'{target_col}_lag_{lag}h'
        df_cleaned[col_name] = df_cleaned[target_col].shift(lag)
    
    # Rolling Statistics
    # Shift by 1 to prevent leakage (value at T should not use data from T)
    df_cleaned[f'{target_col}_rolling_mean_24h'] = df_cleaned[target_col].rolling(window=24).mean().shift(1)
    df_cleaned[f'{target_col}_rolling_std_24h'] = df_cleaned[target_col].rolling(window=24).std().shift(1)
    
    # Temporal Features
    df_cleaned['hour'] = df_cleaned.index.hour
    df_cleaned['day_of_week'] = df_cleaned.index.dayofweek
    df_cleaned['month'] = df_cleaned.index.month
    
    # Final cleanup of NaN created by shifting
    # Now we can safely drop rows that have NaNs in the REMAINING columns
    df_final = df_cleaned.dropna()
    
    return df_final

if __name__ == "__main__":
    logging.info("Starting Feature Engineering...")
    
    raw_df = load_and_prep_data()
    
    if not raw_df.empty:
        logging.info(f"Raw data shape: {raw_df.shape}")
        logging.info(f"Time range: {raw_df.index.min()} to {raw_df.index.max()}")
        
        processed_df = process_data(raw_df)
        
        output_path = os.path.join(DATA_PROCESSED_DIR, "training_data.csv")
        processed_df.to_csv(output_path)
        
        logging.info(f"Processed data shape: {processed_df.shape}")
        logging.info(f"Feature engineering complete. Data saved to {output_path}")
    else:
        logging.error("Failed to aggregate data.")
