# 🌍 BreatheSmart: Production-Ready Air Quality Prediction System

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
python data_ingestor.py
```

*Output:* Raw CSV files saved to `data/raw/` (e.g., `data/raw/abudhabi_pm25_20251224_000905.csv`).

### Step 2: Feature Engineering

Process the raw data into a machine-learning-ready format. This step handles:

- Merging multiple pollutant files
- Resampling to hourly frequency
- Imputing missing values
- Generating Lag and Rolling Mean features (shifted to prevent leakage)

```bash
python 02_feature_engineering.py
```

*Output:* Processed dataset saved to `data/processed/training_data.csv`.

### Step 3: Model Training

Train the XGBoost Regressor on the processed data. The script uses a time-series split (Train: 80%, Test: 20%) to validate performance.

```bash
python 03_model_training.py
```

*Output:*

- Trained model saved to `models/xgboost_pm25.json`
- Feature list saved to `models/model_features.pkl`
- Validated Test RMSE: ~2.9 µg/m³

### Step 4: Generate Forecasts

Run the prediction engine to generate a forecast for the next hour based on the latest available data.

```bash
python 04_predict.py
```

*Output:*

- Console output: `Forecast for 2024-01-01 10:00: 15.2 µg/m³`
- Log file: `data/predictions.csv`

---

## 🤖 Automation

To run the ingestion pipeline on a schedule (e.g., daily at 2:00 AM):

```bash
python scheduler.py
```

## 📊 Project Structure

```
├── data/
│   ├── raw/                 # Raw CSVs from OpenAQ
│   ├── processed/           # Cleaned training data
│   └── predictions.csv      # Log of generated forecasts
├── logs/                    # System logs
├── models/                  # Trained XGBoost artifacts
├── notebooks/               # EDA and Analysis
│   └── 01_eda_and_bias_analysis.ipynb
├── 02_feature_engineering.py
├── 03_model_training.py
├── 04_predict.py
├── data_ingestor.py
├── config.py
└── requirements.txt
```

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
