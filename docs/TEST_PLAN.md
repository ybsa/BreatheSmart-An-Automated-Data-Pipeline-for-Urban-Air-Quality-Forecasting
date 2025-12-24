# 🧪 BreatheSmart Test Plan

This document outlines the testing strategy for the BreatheSmart Automated Data Pipeline.

## 1. Unit Testing

Unit tests focus on individual components in isolation.

| Component | Test File | Test Cases |
|-----------|-----------|------------|
| **Ingestor** | `tests/test_ingestor.py` | - Verify API connection <br> - Verify data fetching for valid city <br> - Check CSV saving functionality <br> - Handle API errors/empty responses |
| **Feature Eng.** | *Manual/Script* | - Input: valid raw CSV -> Output: `training_data.csv` exists <br> - Input: empty file -> Output: Handle gracefully |
| **Model** | *Manual/Script* | - Input: `training_data.csv` -> Output: `model.json` exists <br> - Verify RMSE is within acceptable range (< 5.0) |

## 2. Integration Testing

Integration tests verify that components work together.

### Pipeline Flow

1. **Ingest -> Process**: Run ingestor, then run feature engineering. Verify `training_data.csv` contains data from the new ingest.
2. **Process -> Train**: Run training. Verify model artifacts are updated.
3. **Train -> Predict**: Run prediction. Verify it produces a value using the new model.

## 3. System Testing (End-to-End)

Use `src/scheduler.py` in test mode to run the full cycle.

**Command:**

```bash
python src/scheduler.py --mode test
```

**Pass Criteria:**

1. Log file created in `logs/scheduler_*.log`.
2. Execution flows through Steps 1-4 without crash.
3. `data/predictions.csv` has a new entry.

## 4. Manual Validations

- **Data Quality**: Open `data/raw/` CSVs to ensure values are reasonable (e.g., PM2.5 < 1000).
- **prediction.csv**: Ensure dates are increasing and logical.
