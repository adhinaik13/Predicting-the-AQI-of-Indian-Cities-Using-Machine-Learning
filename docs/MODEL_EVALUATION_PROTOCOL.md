# AQI model evaluation protocol

The checked-in CI baseline is a previous-observation persistence baseline using a chronological holdout. It is useful as a reproducibility check, but it does not reproduce the historical ARIMA, SARIMAX, or Prophet scores recorded in older project notes.

## Fair comparison requirements

1. Define the series key, target column, target units, forecast horizon, and evaluation dates before training.
2. Sort each series by parsed timestamp and split chronologically. Never randomly split time-series rows.
3. Fit transformations, imputers, feature selection, and hyperparameters using training data only.
4. For a multi-step forecast, do not use actual future AQI values from inside the holdout to construct later predictions unless the experiment is explicitly a rolling one-step-ahead evaluation.
5. Compare every candidate on the same series and exact test timestamps as the persistence baseline.
6. Report MAE and RMSE, number of evaluated rows and series, test date range, missing-value policy, and forecast horizon.
7. Record package versions, random seeds, source-data checksum, and the commit SHA used to generate results.
8. Keep the untouched holdout separate from model selection; use a validation window for tuning.

## Data provenance

Before treating this project as a research result, document the original dataset source, license, collection frequency, missingness, and any transformations applied to AQI. Review notebooks for target leakage and ensure the model artifacts can be traced to a specific training procedure.

## Claim boundaries

The historical MAE figures in the main README are reported project notes, not independently reproduced benchmarks. Do not rank the models using those numbers until the original split, target scale, and evaluation protocol have been reproduced. This repository is educational; predictions are not a substitute for official AQI readings or public-health guidance.
