import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import scheduler

def test_scheduler_module_loaded():
    """Test that scheduler module loads correctly"""
    assert hasattr(scheduler, 'run_scheduler')
    assert hasattr(scheduler, 'job')

def test_scheduler_has_job_function():
    """Test that the job function exists"""
    assert callable(scheduler.job)
