# 🗺️ BreatheSmart Project Map

## Project Structure

```mermaid
graph TD
    Root[Project Root] --> Src[src/]
    Root --> Data[data/]
    Root --> Tests[tests/]
    Root --> Docs[docs/]
    Root --> Scripts[scripts/]
    Root --> Logs[logs/]
    Root --> Models[models/]

    Src --> Ingestor[data_ingestor.py]
    Src --> FeatEng[feature_engineering.py]
    Src --> Trainer[model_training.py]
    Src --> Predictor[prediction.py]
    Src --> Scheduler[scheduler.py]
    Src --> Config[config.py]

    Data --> Raw[raw/]
    Data --> Processed[processed/]
    Data --> Preds[predictions.csv]

    Docs --> Plan[TEST_PLAN.md]
    Docs --> Map[PROJECT_MAP.md]

    Models --> ModelFile[xgboost_pm25.json]
    Models --> ModelFeats[model_features.pkl]

    Src --> App[app.py]
    Src --> Viz[visualization.py]
    
    Root --> Reports[reports/]

    subgraph "Data Flow"
        Ingestor -->|Writes| Raw
        Raw -->|Reads| FeatEng
        FeatEng -->|Writes| Processed
        Processed -->|Reads| Trainer
        Processed -->|Reads| Predictor
        Trainer -->|Writes| Models
        Models -->|Reads| Predictor
        Predictor -->|Writes| Preds
        Processed -->|Reads| Viz
        Preds -->|Reads| Viz
        Viz -->|Writes| Reports
        Processed -->|Reads| App
        Preds -->|Reads| App
    end
```

## Description of Key Files

### Source Code (`src/`)

- **`data_ingestor.py`**: Fetches air quality data from OpenAQ API.
- **`feature_engineering.py`**: Cleans raw data and creates lag/rolling features for ML.
- **`model_training.py`**: Trains the XGBoost model on processed data.
- **`prediction.py`**: Generates forecasts for the next hour.
- **`scheduler.py`**: Automates the pipeline to run daily or hourly.
- **`config.py`**: Central configuration (API keys, paths, constants).
- **`app.py`**: Streamlit dashboard for real-time monitoring and visualization.
- **`visualization.py`**: Generates static trend charts for reporting.

### Data (`data/`)

- **`raw/`**: Archival storage of fetched JSON/CSV data.
- **`processed/`**: Cleaned, single-file dataset ready for training.
- **`predictions.csv`**: History of all generated forecasts.

### Reports (`reports/`)

- **`pm25_trend_forecast.png`**: Generated visualization of recent trends.
