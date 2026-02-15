from __future__ import annotations

from pathlib import Path

from money_analyzer.parsing.parsers.n26 import N26Parser


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "statements_pdf"


def test_n26_parser_parse_pdf_with_synthetic_document() -> None:
    pdf_path = FIXTURES_DIR / "n26_synthetic_statement.pdf"
    result = N26Parser().parse_pdf(pdf_path)
    rows = [tx.to_csv_row() for tx in result.transactions]

    assert len(rows) == 2
    assert rows[0]["date"] == "2026-01-01"
    assert rows[0]["description"] == "Grocery Store"
    assert rows[0]["amount"] == "-42.33"
    assert rows[1]["date"] == "2026-01-02"
    assert rows[1]["description"] == "Salary January"
    assert rows[1]["amount"] == "2500.00"


def test_n26_parser_parse_pdf_with_synthetic_multiline_structure() -> None:
    pdf_path = FIXTURES_DIR / "n26_synthetic_multiline_statement.pdf"
    result = N26Parser().parse_pdf(pdf_path)
    rows = [tx.to_csv_row() for tx in result.transactions]

    assert len(rows) == 3
    assert rows[0]["date"] == "2026-01-03"
    assert rows[0]["posted_date"] == "2026-01-03"
    assert rows[0]["description"] == "NORTH STAR SUPERMARKET"
    assert rows[0]["amount"] == "-41.27"
    assert rows[1]["date"] == "2026-01-04"
    assert rows[1]["posted_date"] == "2026-01-04"
    assert rows[1]["description"] == "BLUE RIVER ELECTRIC"
    assert rows[1]["amount"] == "-87.45"
    assert rows[2]["date"] == "2026-01-04"
    assert rows[2]["posted_date"] == "2026-01-04"
    assert rows[2]["description"] == "From Rainy Day Space"
    assert rows[2]["amount"] == "520.00"
