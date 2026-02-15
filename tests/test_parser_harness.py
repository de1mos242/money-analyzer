from __future__ import annotations

import csv
from pathlib import Path

from money_analyzer.parsing.parsers.c24 import C24Parser
from money_analyzer.parsing.parsers.n26 import N26Parser
from money_analyzer.parsing.parsers.vivid import VividParser
from money_analyzer.parsing.router import ParserRouter


FIXTURES = Path(__file__).parent / "fixtures"


def read_fixture(name: str) -> str:
    return (FIXTURES / "statements" / name).read_text(encoding="utf-8")


def read_expected_csv(name: str) -> list[dict[str, str]]:
    with (FIXTURES / "expected" / name).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_n26_parser_golden_fixture() -> None:
    parser = N26Parser()
    text = read_fixture("n26_sample.txt")

    result = parser.parse_text(text, source_file="n26_sample.pdf")

    rows = [tx.to_csv_row() for tx in result.transactions]
    assert rows == read_expected_csv("n26_sample.csv")


def test_c24_parser_golden_fixture() -> None:
    parser = C24Parser()
    text = read_fixture("c24_sample.txt")

    result = parser.parse_text(text, source_file="c24_sample.pdf")

    rows = [tx.to_csv_row() for tx in result.transactions]
    assert rows == read_expected_csv("c24_sample.csv")


def test_vivid_parser_golden_fixture() -> None:
    parser = VividParser()
    text = read_fixture("vivid_sample.txt")

    result = parser.parse_text(text, source_file="vivid_sample.pdf")

    rows = [tx.to_csv_row() for tx in result.transactions]
    assert rows == read_expected_csv("vivid_sample.csv")


def test_router_selects_correct_parser() -> None:
    router = ParserRouter()

    n26_parser = router.route(read_fixture("n26_sample.txt"), source_file="n26_jan.pdf")
    c24_parser = router.route(read_fixture("c24_sample.txt"), source_file="c24_jan.pdf")
    vivid_parser = router.route(read_fixture("vivid_sample.txt"), source_file="vivid_jan.pdf")

    assert n26_parser.parser_id == "n26"
    assert c24_parser.parser_id == "c24"
    assert vivid_parser.parser_id == "vivid"
