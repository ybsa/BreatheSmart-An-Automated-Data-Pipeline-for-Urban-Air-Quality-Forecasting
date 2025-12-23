import pandas as pd
from glob import glob
import os

files = glob("data/raw/abudhabi_pm25_*.csv")
if files:
    latest = max(files, key=os.path.getctime)
    df = pd.read_csv(latest)
    print(f"File: {latest}")
    print(f"Shape: {df.shape}")
    print("Unique Locations:", df['location'].unique())
    print("Sample Data:")
    print(df.head())
else:
    print("No PM2.5 files found")
