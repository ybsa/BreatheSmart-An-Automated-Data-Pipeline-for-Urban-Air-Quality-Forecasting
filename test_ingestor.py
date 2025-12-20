"""
Quick test script to verify the data ingestor setup
This runs a minimal data fetch to test the pipeline
"""
import sys
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, '.')

from data_ingestor import fetch_air_quality_data, save_data
from config import TARGET_CITY

def test_ingestor():
    """
    Run a quick test with minimal data
    """
    print("=" * 80)
    print("🧪 Testing BreatheSmart Data Ingestor")
    print("=" * 80)
    
    # Fetch just 2 days of PM2.5 data
    date_from = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    date_to = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n📅 Fetching PM2.5 data for {TARGET_CITY}")
    print(f"Date range: {date_from} to {date_to}")
    
    df = fetch_air_quality_data(
        city=TARGET_CITY,
        parameter='pm25',
        limit=100,
        date_from=date_from,
        date_to=date_to
    )
    
    if df.empty:
        print("\n❌ TEST FAILED: No data retrieved")
        return False
    
    print(f"\n✅ Retrieved {len(df)} records")
    print(f"\nSample data:")
    print(df.head())
    
    print(f"\n📊 Data summary:")
    print(f"  - Locations: {df['location'].nunique()}")
    print(f"  - Date range: {df['date_utc'].min()} to {df['date_utc'].max()}")
    print(f"  - PM2.5 range: {df['value'].min():.1f} - {df['value'].max():.1f} {df['unit'].iloc[0]}")
    
    # Save test data
    filepath = save_data(df, 'pm25_test')
    
    if filepath:
        print(f"\n💾 Test data saved to: {filepath}")
        print("\n✅ TEST PASSED: Data ingestor is working correctly!")
        return True
    else:
        print("\n❌ TEST FAILED: Could not save data")
        return False

if __name__ == "__main__":
    success = test_ingestor()
    sys.exit(0 if success else 1)
