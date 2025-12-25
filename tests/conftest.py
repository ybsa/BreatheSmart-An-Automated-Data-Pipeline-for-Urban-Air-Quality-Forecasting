import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

@pytest.fixture
def sample_raw_data():
    """Provides a sample raw dataframe similar to OpenAQ output"""
    dates = pd.date_range(end=datetime.now(), periods=10, freq='H')
    df = pd.DataFrame({
        'date_utc': dates,
        'value': np.random.uniform(5, 50, size=10),
        'parameter': ['pm25'] * 10,
        'location': ['Test Station'] * 10,
        'unit': ['µg/m³'] * 10,
        'latitude': [24.45] * 10,
        'longitude': [54.37] * 10
    })
    return df

@pytest.fixture
def sample_processed_data():
    """Provides a sample processed dataframe for training tests"""
    dates = pd.date_range(end=datetime.now(), periods=100, freq='H')
    df = pd.DataFrame({
        'pm25': np.random.uniform(5, 50, size=100),
        'pm10': np.random.uniform(10, 80, size=100),
        'no2': np.random.uniform(0, 30, size=100),
        'o3': np.random.uniform(0, 100, size=100),
        'hour': range(100),
        'day_of_week': [d.dayofweek for d in dates]
    }, index=dates)
    df.index.name = 'date_utc'
    return df

@pytest.fixture
def test_dirs(tmp_path):
    """Creates temporary directories for testing file operations"""
    data_dir = tmp_path / "data"
    raw_dir = data_dir / "raw"
    proc_dir = data_dir / "processed"
    models_dir = tmp_path / "models"
    
    raw_dir.mkdir(parents=True)
    proc_dir.mkdir(parents=True)
    models_dir.mkdir(parents=True)
    
    return {
        "base": tmp_path,
        "raw": raw_dir,
        "processed": proc_dir,
        "models": models_dir
    }
