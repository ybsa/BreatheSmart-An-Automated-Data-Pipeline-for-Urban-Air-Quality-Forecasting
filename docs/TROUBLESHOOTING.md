# 🔍 Troubleshooting Guide

This guide helps you resolve common issues encountered while setting up or running BreatheSmart.

## 🔑 API Key Issues

### Error: `Unauthorized` or `Invalid API Key`

- **Cause**: The API key in your `.env` file is missing or incorrect.
- **Solution**:
  1. Ensure you have registered at [OpenAQ](https://explore.openaq.org/register).
  2. Verify that `OPENAQ_API_KEY` in your `.env` is correct.
  3. Restart the application after modifying `.env`.

---

## 📦 Installation Problems

### Error: `ModuleNotFoundError`

- **Cause**: Some dependencies are not installed in your environment.
- **Solution**:
  1. Ensure you are using a virtual environment.
  2. Run `pip install -r requirements.txt` again.
  3. Check for any installation errors in the console.

### Error: `XGBoost not found`

- **Cause**: XGBoost installation might require additional system libraries.
- **Solution**:
  - **Windows**: Install [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe).
  - **Linux**: Install `libomp` (e.g., `sudo apt-get install libomp-dev`).

---

## 📡 Data Fetching Errors

### Error: `No data retrieved`

- **Cause**: The OpenAQ API may not have data for the specified city/parameter in the given timeframe.
- **Solution**:
  1. Check if the city name is spelled correctly in `config.py` or `.env`.
  2. Increase the `days_back` parameter in `data_ingestor.py`.
  3. Check [OpenAQ Status](https://openaq.org/) for service outages.

---

## 🤖 Model Training Issues

### Error: `DataFrame is empty` during training

- **Cause**: `feature_engineering.py` failed to produce a valid `training_data.csv`.
- **Solution**:
  1. Ensure `data/raw/` contains valid CSV files with data.
  2. Run `python src/feature_engineering.py` manually and check for errors.

---

## 📊 Dashboard Issues

### Error: `Streamlit: command not found`

- **Cause**: Streamlit is not reachable in your path.
- **Solution**: Run it using `python -m streamlit run src/app.py`.

### Blank Charts

- **Cause**: No historical or prediction data found.
- **Solution**: Run the ingestion and prediction steps first as outlined in the README.

---

Still having issues? Open an issue on GitHub! 🚀
