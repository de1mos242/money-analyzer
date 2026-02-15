from __future__ import annotations

import re

from money_analyzer.models import Transaction
from money_analyzer.parsing.base import ParseResult, StatementParser
from money_analyzer.parsing.parsers.common import (
    contains_keywords,
    split_non_empty_lines,
)
from money_analyzer.utils import parse_amount, parse_date


class N26Parser(StatementParser):
    parser_id = "n26"
    bank_name = "N26"
    detection_keywords = (
        "n26",
        "n26 bank",
        "dein n26 team",
        "vorlaufiger kontoauszug",
        "ntsbdeb1xxx",
    )
    amount_pattern = r"[+-]?(?:\d{1,3}(?:[. ]\d{3})*|\d+)(?:,\d{2})?"
    booking_line_pattern = re.compile(
        r"^(?P<date>\d{2}[./]\d{2}[./]\d{4})\s+"
        rf"(?P<amount>{amount_pattern})\s*(?P<currency>EUR|€)?$"
    )
    single_line_pattern = re.compile(
        r"^(?P<date>\d{2}[./]\d{2}[./]\d{4})\s+"
        r"(?P<description>.+?)\s+"
        rf"(?P<amount>{amount_pattern})\s*(?P<currency>EUR|€)?$"
    )
    value_date_pattern = re.compile(
        r"^Wertstellung\s+(?P<posted_date>\d{2}[./]\d{2}[./]\d{4})$"
    )
    date_range_pattern = re.compile(r"^\d{2}[./]\d{2}[./]\d{4}\s+bis\s+\d{2}[./]\d{2}[./]\d{4}$")
    page_pattern = re.compile(r"^\d+\s*/\s*\d+$")
    date_only_pattern = re.compile(r"^\d{2}[./]\d{2}[./]\d{4}$")
    ignored_prefixes = (
        "mastercard",
        "iban:",
        "bic:",
        "wertstellung",
        "vorlaufiger kontoauszug",
        "vorlaufiger space kontoauszug",
        "dein alter kontostand",
        "ausgehende transaktionen",
        "einkommende transaktionen",
        "dein neuer kontostand",
        "space:",
        "datum geoffnet:",
        "erstellt am",
    )
    ignored_exact_lines = {
        "beschreibung",
        "beschreibung verbuchungsdatum betrag",
        "lastschriften",
        "gutschriften",
        "belastungen",
        "zusammenfassung",
        "spaces zusammenfassung",
        "anmerkung",
    }

    def can_parse(self, text: str, file_name: str = "") -> bool:
        return contains_keywords(text + " " + file_name, self.detection_keywords)

    def parse_text(self, text: str, source_file: str = "") -> ParseResult:
        result = ParseResult(parser_id=self.parser_id, source_file=source_file)
        lines = split_non_empty_lines(text)
        previous_booking_index = -1

        for index, line in enumerate(lines):
            single_line_match = self.single_line_pattern.match(line)
            if single_line_match:
                groups = single_line_match.groupdict()
                description = " ".join(groups["description"].split())
                result.transactions.append(
                    Transaction(
                        date=parse_date(groups["date"]),
                        amount=parse_amount(groups["amount"]),
                        currency=(groups.get("currency") or "EUR").replace("€", "EUR"),
                        account_name=self.bank_name,
                        description=description,
                        merchant=description,
                        source_file=source_file,
                        parser_id=self.parser_id,
                        confidence=0.9,
                    )
                )
                previous_booking_index = index
                continue

            booking_match = self.booking_line_pattern.match(line)
            if not booking_match:
                continue

            posted_date = None
            description_search_end = index - 1
            if index > 0:
                value_date_match = self.value_date_pattern.match(lines[index - 1])
                if value_date_match:
                    posted_date = parse_date(value_date_match.group("posted_date"))
                    description_search_end = index - 2

            description = self._find_description(
                lines,
                start=previous_booking_index + 1,
                end=description_search_end,
            )
            previous_booking_index = index
            if not description:
                continue

            groups = booking_match.groupdict()
            result.transactions.append(
                Transaction(
                    date=parse_date(groups["date"]),
                    posted_date=posted_date,
                    amount=parse_amount(groups["amount"]),
                    currency=(groups.get("currency") or "EUR").replace("€", "EUR"),
                    account_name=self.bank_name,
                    description=description,
                    merchant=description,
                    source_file=source_file,
                    parser_id=self.parser_id,
                    confidence=0.9,
                )
            )

        if not result.transactions:
            result.warnings.append("No transactions parsed from statement")
        return result

    @classmethod
    def _find_description(cls, lines: list[str], start: int, end: int) -> str | None:
        if end < start:
            return None

        table_header_index = None
        for index in range(start, end + 1):
            normalized = cls._normalize(lines[index])
            if normalized == "beschreibung verbuchungsdatum betrag":
                table_header_index = index

        description_start = (table_header_index + 1) if table_header_index is not None else start
        for index in range(description_start, end + 1):
            candidate = lines[index].strip()
            if candidate and not cls._is_ignored_line(candidate):
                return " ".join(candidate.split())
        return None

    @classmethod
    def _is_ignored_line(cls, line: str) -> bool:
        normalized = cls._normalize(line)
        if normalized in cls.ignored_exact_lines:
            return True
        if cls.date_range_pattern.match(line):
            return True
        if cls.page_pattern.match(line):
            return True
        if cls.date_only_pattern.match(line):
            return True
        if normalized.startswith(("/", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9")):
            return True
        return normalized.startswith(cls.ignored_prefixes)

    @staticmethod
    def _normalize(value: str) -> str:
        return value.strip().lower().replace("ä", "a").replace("ö", "o").replace("ü", "u")
