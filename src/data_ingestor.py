"""
BreatheSmart Data Ingestor
--------------------------
Production-ready air quality data fetcher from OpenAQ API v2/v3.

This script manages the extraction of pollutant data (PM2.5, PM10, etc.) for a specified city.
It includes:
- Robust error handling and exponential backoff
- Incremental data loading to avoid duplicate fetches
- Resolving location IDs dynamically
- Quality checks and filtering

Usage:
    python src/data_ingestor.py

Output:
    Saves CSV files to data/raw/
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
    PARAMETERS, LOG_FORMAT, LOG_LEVEL, OPENAQ_API_KEY
)

# Setup logging
log_file = LOGS_PATH / f"data_ingestion_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)



def fetch_measurements_for_id(location_id, params, headers, parameter):
    """
    Fetch measurements for a location by first Resolving its Sensors.
    Flow: Location -> Sensors -> Match Parameter -> Fetch Measurements
    """
    # 1. Get Sensors for this location
    sensors_url = f"https://api.openaq.org/v3/locations/{location_id}/sensors"
    try:
        # Use a short timeout for sensor lookup
        resp = requests.get(sensors_url, headers=headers, timeout=10)
        resp.raise_for_status()
        sensors = resp.json().get('results', [])
    except Exception as e:
        logger.warning(f"Failed to fetch sensors for location {location_id}: {e}")
        return pd.DataFrame()

    if not sensors:
        return pd.DataFrame()

    # 2. Find sensor for our target parameter
    target_sensor_id = None
    target_unit = 'µg/m³' # Default
    
    for s in sensors:
        s_param = s.get('parameter', {}).get('name', '').lower()
        if s_param == parameter.lower():
            target_sensor_id = s.get('id')
            target_unit = s.get('parameter', {}).get('units', target_unit)
            break
    
    if not target_sensor_id:
        # logger.debug(f"Location {location_id} has no sensor for {parameter}")
        return pd.DataFrame()

    # 3. Fetch measurements for this sensor
    meas_url = f"https://api.openaq.org/v3/sensors/{target_sensor_id}/measurements"
    
    # Clean params for sensor endpoint (doesn't need location_id etc)
    # v3 limit often capped at 1000
    safe_limit = min(params.get('limit', 1000), 1000)
    sensor_params = {
        "limit": safe_limit,
        "date_from": params.get('date_from'),
        "date_to": params.get('date_to'),
        # "order_by": "datetime" # API v3 default is usually latest, but let's see
    }
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                meas_url,
                params=sensor_params,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                return pd.DataFrame()
            
            # Process results
            processed_rows = []
            for row in results:
                try:
                    # Sensor response structure might be slightly different or same
                    val = row.get('value')
                    if val is None: continue
                    
                    processed_row = {
                        'location': f"Location {location_id}",
                        'parameter': parameter,
                        'value': val,
                        'unit': target_unit,
                        'city': TARGET_CITY
                    }

                    # Extract date from period -> datetimeFrom -> utc
                    period = row.get('period', {})
                    dt_from = period.get('datetimeFrom', {})
                    dt_utc = dt_from.get('utc')
                    
                    if dt_utc:
                        processed_row['date_utc'] = dt_utc
                        processed_row['date_local'] = dt_from.get('local')
                    else:
                        continue # Skip if no date
                    
                    processed_rows.append(processed_row)
                except Exception as e:
                    continue
            
            return pd.DataFrame(processed_rows)

        except Exception as e:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_FACTOR ** attempt)
            else:
                logger.warning(f"Failed to fetch measurements for sensor {target_sensor_id}: {e}")
                return pd.DataFrame()
    return pd.DataFrame()


def fetch_air_quality_data(
    city: str = TARGET_CITY,
    parameter: str = 'pm25',
    limit: int = 1000,
    date_from: str = None,
    date_to: str = None,
    location_ids: list = None
) -> pd.DataFrame:
    """Fetch air quality data handling multiple locations"""
    
    # Setup base params (order, dates, parameter)
    params = {
        "limit": limit,
        "order_by": "datetime"
    }
    
    # Parameter mapping
    param_map = {'pm25': 2, 'pm10': 1, 'no2': 3, 'o3': 5, 'so2': 8, 'co': 7}
    if parameter:
        params['parameters_id'] = param_map.get(parameter.lower(), 2)
    
    if date_from: params['date_from'] = date_from
    if date_to: params['date_to'] = date_to
    
    headers = {}
    if OPENAQ_API_KEY:
        headers['X-API-Key'] = OPENAQ_API_KEY

    all_dfs = []
    
    # If we have specific IDs, loop through them
    if location_ids:
        logger.info(f"🔗 Fetching {parameter.upper()} data for {len(location_ids)} locations in {city}")
        for loc_id in location_ids:
            # logger.debug(f"Fetching location {loc_id}...")
            df = fetch_measurements_for_id(loc_id, params, headers, parameter)
            if not df.empty:
                all_dfs.append(df)
            # Small delay to avoid rate limits
            time.sleep(0.1) 
    else:
        # Legacy/Fallback path if no IDs provided (should not happen with new logic)
        logger.warning("No location IDs provided to fetch_air_quality_data")
        return pd.DataFrame()

    if not all_dfs:
        logger.warning(f"No data returned for {parameter} in {city} across all locations")
        return pd.DataFrame()
        
    # Combine all results
    combined_df = pd.concat(all_dfs, ignore_index=True)
    logger.info(f"Successfully fetched {len(combined_df)} total records")
    
    # Clean and Filter
    if not combined_df.empty and parameter == 'pm25':
        initial_count = len(combined_df)
        combined_df = combined_df[combined_df['value'] <= MAX_PM25_VALUE]
        filtered_count = initial_count - len(combined_df)
        if filtered_count > 0:
            logger.warning(f"Filtered out {filtered_count} records with PM2.5 > {MAX_PM25_VALUE}")

    return combined_df


def get_city_locations(city_name: str = TARGET_CITY) -> list:
    """
    Fetch location IDs for a given city/region
    """
    url = "https://api.openaq.org/v3/locations"
    params = {
        "limit": 100,
        "page": 1,
        "iso": "AE",  # Filter by UAE
    }
    
    headers = {}
    if OPENAQ_API_KEY:
        headers['X-API-Key'] = OPENAQ_API_KEY
    
    logger.info(f"🔎 Searching for locations in {city_name} (UAE)...")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        results = data.get('results', [])
        
        # Filter for city name in location name or other fields
        # Note: v3 'city' field might be nested or named differently, 
        # but searching 'name' is a good start.
        city_locations = []
        for loc in results:
            # Check name or locality
            name = loc.get('name', '').lower()
            locality = loc.get('locality', '').lower() if loc.get('locality') else ''
            
            target = city_name.lower()
            if target in name or target in locality:
                city_locations.append(loc['id'])
        
        # Hardcoded known IDs for Abu Dhabi if search misses them (optional)
        # But for now rely on search.
        # Fallback: if 'Abu Dhabi' not found, maybe return all UAE locations?
        # Let's return what we found.
        
        # Also include some known Abu Dhabi locations if list is empty
        if not city_locations and city_name == "Abu Dhabi":
             # Bida Zayed, Khadeeja School, etc are in AD region
             # Let's assume all AE locations might be relevant if detailed filtering fails?
             # No, better to be specific.
             pass
        
        logger.info(f"✅ Found {len(city_locations)} locations for {city_name}: {city_locations}")
        return city_locations
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch locations: {e}")
        return []



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
        
        # Get location IDs first
        location_ids = get_city_locations(TARGET_CITY)
        
        if not location_ids:
            logger.error(f"❌ No locations found for {TARGET_CITY}. Cannot fetch data.")
            continue

        # Fetch data
        df = fetch_air_quality_data(
            city=TARGET_CITY,
            parameter=parameter,
            limit=10000,
            date_from=date_from,
            date_to=date_to,
            location_ids=location_ids
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
    logger.info("Data ingestion complete!")
    
    return all_results


if __name__ == "__main__":
    # Run the ingestor
    # Set incremental=False for first run to get full historical data
    # Set incremental=True for daily runs to only get new data
    fetch_abu_dhabi_air(days_back=30, incremental=False)
