# DMRC Network and Hub Analytics

Analysis of Delhi Metro fare patterns, station routes, and fare prediction models.

## Project structure

```text
data/
  dmrc_fare_prediction_cleaned.csv   # Clean input dataset
  processed/
    dmrc_fare_results.csv            # Trips with estimated fares
reports/
  line_summary.csv                   # Summary by corridor line
  model_comparison.csv               # Model performance comparison
  feature_importance.csv             # Standardized feature coefficients
  test_predictions.csv               # Test-set predictions
src/
  dmrc_fare_prediction.py            # Data analysis and fare estimation
requirements.txt
```

## Setup

```powershell
python -m pip install -r requirements.txt
```

## Run

From the project root:

```powershell
python src/dmrc_fare_prediction.py
```

The script reads the dataset from `data/` and writes generated files to `data/processed/` and `reports/`.