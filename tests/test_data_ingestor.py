import pytest
import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import data_ingestor
import config

def test_save_data(sample_raw_data, tmp_path):
    """Test that data is correctly saved to CSV"""
    with patch.object(config, 'RAW_DATA_PATH', tmp_path):
        filepath = data_ingestor.save_data(sample_raw_data, 'test_param')
        assert filepath is not None
        assert Path(filepath).exists()
        
        # Verify content
        saved_df = pd.read_csv(filepath)
        assert len(saved_df) == len(sample_raw_data)
        assert 'value' in saved_df.columns

def test_get_last_ingestion_date_no_files(tmp_path):
    """Test last ingestion date when no files exist returns a past date"""
    with patch.object(config, 'RAW_DATA_PATH', tmp_path):
        last_date = data_ingestor.get_last_ingestion_date('pm25')
        # Should return a datetime-like object in the past
        assert last_date is not None
        # The date should be in the past (before now)
        now = pd.Timestamp.now(tz='UTC') if hasattr(last_date, 'tzinfo') and last_date.tzinfo else datetime.now()
        assert last_date < now

def test_get_city_locations_callable():
    """Test that get_city_locations function exists and is callable"""
    assert callable(data_ingestor.get_city_locations)

def test_fetch_air_quality_data_callable():
    """Test that fetch_air_quality_data function exists and is callable"""
    assert callable(data_ingestor.fetch_air_quality_data)
