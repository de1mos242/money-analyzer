from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


CANONICAL_COLUMNS = [
    "date",
    "posted_date",
    "amount",
    "currency",
    "account_id",
    "account_name",
    "transaction_type",
    "description",
    "merchant",
    "category",
    "source_file",
    "parser_id",
    "confidence",
]


@dataclass(slots=True)
class Transaction:
    date: date
    amount: Decimal
    currency: str
    account_name: str
    description: str
    posted_date: date | None = None
    account_id: str = ""
    transaction_type: str = ""
    merchant: str = ""
    category: str = ""
    source_file: str = ""
    parser_id: str = ""
    confidence: float = 1.0

    def to_csv_row(self) -> dict[str, str]:
        return {
            "date": self.date.isoformat(),
            "posted_date": self.posted_date.isoformat() if self.posted_date else "",
            "amount": f"{self.amount:.2f}",
            "currency": self.currency,
            "account_id": self.account_id,
            "account_name": self.account_name,
            "transaction_type": self.transaction_type,
            "description": self.description,
            "merchant": self.merchant,
            "category": self.category,
            "source_file": self.source_file,
            "parser_id": self.parser_id,
            "confidence": f"{self.confidence:.2f}",
        }

    @staticmethod
    def from_csv_row(row: dict[str, str]) -> "Transaction":
        from .utils import parse_amount, parse_iso_date

        return Transaction(
            date=parse_iso_date(row["date"]),
            posted_date=parse_iso_date(row["posted_date"]) if row.get("posted_date") else None,
            amount=parse_amount(row["amount"]),
            currency=row.get("currency", "EUR"),
            account_id=row.get("account_id", ""),
            account_name=row.get("account_name", ""),
            transaction_type=row.get("transaction_type", ""),
            description=row.get("description", ""),
            merchant=row.get("merchant", ""),
            category=row.get("category", ""),
            source_file=row.get("source_file", ""),
            parser_id=row.get("parser_id", ""),
            confidence=float(row.get("confidence", "1.0") or "1.0"),
        )

    def fingerprint(self) -> tuple[str, ...]:
        return (
            self.date.isoformat(),
            f"{self.amount:.2f}",
            self.currency,
            self.account_id,
            self.account_name,
            self.description.strip().lower(),
            self.merchant.strip().lower(),
        )
