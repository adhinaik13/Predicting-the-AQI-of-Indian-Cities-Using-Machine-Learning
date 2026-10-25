#!/usr/bin/env python3
"""Evaluate a leakage-resistant persistence baseline on chronological AQI holdout data.

The ID_Date field is expected to contain a stable series identifier followed by
an ISO date, e.g. AS_4_2022-12-04. Each series is evaluated independently.
Only prior observed AQI values are used as predictions.
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from datetime import date
from pathlib import Path

ID_DATE_PATTERN = re.compile(r"^(?P<series>.+)_(?P<date>\d{4}-\d{2}-\d{2})$")


def load_series(path: Path) -> dict[str, list[tuple[date, float]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        if not {"ID_Date", "AQI"}.issubset(fields):
            raise ValueError("train CSV must contain ID_Date and AQI columns")
        series: dict[str, list[tuple[date, float]]] = {}
        for line, row in enumerate(reader, start=2):
            key = (row.get("ID_Date") or "").strip()
            match = ID_DATE_PATTERN.fullmatch(key)
            if not match:
                raise ValueError(f"line {line}: ID_Date must end with YYYY-MM-DD: {key!r}")
            raw = (row.get("AQI") or "").strip()
            try:
                value = float(raw)
            except ValueError as exc:
                raise ValueError(f"line {line}: AQI must be numeric, got {raw!r}") from exc
            if not math.isfinite(value):
                raise ValueError(f"line {line}: AQI must be finite")
            series.setdefault(match.group("series"), []).append(
                (date.fromisoformat(match.group("date")), value)
            )
    if not series:
        raise ValueError("train CSV contains no records")
    for key, rows in series.items():
        rows.sort(key=lambda item: item[0])
        dates = [item[0] for item in rows]
        if len(dates) != len(set(dates)):
            raise ValueError(f"duplicate date in series {key!r}")
        if len(rows) < 3:
            raise ValueError(f"series {key!r} needs at least 3 rows for chronological evaluation")
    return series


def evaluate(series: dict[str, list[tuple[date, float]]], test_fraction: float = 0.2) -> dict[str, float | int | str]:
    if not 0.05 <= test_fraction <= 0.5:
        raise ValueError("test fraction must be between 0.05 and 0.5")
    errors: list[float] = []
    first_test_date: date | None = None
    last_test_date: date | None = None
    series_count = 0
    for rows in series.values():
        split = max(2, math.floor(len(rows) * (1.0 - test_fraction)))
        split = min(split, len(rows) - 1)
        # One-step-ahead persistence: predict each held-out value using only
        # the immediately preceding observed value in the same series.
        for index in range(split, len(rows)):
            errors.append(rows[index][1] - rows[index - 1][1])
            first_test_date = min(first_test_date, rows[index][0]) if first_test_date else rows[index][0]
            last_test_date = max(last_test_date, rows[index][0]) if last_test_date else rows[index][0]
        series_count += 1
    if not errors:
        raise ValueError("no held-out rows available")
    return {
        "baseline": "previous_observation",
        "series": series_count,
        "test_rows": len(errors),
        "test_start": first_test_date.isoformat() if first_test_date else "",
        "test_end": last_test_date.isoformat() if last_test_date else "",
        "mae": sum(abs(error) for error in errors) / len(errors),
        "rmse": math.sqrt(sum(error * error for error in errors) / len(errors)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("dataset/train.csv"))
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()
    try:
        metrics = evaluate(load_series(args.data), args.test_fraction)
    except (OSError, ValueError) as exc:
        print(f"Evaluation failed: {exc}", file=sys.stderr)
        return 2
    import json
    rendered = json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
