import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import config

def test_base_dir_exists():
    assert config.BASE_DIR.exists()
    assert config.BASE_DIR.is_dir()

def test_paths_are_initialized():
    assert isinstance(config.RAW_DATA_PATH, Path)
    assert isinstance(config.PROCESSED_DATA_PATH, Path)
    assert isinstance(config.LOGS_PATH, Path)
    assert isinstance(config.MODELS_PATH, Path)

def test_default_values():
    assert config.TARGET_CITY in ['Abu Dhabi', 'Dubai'] # Depends on .env but usually Abu Dhabi
    assert config.PRIMARY_PARAMETER == 'pm25'
    assert 'pm25' in config.PARAMETERS

def test_directories_created():
    assert config.RAW_DATA_PATH.exists()
    assert config.PROCESSED_DATA_PATH.exists()
    assert config.LOGS_PATH.exists()
    assert config.MODELS_PATH.exists()
