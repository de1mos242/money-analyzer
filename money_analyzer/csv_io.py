from __future__ import annotations

import csv
from pathlib import Path

from money_analyzer.models import CANONICAL_COLUMNS, Transaction


def export_transactions_to_csv(transactions: list[Transaction], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANONICAL_COLUMNS)
        writer.writeheader()
        for tx in transactions:
            writer.writerow(tx.to_csv_row())


def load_transactions_from_csv(csv_file: Path) -> list[Transaction]:
    with csv_file.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [Transaction.from_csv_row(row) for row in reader]
