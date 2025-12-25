# 🌍 BreatheSmart: Production-Ready Air Quality Prediction System

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

An end-to-end automated data pipeline for forecasting urban air quality in Abu Dhabi, with built-in bias detection and mitigation.

## 📋 Overview

BreatheSmart is an automated system that:

- **Fetches** live air quality data from OpenAQ API (PM2.5, PM10, NO2, O3, SO2, CO)
- **Analyzes** geographic bias in sensor placement across neighborhoods
- **Predicts** PM2.5 levels for the next hour using machine learning
- **Delivers** health alerts via actionable forecasts

## 🎯 The Problem & Solution

**Problem:** Urban residents lack hyper-local, predictive insights to plan outdoor activities safely. Sensor networks often have geographic bias, with fewer monitors in lower-income areas.

**Solution:** An automated pipeline that ingests, cleans, and analyzes air quality data to provide accurate forecasts with emphasis on sensor bias mitigation in under-represented neighborhoods.

---

## 🏗️ Architecture

The system is built across **5 phases**:

1. **Automated Data Ingestor** - Daily data collection from OpenAQ
2. **EDA & Bias Analysis** - Geographic discrimination detection
3. **Feature Engineering** - Correction of data leakage, imputation, and lag generation
4. **ML Predictor** - XGBoost forecasting (RMSE ~2.9 µg/m³)
5. **Operational Forecasting** - Automated prediction script

See [PROJECT_MAP.md](docs/PROJECT_MAP.md) for a detailed architecture diagram.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd BreatheSmart-An-Automated-Data-Pipeline-for-Urban-Air-Quality-Forecasting
```

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

1. **Get your OpenAQ API Key (FREE & REQUIRED)**
   - Visit [https://explore.openaq.org/register](https://explore.openaq.org/register)
   - Create a free account
   - Copy your API key from your dashboard

2. **Configure your environment**

```bash
# Option 1: Copy the example and edit
copy .env.example .env
# Then open .env and replace 'your_api_key_here' with your actual API key

# Option 2: Create .env directly
echo OPENAQ_API_KEY=your_actual_api_key_here > .env
```

---

## 🛠️ Running the Pipeline

### Step 1: Data Collection

Fetch historical data (last 30 days) or start the daily ingestor:

```bash
python src/data_ingestor.py
```

*Output:* Raw CSV files saved to `data/raw/` (e.g., `data/raw/abudhabi_pm25_20251224_000905.csv`).

### Step 2: Feature Engineering

Process the raw data into a machine-learning-ready format:

```bash
python src/feature_engineering.py
```

*Output:* Processed dataset saved to `data/processed/training_data.csv`.

### Step 3: Model Training

Train the XGBoost Regressor on the processed data:

```bash
python src/model_training.py
```

*Output:*

- Trained model saved to `models/xgboost_pm25.json`
- Feature list saved to `models/model_features.pkl`

### Step 4: Generate Forecasts

Run the prediction engine to generate a forecast for the next hour:

```bash
python src/prediction.py
```

*Output:*

- Console output: `Forecast for 2024-01-01 10:00: 15.2 µg/m³`
- Log file: `data/predictions.csv`

---

## 🧪 Testing

We use `pytest` for unit and integration testing.

### Run all tests

```bash
pytest tests/
```

### Run with coverage report

```bash
pytest tests/ --cov=src --cov-report=html
```

---

## 🤖 Automation

To run the ingestion pipeline on a schedule (e.g., daily at 2:00 AM):

```bash
python src/scheduler.py
```

To run a single test loop:

```bash
python src/scheduler.py --mode test
```

---

## 💻 Web Dashboard

To launch the interactive dashboard:

```bash
streamlit run src/app.py
```

Features:

- **Real-time Metrics**: View current PM2.5 and forecasts.
- **Interactive Chart**: Explore historical trends.
- **Forecast Logs**: View prediction history.

---

## 📊 Project Structure

```
├── src/                 # Source code
│   ├── config.py
│   ├── data_ingestor.py
│   ├── feature_engineering.py
│   ├── model_training.py
│   ├── prediction.py
│   └── scheduler.py
├── tests/               # Test scripts
│   ├── conftest.py      # Test fixtures
│   ├── test_config.py
│   ├── test_ingestor.py
│   └── ...
├── data/
│   ├── raw/             # Raw CSVs
│   ├── processed/       # Cleaned training data
│   └── predictions.csv  # Forecast logs
├── docs/                # Project Documentation
│   ├── PROJECT_MAP.md
│   ├── TEST_PLAN.md
│   └── TROUBLESHOOTING.md
├── .github/workflows/   # CI/CD pipelines
├── logs/                # System logs
├── models/              # Trained XGBoost artifacts
├── notebooks/           # EDA and Analysis
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Multi-service orchestration
└── requirements.txt
```

---

## 🐳 Docker Deployment

### Quick Start with Docker

```bash
# Build and run the dashboard
docker compose up -d dashboard

# View logs
docker compose logs -f dashboard

# Stop
docker compose down
```

### Run Full Pipeline (with Scheduler)

```bash
# Run dashboard + automated scheduler
docker compose --profile full up -d
```

### Build Manually

```bash
# Build the image
docker build -t breathesmart .

# Run the dashboard
docker run -p 8501:8501 -e OPENAQ_API_KEY=your_key breathesmart
```

---

## 🔄 CI/CD Pipeline

This project uses **GitHub Actions** for continuous integration:

- ✅ **Automated Testing** - Runs on Python 3.10, 3.11, 3.12
- ✅ **Code Quality** - Flake8 linting, Black formatting checks
- ✅ **Docker Build** - Validates container builds
- ✅ **Coverage Reports** - Uploaded to Codecov

### Workflow Status

Tests run automatically on every push and pull request to `main`/`master`.

---

## ☁️ Cloud Deployment

### Streamlit Cloud (Recommended - Free)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub account
4. Deploy with:
   - **Main file path:** `src/app.py`
   - **Secrets:** Add `OPENAQ_API_KEY`

### Railway / Render

Use the included `Dockerfile` for one-click deployment.

---

## 🤖 MLOps Features

### Experiment Tracking (MLflow)

```bash
# Start MLflow UI
mlflow ui
# View experiments at http://localhost:5000
```

### Model Monitoring

```bash
# Run health checks on predictions
python src/monitoring.py
```

### Data Versioning (DVC)

```bash
# Track training data
dvc add data/processed/training_data.csv
dvc push
```

### Pre-commit Hooks

```bash
# Install hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

See [MLOPS_GUIDE.md](docs/MLOPS_GUIDE.md) for detailed documentation.

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
