import pytest
import pandas as pd
import sys
import os
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import model_training

def test_load_data_valid(sample_processed_data, tmp_path):
    """Test loading data for training"""
    file_path = tmp_path / "training_data.csv"
    sample_processed_data.to_csv(file_path)
    
    df = model_training.load_data(str(file_path))
    assert not df.empty
    assert 'pm25' in df.columns
    assert isinstance(df.index, pd.DatetimeIndex)

def test_load_data_missing():
    """Test error when data file is missing"""
    with pytest.raises(FileNotFoundError):
        model_training.load_data("non_existent.csv")
