from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from money_analyzer.models import Transaction
from money_analyzer.parsing.pdf_text import extract_text_from_pdf


@dataclass(slots=True)
class ParseResult:
    parser_id: str
    source_file: str
    transactions: list[Transaction] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class StatementParser(ABC):
    parser_id: str
    bank_name: str

    @abstractmethod
    def can_parse(self, text: str, file_name: str = "") -> bool:
        raise NotImplementedError

    @abstractmethod
    def parse_text(self, text: str, source_file: str = "") -> ParseResult:
        raise NotImplementedError

    def parse_pdf(self, pdf_path: Path) -> ParseResult:
        text = extract_text_from_pdf(pdf_path)
        return self.parse_text(text, source_file=pdf_path.name)
