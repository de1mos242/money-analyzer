from __future__ import annotations

import argparse
from pathlib import Path

from money_analyzer.csv_io import export_transactions_to_csv, load_transactions_from_csv
from money_analyzer.models import Transaction


def collect_csv_files(inputs: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in inputs:
        if path.is_dir():
            files.extend(sorted(path.glob("*.csv")))
        elif path.suffix.lower() == ".csv":
            files.append(path)
    return files


def combine_csv_files(csv_files: list[Path]) -> list[Transaction]:
    seen: set[tuple[str, ...]] = set()
    combined: list[Transaction] = []

    for csv_file in csv_files:
        for tx in load_transactions_from_csv(csv_file):
            fingerprint = tx.fingerprint()
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            combined.append(tx)

    combined.sort(key=lambda tx: (tx.date, tx.amount, tx.description.lower()))
    return combined


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Combine statement CSV files into one ledger")
    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help="Input CSV files or directories containing CSV files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/combined/transactions.csv"),
        help="Output combined CSV path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_files = collect_csv_files(args.inputs)
    if not csv_files:
        raise SystemExit("No CSV files found in inputs")
    combined = combine_csv_files(csv_files)
    export_transactions_to_csv(combined, args.output)
    print(f"Combined {len(csv_files)} file(s) into {args.output} ({len(combined)} rows)")


if __name__ == "__main__":
    main()
