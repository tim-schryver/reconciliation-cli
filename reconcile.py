"""Compare order and settlement CSV exports by transaction ID."""

import argparse
import csv
import re
import sys
from pathlib import Path

AMOUNT_PATTERN = re.compile(r"-?[0-9]+\.[0-9]{2}")
COLUMNS = {"transaction_id", "amount"}


def read_amounts(path):
    with path.open(newline="", encoding="utf-8-sig") as source:
        rows = csv.DictReader(source, strict=True)
        if rows.fieldnames is None or not COLUMNS.issubset(rows.fieldnames):
            raise ValueError(f"{path}: expected transaction_id and amount columns")
        amounts = {}
        for row in rows:
            transaction_id = (row["transaction_id"] or "").strip()
            amount = (row["amount"] or "").strip()
            if not transaction_id or not AMOUNT_PATTERN.fullmatch(amount):
                raise ValueError(f"{path}:{rows.line_num}: invalid ID or amount")
            if transaction_id in amounts:
                raise ValueError(f"{path}:{rows.line_num}: duplicate ID {transaction_id}")
            amounts[transaction_id] = int(amount.replace(".", ""))
        return amounts


def decimal_text(cents):
    if cents is None:
        return ""
    whole, fraction = divmod(abs(cents), 100)
    sign = "-" if cents < 0 else ""
    return f"{sign}{whole}.{fraction:02d}"


def differences(orders, settlements):
    for transaction_id in sorted(orders.keys() | settlements.keys()):
        order, settlement = orders.get(transaction_id), settlements.get(transaction_id)
        if order == settlement:
            continue
        if order is None:
            status = "missing_order"
        elif settlement is None:
            status = "missing_settlement"
        else:
            status = "amount_mismatch"
        yield transaction_id, status, decimal_text(order), decimal_text(settlement)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("orders", type=Path)
    parser.add_argument("settlements", type=Path)
    options = parser.parse_args()
    try:
        rows = list(differences(read_amounts(options.orders), read_amounts(options.settlements)))
    except (OSError, ValueError, csv.Error) as error:
        print(error, file=sys.stderr)
        return 2
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(["transaction_id", "status", "order_amount", "settlement_amount"])
    writer.writerows(rows)
    return int(bool(rows))


if __name__ == "__main__":
    raise SystemExit(main())
