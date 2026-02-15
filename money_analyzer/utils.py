from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal


def parse_date(value: str) -> date:
    value = value.strip()
    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def parse_iso_date(value: str) -> date:
    return datetime.strptime(value.strip(), "%Y-%m-%d").date()


def parse_amount(value: str) -> Decimal:
    raw = value.strip().replace("EUR", "").replace("€", "").replace(" ", "")
    if raw.endswith("-"):
        raw = f"-{raw[:-1]}"
    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        raw = raw.replace(",", ".")
    return Decimal(raw)
