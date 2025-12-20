# 🌍 BreatheSmart: Production-Ready Air Quality Prediction System

An end-to-end automated data pipeline for forecasting urban air quality in Abu Dhabi, with built-in bias detection and mitigation.

## 📋 Overview

BreatheSmart is an automated system that:

- **Fetches** live air quality data from OpenAQ API (PM2.5, PM10, NO2, O3, SO2, CO)
- **Analyzes** geographic bias in sensor placement across neighborhoods
- **Predicts** PM2.5 levels for the next 6 hours using machine learning
- **Delivers** health alerts via a beautiful Streamlit web interface

## 🎯 The Problem & Solution

**Problem:** Urban residents lack hyper-local, predictive insights to plan outdoor activities safely. Sensor networks often have geographic bias, with fewer monitors in lower-income areas.

**Solution:** An automated pipeline that ingests, cleans, and analyzes air quality data to provide 6-hour forecasts with emphasis on sensor bias mitigation in under-represented neighborhoods.

---

## 🏗️ Architecture

The system is built across **5 phases**:

1. **Automated Data Ingestor** - Daily data collection from OpenAQ
2. **EDA & Bias Analysis** - Geographic discrimination detection
3. **Feature Engineering** - Time, weather, and spatial features
4. **ML Predictor** - XGBoost/Random Forest forecasting (target: 80%+ accuracy)
5. **Streamlit Deployment** - Public-facing web app with bias transparency

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

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Get your OpenAQ API Key (FREE & REQUIRED)**
   - Visit [https://explore.openaq.org/register](https://explore.openaq.org/register)
   - Create a free account
   - Copy your API key from your dashboard

4. **Configure your environment**

```bash
# Option 1: Copy the example and edit
copy .env.example .env
# Then open .env and replace 'your_api_key_here' with your actual API key

# Option 2: Create .env directly
echo OPENAQ_API_KEY=your_actual_api_key_here > .env
```

5. **Test the data ingestor**

```bash
python test_ingestor.py
```

### First Data Collection

**Fetch historical data (last 30 days):**

```bash
python data_ingestor.py
```

This will:

- Download PM2.5, PM10, NO2, O3, SO2, CO data for Abu Dhabi
- Save timestamped CSV files to `data/raw/`
- Generate logs in `logs/`

**Set up automated daily collection:**

```bash
python scheduler.py --mode daily  # Runs at 2:00 AM daily
python scheduler.py --mode hourly # For testing (runs every hour)
```

---

## 📁 Project Structure

```
BreatheSmart/
├── config.py                  # Centralized configuration
├── data_ingestor.py          # Production data fetcher with retry logic
├── scheduler.py              # Automated scheduling system
├── test_ingestor.py          # Test script
├── requirements.txt          # Python dependencies
├── .env                      # Configuration (gitignored)
├── .env.example              # Template for .env
├── .gitignore               
│
├── data/
│   ├── raw/                  # Raw data from OpenAQ
│   └── processed/            # Engineered features (Phase 3)
│
├── logs/                     # Execution logs
├── models/                   # Trained ML models (Phase 4)
├── notebooks/                # Jupyter notebooks for EDA (Phase 2)
└── reports/                  # Analysis reports
```

---

## 🔧 Configuration

Edit `.env` to customize:

```bash
TARGET_CITY=Abu Dhabi          # Target city
MAX_PM25_VALUE=500             # Filter unrealistic values
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR
```

---

## 📊 Current Status: Phase 1 Complete ✅

### ✅ Completed

- [x] Project structure setup
- [x] Configuration management
- [x] Production-ready data ingestor with:
  - Multi-parameter support (PM2.5, PM10, NO2, O3, SO2, CO)
  - Exponential backoff retry logic
  - Incremental loading (only fetch new data)
  - Comprehensive logging
- [x] Automated scheduler
- [x] Test suite

### 🔜 Next Steps (Phase 2)

- [ ] Exploratory Data Analysis
- [ ] Geographic bias detection
- [ ] Sensor coverage mapping

---

## 🧪 Testing

**Test data ingestion:**

```bash
python test_ingestor.py
```

**Check logs:**

```bash
# View latest ingestion log
ls logs/ | sort -r | head -1
```

---

## 📈 Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| 1: Data Ingestor | ✅ Complete | Automated OpenAQ data collection |
| 2: EDA & Bias | 🔜 Next | Geographic discrimination analysis |
| 3: Feature Engineering | ⏳ Planned | Time, weather, spatial features |
| 4: ML Predictor | ⏳ Planned | XGBoost forecasting model |
| 5: Web Deployment | ⏳ Planned | Streamlit public interface |

---

## 🤝 Contributing

This is a production-ready data engineering and ML project. Contributions welcome!

---

## 📄 License

See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAQ** - Open air quality data platform
- **Open-Meteo** - Free weather data API (Phase 3)

---

**Built with ❤️ for cleaner air in Abu Dhabi**
