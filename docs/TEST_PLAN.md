# 🧪 BreatheSmart Test Plan

## 🎯 Testing Strategy

The goal of this test plan is to ensure the reliability and accuracy of the BreatheSmart air quality prediction pipeline. We use a multi-layered approach involving unit tests, integration tests, and manual verification.

## 🏗️ Test Layers

### 1. Unit Testing

Testing individual components in isolation.

- **Locations**: `tests/test_*.py`
- **Framework**: `pytest`
- **Focus**: Function-level logic, error handling, data transformations.

### 2. Integration Testing

Testing multiple components working together.

- **Focus**: API to Storage flow, Feature Engineering to Model input.
- **Scripts**: `tests/test_ingestor.py`

### 3. Manual Verification

End-to-end checks of the system output.

- **Focus**: Dashboard UI, Scheduler loops, Log auditing.

## 🚀 Execution Commands

### Run all tests

```bash
pytest tests/
```

### Run with coverage report

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Run specific module tests

```bash
pytest tests/test_data_ingestor.py
```

## 📋 Test Matrix

| Component | Test File | Test Case | Success Criteria |
|-----------|-----------|-----------|------------------|
| Config | `test_config.py` | Load .env | Keys are loaded correctly |
| Ingestor | `test_data_ingestor.py` | Fetch API | Dataframe returned with data |
| Feature Eng | `test_feature_engineering.py` | Lag Generation | Features match expected shift |
| Model | `test_model_training.py` | Save/Load | Artifacts are valid JSON/PKL |
| Predictor | `test_prediction.py` | Single Forecast | Numeric output > 0 |

## 🧪 Manual Checklists

### Dashboard Verification

- [ ] Run `streamlit run src/app.py`
- [ ] Verify "Current Level" matches latest raw data
- [ ] Verify "Forecast" line is visible on chart
- [ ] Check sidebar for any error warnings

### Scheduler Verification

- [ ] Run `python src/scheduler.py --mode test`
- [ ] Verify logs show full loop completion
- [ ] Check `data/predictions.csv` for the new timestamp
