import tempfile
import unittest
from pathlib import Path

from reconcile import differences, read_amounts


class ReconciliationTests(unittest.TestCase):
    def test_reports_all_differences_in_order(self):
        rows = differences({"b": 0, "a": 102, "d": -1}, {"c": 150, "a": 103, "d": -1})
        self.assertEqual(list(rows), [
            ("a", "amount_mismatch", "1.02", "1.03"),
            ("b", "missing_settlement", "0.00", ""),
            ("c", "missing_order", "", "1.50"),
        ])

    def test_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.csv"
            path.write_text("transaction_id,amount\na,1.05\na,2.00\n")
            with self.assertRaisesRegex(ValueError, "duplicate ID"):
                read_amounts(path)
