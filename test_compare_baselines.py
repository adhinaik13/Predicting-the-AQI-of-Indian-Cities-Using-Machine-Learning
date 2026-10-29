import unittest
from datetime import date

from compare_baselines import compare


class BaselineComparisonTests(unittest.TestCase):
    def test_models_use_identical_chronological_holdout(self):
        rows = {
            "A": [
                (date(2024, 1, 1), 10.0),
                (date(2024, 1, 2), 12.0),
                (date(2024, 1, 3), 15.0),
                (date(2024, 1, 4), 14.0),
                (date(2024, 1, 5), 18.0),
            ]
        }
        result = compare(rows, test_fraction=0.4)
        self.assertEqual(result["test_rows"], 2)
        self.assertEqual(result["test_start"], "2024-01-04")
        self.assertEqual(result["test_end"], "2024-01-05")
        self.assertEqual(set(result["models"]), {"previous_observation", "training_mean"})
        self.assertAlmostEqual(result["models"]["previous_observation"]["mae"], 2.5)
        self.assertAlmostEqual(result["models"]["training_mean"]["mae"], 4.5)

    def test_invalid_holdout_fraction_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "test fraction"):
            compare({"A": [(date(2024, 1, i), float(i)) for i in range(1, 4)]}, 0.9)

    def test_no_future_values_used_to_fit_training_mean(self):
        original = {
            "A": [
                (date(2024, 1, 1), 1.0),
                (date(2024, 1, 2), 2.0),
                (date(2024, 1, 3), 3.0),
                (date(2024, 1, 4), 1000.0),
            ]
        }
        result = compare(original, test_fraction=0.25)
        self.assertAlmostEqual(result["models"]["training_mean"]["mae"], 998.0)


if __name__ == "__main__":
    unittest.main()
