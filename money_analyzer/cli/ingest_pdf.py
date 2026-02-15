from __future__ import annotations

import argparse
from pathlib import Path

from money_analyzer.csv_io import export_transactions_to_csv
from money_analyzer.parsing.router import ParserNotFoundError, ParserRouter


def build_output_name(source_pdf: Path, parser_id: str) -> str:
    stem = source_pdf.stem.replace(" ", "_")
    return f"{stem}.{parser_id}.csv"


def run_ingest(pdf_files: list[Path], output_dir: Path) -> int:
    router = ParserRouter()
    output_dir.mkdir(parents=True, exist_ok=True)
    failures = 0

    for pdf_file in pdf_files:
        try:
            result, decision = router.parse_pdf(pdf_file)
            output_file = output_dir / build_output_name(pdf_file, decision.parser_id)
            export_transactions_to_csv(result.transactions, output_file)
            print(
                f"OK {pdf_file.name}: parser={decision.parser_id} "
                f"transactions={len(result.transactions)} output={output_file}"
            )
            for warning in result.warnings:
                print(f"WARN {pdf_file.name}: {warning}")
        except ParserNotFoundError as error:
            failures += 1
            print(f"ERROR {pdf_file.name}: {error}")
        except Exception as error:  # noqa: BLE001
            failures += 1
            print(f"ERROR {pdf_file.name}: failed to ingest ({error})")

    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse bank statements PDF files into CSV")
    parser.add_argument("pdfs", nargs="+", type=Path, help="Input PDF statement files")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("output/parsed"),
        help="Directory for per-statement CSV files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    failures = run_ingest(args.pdfs, args.out_dir)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
