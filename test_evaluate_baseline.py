import csv
import tempfile
import unittest
from pathlib import Path

from evaluate_baseline import evaluate, load_series


class BaselineEvaluationTests(unittest.TestCase):
    def write_csv(self, rows):
        temporary = tempfile.NamedTemporaryFile(mode="w", newline="", encoding="utf-8", suffix=".csv", delete=False)
        self.addCleanup(lambda: Path(temporary.name).unlink(missing_ok=True))
        with temporary:
            writer = csv.DictWriter(temporary, fieldnames=["ID_Date", "AQI"])
            writer.writeheader()
            writer.writerows(rows)
        return Path(temporary.name)

    def test_chronological_persistence_metrics_are_deterministic(self):
        path = self.write_csv([
            {"ID_Date": f"A_1_2024-01-0{i}", "AQI": value}
            for i, value in [(1, 10), (2, 12), (3, 15), (4, 14), (5, 18)]
        ])
        result = evaluate(load_series(path), test_fraction=0.4)
        self.assertEqual(result["test_rows"], 2)
        self.assertEqual(result["test_start"], "2024-01-04")
        self.assertAlmostEqual(result["mae"], 2.5)
        self.assertAlmostEqual(result["rmse"], (8.5) ** 0.5)

    def test_series_are_evaluated_independently(self):
        rows = []
        for series, values in (("A_1", [1, 2, 3]), ("B_2", [10, 10, 10])):
            for day, value in enumerate(values, start=1):
                rows.append({"ID_Date": f"{series}_2024-01-0{day}", "AQI": value})
        result = evaluate(load_series(self.write_csv(rows)), test_fraction=0.34)
        self.assertEqual(result["series"], 2)
        self.assertEqual(result["test_rows"], 2)

    def test_rejects_malformed_id_date(self):
        path = self.write_csv([
            {"ID_Date": "missing-date", "AQI": "1"},
            {"ID_Date": "A_1_2024-01-02", "AQI": "2"},
            {"ID_Date": "A_1_2024-01-03", "AQI": "3"},
        ])
        with self.assertRaisesRegex(ValueError, "ID_Date"):
            load_series(path)

    def test_rejects_non_finite_aqi(self):
        path = self.write_csv([
            {"ID_Date": f"A_1_2024-01-0{i}", "AQI": value}
            for i, value in [(1, "1"), (2, "NaN"), (3, "3")]
        ])
        with self.assertRaisesRegex(ValueError, "finite"):
            load_series(path)


if __name__ == "__main__":
    unittest.main()
