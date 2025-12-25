"""
MLflow Experiment Tracking Integration
--------------------------------------
Provides utilities for tracking model training experiments, logging metrics,
and managing model versions.

Usage:
    from mlflow_tracking import start_experiment, log_model_metrics

Setup:
    pip install mlflow
    mlflow ui  # Start local tracking server at http://localhost:5000
"""
import os
import logging
from datetime import datetime
from pathlib import Path

# Check if MLflow is available
try:
    import mlflow
    import mlflow.xgboost
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logging.warning("MLflow not installed. Run: pip install mlflow")

# Configuration
EXPERIMENT_NAME = "BreatheSmart-PM25-Prediction"
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "mlruns")  # Local by default


def init_mlflow():
    """Initialize MLflow tracking"""
    if not MLFLOW_AVAILABLE:
        return False

    mlflow.set_tracking_uri(TRACKING_URI)

    # Create or get experiment
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        mlflow.create_experiment(EXPERIMENT_NAME)

    mlflow.set_experiment(EXPERIMENT_NAME)
    logging.info(f"MLflow initialized. Experiment: {EXPERIMENT_NAME}")
    return True


def start_run(run_name: str = None):
    """Start a new MLflow run"""
    if not MLFLOW_AVAILABLE:
        return None

    if run_name is None:
        run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return mlflow.start_run(run_name=run_name)


def log_params(params: dict):
    """Log hyperparameters"""
    if not MLFLOW_AVAILABLE:
        return

    for key, value in params.items():
        mlflow.log_param(key, value)


def log_metrics(metrics: dict, step: int = None):
    """Log metrics"""
    if not MLFLOW_AVAILABLE:
        return

    for key, value in metrics.items():
        mlflow.log_metric(key, value, step=step)


def log_model(model, model_name: str = "xgboost_pm25"):
    """Log and register model"""
    if not MLFLOW_AVAILABLE:
        return

    mlflow.xgboost.log_model(model, model_name)
    logging.info(f"Model logged: {model_name}")


def log_artifact(file_path: str):
    """Log a file as artifact"""
    if not MLFLOW_AVAILABLE:
        return

    if os.path.exists(file_path):
        mlflow.log_artifact(file_path)


def end_run():
    """End current MLflow run"""
    if MLFLOW_AVAILABLE:
        mlflow.end_run()


# Context manager for easy usage
class ExperimentRun:
    """Context manager for MLflow experiment runs"""

    def __init__(self, run_name: str = None, params: dict = None):
        self.run_name = run_name
        self.params = params or {}
        self.run = None

    def __enter__(self):
        if MLFLOW_AVAILABLE:
            init_mlflow()
            self.run = start_run(self.run_name)
            log_params(self.params)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_run()
        return False

    def log(self, metrics: dict):
        """Log metrics within the run"""
        log_metrics(metrics)


# Example usage
if __name__ == "__main__":
    # Check if MLflow is available
    if not MLFLOW_AVAILABLE:
        print("Please install MLflow: pip install mlflow")
        exit(1)

    # Example experiment
    with ExperimentRun(run_name="test_run", params={"learning_rate": 0.05}) as run:
        run.log({"rmse": 2.5, "mae": 1.8, "r2": 0.95})
        print("Test run logged successfully!")
        print(f"View at: mlflow ui")
