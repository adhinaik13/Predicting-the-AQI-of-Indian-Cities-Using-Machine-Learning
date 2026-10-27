# Indian City AQI Prediction

[![Artifact validation](https://github.com/vankudothuadhinaik/Predicting-the-AQI-of-Indian-Cities-Using-Machine-Learning/actions/workflows/validate-artifacts.yml/badge.svg)](https://github.com/vankudothuadhinaik/Predicting-the-AQI-of-Indian-Cities-Using-Machine-Learning/actions/workflows/validate-artifacts.yml)

A time-series forecasting and evaluation project exploring air-quality trends across Indian city/station series. The repository combines exploratory notebooks with a reproducible chronological persistence baseline so that future model comparisons can start from a transparent reference point.

> **Research/demo only.** This repository is not a live AQI service. Its predictions are not a substitute for official measurements, alerts, or public-health guidance.

## At a glance

| Area | Current state |
|---|---|
| Problem | Explore historical AQI forecasting across multiple series |
| Data | Repository training CSV and sample-submission template |
| Methods explored | ARIMA, SARIMAX, Prophet |
| Reproducible evaluation | Previous-observation persistence baseline |
| Automation | GitHub Actions validates tests, data artifacts, and notebook structure |
| Deployment | No production service is provided |

## Results: reproducible baseline

The committed baseline script uses a chronological holdout within each `ID_Date` series. It predicts each held-out value using the immediately preceding observed AQI from the same series.

| Metric | Current baseline result |
|---|---:|
| Held-out rows | 5,088 |
| Series | 40 |
| Test date range | 2022-06-16 to 2022-12-03 |
| MAE | 28.54 |
| RMSE | 43.42 |

These values describe the current CSV and the script's current split settings. They are a **persistence baseline**, not a model leaderboard or evidence of production forecasting quality.

### Historical notebook metrics (not yet validated)

| Model | Historical MAE noted in the project |
|---|---:|
| Prophet | 528.99 |
| SARIMAX | 36.89 |
| ARIMA with Box–Cox transformation | 32 |

The older numbers are retained as historical notes only. The original evaluation protocol does not fully specify the split, target scale, forecast horizon, or leakage checks. Do not compare these values directly with the baseline above until all models are rerun on the same chronological holdout and target scale.

## Repository guide

| Path | Purpose |
|---|---|
| `dataset/train.csv` | Training data used by the baseline evaluator |
| `dataset/sample_submission.csv` | Submission-format example |
| `Notebooks/Data Analysis-EDA.ipynb` | Exploratory data analysis |
| `Notebooks/ARIMA .ipynb` | ARIMA-family forecasting experiments |
| `H2o_models/` | Supporting model artifacts |
| `output_file/` | Existing output artifacts |
| `evaluate_baseline.py` | Standard-library chronological baseline evaluator |
| `test_evaluate_baseline.py` | Unit tests for the evaluator |
| `.github/workflows/validate-artifacts.yml` | CI checks for tests and repository artifacts |

## Quick start

**Requirements:** Python 3.10 or newer. The baseline evaluator and its unit tests use only the Python standard library.

From the repository root:

```bash
python -m unittest -v test_evaluate_baseline.py
python evaluate_baseline.py --data dataset/train.csv --output baseline_metrics.json
```

The JSON output records the evaluation metrics and date/series coverage. To explore the notebooks, open them in Jupyter Notebook or JupyterLab and install the packages imported by the notebook you intend to run.

## Evaluation protocol

The current baseline:

1. Parses the series key and date from `ID_Date`.
2. Sorts observations chronologically within each series.
3. Holds out the latest 20% of rows in each series.
4. Uses the immediately previous observed value as each prediction.
5. Reports MAE, RMSE, test date range, series count, and held-out row count.

Before treating any model comparison as valid, keep the same time-based split, target units, forecast horizon, and metric definitions across all models. Fit preprocessing on training data only, check missing values and duplicate timestamps, and verify that no future information enters features or transformations.

## Models explored

- **ARIMA** — univariate autoregressive integrated moving-average forecasting.
- **SARIMAX** — seasonal and/or exogenous-variable time-series modeling.
- **Prophet** — decomposable trend and seasonality modeling.

The notebooks are exploratory artifacts; they are not yet a single, fully reproducible benchmark pipeline.

## Roadmap

- [ ] Document the dataset source, license, target units, and series semantics.
- [ ] Pin notebook dependencies and add a repeatable training/evaluation entry point.
- [ ] Re-run ARIMA, SARIMAX, and Prophet on the same chronological holdout.
- [ ] Add per-series metrics and a clear forecast horizon.
- [ ] Review all feature engineering and transformations for temporal leakage.
- [ ] Record environment and configuration alongside each result.

## Limitations

- Historical model metrics have not been independently reproduced.
- Dataset provenance and licensing need to be documented clearly.
- A persistence baseline is a reference point, not a complete forecasting solution.
- No live data ingestion, deployment, monitoring, or public-health alerting is included.

## Contributing

Keep evaluation changes reproducible: add or update tests, preserve chronological separation, avoid leakage, and document any change to the holdout protocol before comparing metrics.
