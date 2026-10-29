#!/usr/bin/env python3
"""Compare simple AQI baselines on the same chronological holdout.

The persistence model predicts the immediately previous observation. The mean
model predicts the mean AQI of each series' training partition. No held-out
target values are used to fit either model.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from evaluate_baseline import load_series


def compare(series: dict[str, list[tuple[Any, float]]], test_fraction: float = 0.2) -> dict[str, Any]:
    if not 0.05 <= test_fraction <= 0.5:
        raise ValueError("test fraction must be between 0.05 and 0.5")

    errors: dict[str, list[float]] = {"previous_observation": [], "training_mean": []}
    first_test_date = None
    last_test_date = None
    test_rows = 0

    for rows in series.values():
        if len(rows) < 3:
            raise ValueError("each series needs at least 3 rows")
        split = max(2, math.floor(len(rows) * (1.0 - test_fraction)))
        split = min(split, len(rows) - 1)
        training = rows[:split]
        held_out = rows[split:]
        mean_prediction = sum(value for _, value in training) / len(training)

        for index, (timestamp, actual) in enumerate(held_out, start=split):
            errors["previous_observation"].append(actual - rows[index - 1][1])
            errors["training_mean"].append(actual - mean_prediction)
            first_test_date = min(first_test_date, timestamp) if first_test_date else timestamp
            last_test_date = max(last_test_date, timestamp) if last_test_date else timestamp
            test_rows += 1

    if not test_rows:
        raise ValueError("no held-out rows available")

    metrics = {}
    for name, residuals in errors.items():
        metrics[name] = {
            "mae": sum(abs(error) for error in residuals) / len(residuals),
            "rmse": math.sqrt(sum(error * error for error in residuals) / len(residuals)),
        }

    return {
        "evaluation": "chronological_one_step_ahead",
        "test_fraction": test_fraction,
        "series": len(series),
        "test_rows": test_rows,
        "test_start": first_test_date.isoformat(),
        "test_end": last_test_date.isoformat(),
        "models": metrics,
        "best_by_mae": min(metrics, key=lambda name: metrics[name]["mae"]),
        "best_by_rmse": min(metrics, key=lambda name: metrics[name]["rmse"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("dataset/train.csv"))
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--output", type=Path, default=Path("baseline_comparison.json"))
    args = parser.parse_args()
    try:
        result = compare(load_series(args.data), args.test_fraction)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
