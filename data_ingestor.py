"""
BreatheSmart Data Ingestor
Production-ready air quality data fetcher from OpenAQ API v2

This script fetches PM2.5 and other pollutant data for Abu Dhabi
with robust error handling, retry logic, and incremental loading.

Author: BreatheSmart Team
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
import time
import sys

# Import our config
from config import (
    OPENAQ_API_V2_URL, TARGET_CITY, RAW_DATA_PATH, LOGS_PATH,
    MAX_PM25_VALUE, MAX_RETRIES, RETRY_BACKOFF_FACTOR, REQUEST_TIMEOUT,
    PARAMETERS, LOG_FORMAT, LOG_LEVEL
)

# Setup logging
log_file = LOGS_PATH / f"data_ingestion_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def fetch_air_quality_data(
    city: str = TARGET_CITY,
    parameter: str = 'pm25',
    limit: int = 1000,
    date_from: str = None,
    date_to: str = None
) -> pd.DataFrame:
    """
    Fetch air quality data from OpenAQ API v3 with retry logic
    
    Args:
        city: Target city name (default: Abu Dhabi)
        parameter: Pollutant parameter (pm25, pm10, no2, etc.)
        limit: Max number of records to fetch per request
        date_from: Start date in ISO format (YYYY-MM-DD)
        date_to: End date in ISO format (YYYY-MM-DD)
    
    Returns:
        pandas DataFrame with air quality measurements
    """
    # v3 API uses different parameter format
    params = {
        "limit": limit,
        "order_by": "datetime"
    }
    
    # v3 uses 'locations_name' instead of 'city'
    if city:
        params['locations_name'] = city
    
    # v3 uses 'parameters_id' instead of 'parameter'
    if parameter:
        # Parameter IDs in v3: pm25=2, pm10=1, no2=3, o3=5, so2=8, co=7
        param_map = {'pm25': 2, 'pm10': 1, 'no2': 3, 'o3': 5, 'so2': 8, 'co': 7}
        params['parameters_id'] = param_map.get(parameter.lower(), 2)
    
    if date_from:
        params['date_from'] = date_from
    if date_to:
        params['date_to'] = date_to
    
    logger.info(f"🔗 Fetching {parameter.upper()} data for {city}")
    logger.debug(f"Request params: {params}")
    
    # v3 API URL
    url = "https://api.openaq.org/v3/measurements"
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # v3 requires API key in header (but may work without for basic usage)
            headers = {}
            if OPENAQ_API_KEY:
                headers['X-API-Key'] = OPENAQ_API_KEY
            
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' not in data:
                logger.error(f"Unexpected API response format: {data}")
                return pd.DataFrame()
            
            results = data['results']
            
            if not results:
                logger.warning(f"No data returned for {parameter} in {city}")
                return pd.DataFrame()
            
            logger.info(f"✅ Successfully fetched {len(results)} records (Attempt {attempt})")
            
            # Convert to DataFrame
            df = pd.DataFrame(results)
            
            # Parse v3 response structure
            # v3 has different structure than v2
            processed_rows = []
            for idx, row in df.iterrows():
                try:
                    processed_row = {
                        'location': row.get('location', {}).get('name', 'Unknown'),
                        'parameter': parameter,
                        'value': row.get('value'),
                        'unit': row.get('parameter', {}).get('units') if isinstance(row.get('parameter'), dict) else 'µg/m³',
                        'date_utc': pd.to_datetime(row.get('datetime')),
                        'city': city
                    }
                    processed_rows.append(processed_row)
                except Exception as e:
                    logger.warning(f"Skipping row {idx} due to parsing error: {e}")
                    continue
            
            df = pd.DataFrame(processed_rows)
            
            if df.empty:
                logger.warning("No valid data after processing")
                return pd.DataFrame()
            
            # Data quality filtering
            if parameter == 'pm25':
                initial_count = len(df)
                df = df[df['value'] <= MAX_PM25_VALUE]
                filtered_count = initial_count - len(df)
                if filtered_count > 0:
                    logger.warning(f"Filtered out {filtered_count} records with PM2.5 > {MAX_PM25_VALUE}")
            
            return df
            
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️ Request timeout (Attempt {attempt}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES:
                wait_time = RETRY_BACKOFF_FACTOR ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP Error: {e}")
            logger.error(f"Response body: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            if e.response.status_code == 429:  # Rate limit
                logger.warning("Rate limit exceeded. Waiting 60 seconds...")
                time.sleep(60)
            elif e.response.status_code == 410:  # Gone - deprecated API
                logger.error("⚠️  API endpoint deprecated. Please ensure using v3 endpoints.")
                break
            elif e.response.status_code >= 500:  # Server error
                if attempt < MAX_RETRIES:
                    wait_time = RETRY_BACKOFF_FACTOR ** attempt
                    logger.info(f"Server error. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
            else:
                break  # Don't retry for client errors
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request failed: {e}")
            if attempt < MAX_RETRIES:
                wait_time = RETRY_BACKOFF_FACTOR ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            break
    
    logger.error(f"Failed to fetch data after {MAX_RETRIES} attempts")
    return pd.DataFrame()



def get_last_ingestion_date(parameter: str = 'pm25') -> datetime:
    """
    Find the most recent date in existing data files for incremental loading
    
    Args:
        parameter: Pollutant parameter to check
    
    Returns:
        datetime of last ingestion, or 7 days ago if no data exists
    """
    pattern = f"abudhabi_{parameter}_*.csv"
    existing_files = list(RAW_DATA_PATH.glob(pattern))
    
    if not existing_files:
        # Default to 7 days ago if no data exists
        last_date = datetime.now() - timedelta(days=7)
        logger.info(f"No existing data found. Starting from {last_date.strftime('%Y-%m-%d')}")
        return last_date
    
    # Read the most recent file
    latest_file = max(existing_files, key=lambda x: x.stat().st_mtime)
    try:
        df = pd.read_csv(latest_file)
        if 'date_utc' in df.columns and len(df) > 0:
            df['date_utc'] = pd.to_datetime(df['date_utc'])
            last_date = df['date_utc'].max()
            logger.info(f"Last ingestion date: {last_date}")
            return last_date
    except Exception as e:
        logger.warning(f"Could not read last date from {latest_file}: {e}")
    
    return datetime.now() - timedelta(days=7)


def save_data(df: pd.DataFrame, parameter: str = 'pm25') -> str:
    """
    Save DataFrame to CSV with timestamp
    
    Args:
        df: DataFrame to save
        parameter: Pollutant parameter name
    
    Returns:
        Path to saved file
    """
    if df.empty:
        logger.warning("No data to save")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = RAW_DATA_PATH / f"abudhabi_{parameter}_{timestamp}.csv"
    
    try:
        df.to_csv(filename, index=False)
        logger.info(f"💾 Saved {len(df)} rows to {filename}")
        return str(filename)
    except Exception as e:
        logger.error(f"❌ Failed to save data: {e}")
        return None


def fetch_abu_dhabi_air(days_back: int = 7, incremental: bool = True):
    """
    Main orchestrator function - fetches data for all parameters
    
    Args:
        days_back: Number of days to fetch (if not incremental)
        incremental: If True, only fetch data since last ingestion
    """
    logger.info("=" * 80)
    logger.info("🌍 BreatheSmart Data Ingestion Started")
    logger.info(f"Target City: {TARGET_CITY}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    all_results = {}
    
    for parameter in PARAMETERS:
        logger.info(f"\n📊 Processing parameter: {parameter.upper()}")
        
        # Determine date range
        if incremental:
            last_date = get_last_ingestion_date(parameter)
            date_from = last_date.strftime('%Y-%m-%d')
            date_to = datetime.now().strftime('%Y-%m-%d')
        else:
            date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            date_to = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Date range: {date_from} to {date_to}")
        
        # Fetch data
        df = fetch_air_quality_data(
            city=TARGET_CITY,
            parameter=parameter,
            limit=10000,  # Fetch more records
            date_from=date_from,
            date_to=date_to
        )
        
        # Save data
        if not df.empty:
            saved_path = save_data(df, parameter)
            all_results[parameter] = {
                'records': len(df),
                'file': saved_path,
                'date_range': f"{df['date_utc'].min()} to {df['date_utc'].max()}"
            }
        else:
            all_results[parameter] = {'records': 0, 'file': None}
        
        # Be nice to the API - small delay between requests
        time.sleep(1)
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("📈 INGESTION SUMMARY")
    logger.info("=" * 80)
    for param, result in all_results.items():
        logger.info(f"{param.upper()}: {result['records']} records")
        if result['file']:
            logger.info(f"  → File: {result['file']}")
    logger.info("=" * 80)
    logger.info("✅ Data ingestion complete!")
    
    return all_results


if __name__ == "__main__":
    # Run the ingestor
    # Set incremental=False for first run to get full historical data
    # Set incremental=True for daily runs to only get new data
    fetch_abu_dhabi_air(days_back=30, incremental=False)
