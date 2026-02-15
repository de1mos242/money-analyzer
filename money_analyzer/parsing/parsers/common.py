from __future__ import annotations

import re
from collections.abc import Iterable

from money_analyzer.models import Transaction
from money_analyzer.utils import parse_amount, parse_date


def split_non_empty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def contains_keywords(text: str, keywords: Iterable[str]) -> bool:
    haystack = text.lower()
    return any(keyword.lower() in haystack for keyword in keywords)


def parse_transaction_line(
    line: str,
    pattern: re.Pattern[str],
    account_name: str,
    source_file: str,
    parser_id: str,
) -> Transaction | None:
    match = pattern.search(line)
    if not match:
        return None
    groups = match.groupdict()
    description = " ".join(groups["description"].split())
    merchant = groups.get("merchant") or description
    return Transaction(
        date=parse_date(groups["date"]),
        posted_date=parse_date(groups["posted_date"]) if groups.get("posted_date") else None,
        amount=parse_amount(groups["amount"]),
        currency=(groups.get("currency") or "EUR").replace("€", "EUR"),
        account_name=account_name,
        description=description,
        merchant=merchant,
        source_file=source_file,
        parser_id=parser_id,
        confidence=0.9,
    )
