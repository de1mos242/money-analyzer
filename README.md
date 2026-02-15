# money-analyzer

Family money analyzer focused on statement ingestion, normalization, and reconciliation.

## What is implemented

- PDF parser routing wrapper that auto-detects parser based on statement content.
- Bank statement parsers for N26, C24, and Vivid.
- Per-statement CSV export in a canonical schema.
- CSV combiner that merges many statement CSV files into one deduplicated ledger.
- Golden-fixture parser test harness.

## Canonical CSV schema

The generated CSV columns are:

`date, posted_date, amount, currency, account_id, account_name, transaction_type, description, merchant, category, source_file, parser_id, confidence`

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Parse PDF statements to CSV

```bash
money-ingest statements/n26_jan.pdf statements/c24_jan.pdf --out-dir output/parsed
```

This creates one CSV per statement file, with parser ID in the file name.

## Combine CSV files

```bash
money-combine output/parsed --output output/combined/transactions.csv
```

## Run tests

```bash
pytest
```
