# 🤖 MLOps Guide

This guide covers the MLOps features added to BreatheSmart for production-grade machine learning operations.

## 📊 MLflow Experiment Tracking

### Setup

```bash
# Install MLflow
pip install mlflow

# Start the MLflow UI
mlflow ui
# Access at http://localhost:5000
```

### Usage

The `mlflow_tracking.py` module provides easy integration:

```python
from mlflow_tracking import ExperimentRun

# Track an experiment
with ExperimentRun(run_name="my_experiment", params={"lr": 0.05}) as run:
    # Train your model...
    run.log({"rmse": 2.5, "mae": 1.8, "r2": 0.95})
```

### What Gets Tracked

- **Parameters**: Hyperparameters, configuration
- **Metrics**: RMSE, MAE, R², training loss
- **Artifacts**: Model files, feature lists, plots
- **Models**: Registered XGBoost models

---

## 📈 Model Monitoring

### Run Monitoring

```bash
python src/monitoring.py
```

### Features

- **Prediction Range Check**: Ensures PM2.5 values are 0-500 µg/m³
- **Variance Detection**: Alerts on unusual prediction variance
- **Gap Detection**: Identifies missing hourly predictions

### Alerts

Alerts are logged and can be sent to:

- Console logs
- Slack (webhook integration)
- Email (SMTP integration)

### Monitoring Report

Generated at `reports/monitoring_report.md`:

```markdown
# Model Monitoring Report
- Predictions Analyzed: 168
- All Checks Passed: ✅ Yes
```

---

## 📦 Data Versioning (DVC)

### Setup

```bash
# Install DVC
pip install dvc

# Initialize (already done)
dvc init

# Add remote storage
dvc remote add -d myremote s3://bucket/path
```

### Track Data

```bash
# Track training data
dvc add data/processed/training_data.csv

# Commit changes
git add data/processed/training_data.csv.dvc .gitignore
git commit -m "Track training data"

# Push to remote
dvc push
```

### Retrieve Data

```bash
# Pull data from remote
dvc pull

# Checkout specific version
git checkout v1.0
dvc checkout
```

---

## 🔄 Pre-commit Hooks

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

### What Runs

- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Linting
- **Bandit**: Security checks
- **General**: Trailing whitespace, YAML/JSON validation

### Manual Run

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

---

## 🏗️ CI/CD Integration

The GitHub Actions workflow includes:

1. **Testing**: pytest on Python 3.10-3.12
2. **Linting**: Flake8, Black checks
3. **Security**: Bandit security scan
4. **Docker**: Build validation

---

## 📋 Quick Commands

| Task | Command |
|------|---------|
| Start MLflow UI | `mlflow ui` |
| Run monitoring | `python src/monitoring.py` |
| Track data | `dvc add <file>` |
| Run pre-commit | `pre-commit run --all-files` |
| Run tests | `pytest tests/` |

---

## 🎯 Best Practices

1. **Always track experiments** - Use MLflow for every training run
2. **Version your data** - Use DVC for training data changes
3. **Monitor continuously** - Run monitoring after each prediction batch
4. **Automate checks** - Let pre-commit catch issues before commit
