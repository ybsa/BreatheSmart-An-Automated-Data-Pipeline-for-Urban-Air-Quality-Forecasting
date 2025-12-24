"""
Configuration management for BreatheSmart Air Quality System
Loads environment variables and provides centralized config access
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project Paths
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_PATH = BASE_DIR / os.getenv('RAW_DATA_PATH', 'data/raw')
PROCESSED_DATA_PATH = BASE_DIR / os.getenv('PROCESSED_DATA_PATH', 'data/processed')
LOGS_PATH = BASE_DIR / os.getenv('LOGS_PATH', 'logs')
MODELS_PATH = BASE_DIR / os.getenv('MODELS_PATH', 'models')

# Ensure directories exist
for path in [RAW_DATA_PATH, PROCESSED_DATA_PATH, LOGS_PATH, MODELS_PATH]:
    path.mkdir(parents=True, exist_ok=True)

# API Configuration
OPENAQ_API_V2_URL = "https://api.openaq.org/v2/measurements"
OPENAQ_API_V3_URL = "https://api.openaq.org/v3/measurements"
OPENAQ_API_KEY = os.getenv('OPENAQ_API_KEY', None)  # v2 doesn't need key

# Target Location
TARGET_CITY = os.getenv('TARGET_CITY', 'Abu Dhabi')

# Data Quality Parameters
MAX_PM25_VALUE = int(os.getenv('MAX_PM25_VALUE', 500))
MIN_RECORDS_PER_DAY = int(os.getenv('MIN_RECORDS_PER_DAY', 10))

# API Rate Limiting
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2  # Exponential backoff: 2, 4, 8 seconds
REQUEST_TIMEOUT = 30  # seconds

# Pollutant Parameters to track
PARAMETERS = ['pm25', 'pm10', 'no2', 'o3', 'so2', 'co']
PRIMARY_PARAMETER = 'pm25'  # Main focus for prediction

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
