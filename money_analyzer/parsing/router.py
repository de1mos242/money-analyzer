from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from money_analyzer.parsing.base import ParseResult, StatementParser
from money_analyzer.parsing.parsers.c24 import C24Parser
from money_analyzer.parsing.parsers.n26 import N26Parser
from money_analyzer.parsing.parsers.vivid import VividParser
from money_analyzer.parsing.pdf_text import extract_text_from_pdf


@dataclass(slots=True)
class RoutingDecision:
    parser_id: str
    source_file: str


class ParserNotFoundError(RuntimeError):
    pass


class ParserRouter:
    def __init__(self, parsers: list[StatementParser] | None = None) -> None:
        self.parsers = parsers or [N26Parser(), C24Parser(), VividParser()]

    def route(self, text: str, source_file: str = "") -> StatementParser:
        for parser in self.parsers:
            if parser.can_parse(text, source_file):
                return parser
        parser_ids = ", ".join(parser.parser_id for parser in self.parsers)
        raise ParserNotFoundError(
            f"No parser matched '{source_file}'. Available parsers: {parser_ids}"
        )

    def parse_pdf(self, pdf_path: Path) -> tuple[ParseResult, RoutingDecision]:
        text = extract_text_from_pdf(pdf_path)
        parser = self.route(text, source_file=pdf_path.name)
        result = parser.parse_text(text, source_file=pdf_path.name)
        decision = RoutingDecision(parser_id=parser.parser_id, source_file=pdf_path.name)
        return result, decision
