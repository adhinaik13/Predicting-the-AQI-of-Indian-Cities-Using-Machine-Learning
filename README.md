[![Artifact Validation](https://github.com/vankudothuadhinaik/Predicting-the-AQI-of-Indian-Cities-Using-Machine-Learning/actions/workflows/validate-artifacts.yml/badge.svg)](https://github.com/vankudothuadhinaik/Predicting-the-AQI-of-Indian-Cities-Using-Machine-Learning/actions/workflows/validate-artifacts.yml)

# Indian City AQI Prediction

An exploratory time-series forecasting project developed for an H2O.ai hackathon. The repository contains AQI training data, exploratory data analysis, and notebooks comparing ARIMA-family models with Prophet.

## Problem

Air Quality Index (AQI) forecasting can help communicate potential changes in air quality. This project explores historical AQI data and environmental features for Indian cities, with a focus on time-series approaches.

## Repository contents

- `dataset/train.csv` — training dataset
- `dataset/sample_submission.csv` — sample submission format
- `Notebooks/Data Analysis-EDA.ipynb` — exploratory analysis notebook
- `Notebooks/ARIMA .ipynb` — time-series forecasting experiments
- `H2o_models/` and `output_file/` — supporting project artifacts

## Models explored

- ARIMA
- SARIMAX
- Facebook Prophet

The original project notes report the following MAE values:

| Model | Reported MAE |
|---|---:|
| Prophet | 528.99 |
| SARIMAX | 36.89 |
| ARIMA with Box–Cox transformation | 32 |

These are historical values recorded in the project notes, not independently reproduced results. The repository notes do not fully document the evaluation split, target scale, or leakage checks, so the values should not be treated as a validated benchmark until the experiments are rerun under a clearly defined protocol.

## Explore the notebooks

1. Clone or download this repository.
2. Open the notebooks in Jupyter Notebook or JupyterLab.
3. Review the import cells at the top of each notebook and install the required Python packages.
4. Run the data preparation and modeling cells in order.
5. Before comparing models, verify the time-based train/test split, target units, missing-value handling, and that future information is not used during training.

A standard-library evaluation script now measures a previous-observation persistence baseline with a chronological holdout split per `ID_Date` series. CI runs the baseline and its unit tests. The script is intentionally a baseline, not a reproduction of the ARIMA/SARIMAX/Prophet experiments; the original model metrics remain unverified.

## Reproducible baseline evaluation

Run from the repository root with Python 3.10+ (standard library only):

```bash
python -m unittest -v test_evaluate_baseline.py
python evaluate_baseline.py --data dataset/train.csv --output baseline_metrics.json
```

The script parses the series key and date from `ID_Date`, sorts each series chronologically, holds out the latest 20% of rows per series, and predicts each held-out value using the immediately previous observed AQI from that same series. It reports MAE/RMSE, test date range, series count, and test row count. This avoids random splitting and cross-series carryover. The result is a persistence baseline only; it does not prove the older model results or establish a production-quality forecast.

## Limitations and next steps

- Make the time-based validation split explicit and reproducible.
- Record the AQI target scale, forecast horizon, and evaluation period.
- Compare models against a simple baseline and report MAE/RMSE on the same held-out period.
- Add a pinned dependency file and a script for repeatable training/evaluation.
- Review the notebooks for leakage and document the dataset source and license.

This is an educational/research project, not a deployed air-quality forecasting service. Predictions should not be used as a substitute for official AQI measurements or public-health guidance.
