# Transaction Reconciliation CLI

Compare two CSV exports and report missing transactions and amount mismatches. The CLI compares integer cents and rejects duplicate IDs so ambiguous rows cannot silently override earlier data. Both exports must use the same currency and have `transaction_id` and `amount` headers. Amounts require two decimal places.

```sh
python3 reconcile.py examples/orders.csv examples/settlements.csv
python3 -m unittest -v
```

The CSV report goes to standard output. The exit status is 0 for a match, 1 for differences, and 2 for invalid input or file errors. Requires Python 3.10+ and uses the standard library.
