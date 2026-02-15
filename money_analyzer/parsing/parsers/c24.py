from __future__ import annotations

import re

from money_analyzer.parsing.base import ParseResult, StatementParser
from money_analyzer.parsing.parsers.common import (
    contains_keywords,
    parse_transaction_line,
    split_non_empty_lines,
)


class C24Parser(StatementParser):
    parser_id = "c24"
    bank_name = "C24"
    detection_keywords = ("c24", "c24 bank", "kontoauszug")
    line_pattern = re.compile(
        r"^(?P<date>\d{2}[./]\d{2}[./]\d{4})\s+"
        r"(?:(?P<posted_date>\d{2}[./]\d{2}[./]\d{4})\s+)?"
        r"(?P<description>.+?)\s+"
        r"(?P<amount>[+-]?\d[\d.,]*)\s*(?P<currency>EUR|€)?$"
    )

    def can_parse(self, text: str, file_name: str = "") -> bool:
        return contains_keywords(text + " " + file_name, self.detection_keywords)

    def parse_text(self, text: str, source_file: str = "") -> ParseResult:
        result = ParseResult(parser_id=self.parser_id, source_file=source_file)
        for line in split_non_empty_lines(text):
            tx = parse_transaction_line(
                line,
                pattern=self.line_pattern,
                account_name=self.bank_name,
                source_file=source_file,
                parser_id=self.parser_id,
            )
            if tx:
                result.transactions.append(tx)
        if not result.transactions:
            result.warnings.append("No transactions parsed from statement")
        return result
