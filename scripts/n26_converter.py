#!/usr/bin/env python3
"""
Convert N26 PDF account statements to CSV, using integer cents internally.

Defaults (so it can run with no parameters):
- input folder:  ../inputs   (all *.pdf inside)
- output folder: ../outputs  (CSV files written there)

CSV columns:
- Date
- Amount (formatted as +/-1234.56 with '.' decimal separator)
- Merchant
- Type (card|sepa)
- Category
- Sender
- Additional payment info

Examples:
  python n26_pdf_to_csv.py
  python n26_pdf_to_csv.py --input-dir ../inputs --output-dir ../outputs
  python n26_pdf_to_csv.py ../inputs/January.pdf
  python n26_pdf_to_csv.py ../inputs/*.pdf --output-dir ../outputs
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import re
from dataclasses import dataclass
from typing import List, Tuple

import pdfplumber


MERCHANT_LINE_RE = re.compile(
    r"^(?P<merchant>.+?)\s+(?P<date>\d{2}\.\d{2}\.\d{4})\s+(?P<amt>[+-]?\d[\d\.]*,\d{2})€$"
)
DATE_RANGE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}\s+bis\s+\d{2}\.\d{2}\.\d{4}$")
PAGE_NO_RE = re.compile(r"^\d+\s*/\s*\d+$")

SEPA_TYPE_WORDS = {"Lastschriften", "Belastungen", "Gutschriften"}


@dataclass
class Txn:
    date: str
    amount_cents: int
    merchant: str
    typ: str
    category: str
    sender: str
    additional_info: str


def parse_amount_de_to_cents(s: str) -> int:
    """
    German formatted amount like "-2.136,17" -> -213617 (cents)
    """
    s = s.strip()
    sign = -1 if s.startswith("-") else 1
    if s and s[0] in "+-":
        s = s[1:]

    s = s.replace(".", "")
    if "," not in s:
        euros = int(re.sub(r"\D", "", s) or "0")
        cents = 0
    else:
        euros_str, cents_str = s.split(",", 1)
        euros = int(re.sub(r"\D", "", euros_str) or "0")
        cents_digits = re.sub(r"\D", "", cents_str)
        if len(cents_digits) == 0:
            cents = 0
        elif len(cents_digits) == 1:
            cents = int(cents_digits) * 10
        else:
            cents = int(cents_digits[:2])

    return sign * (euros * 100 + cents)


def format_cents_to_eur(cents: int) -> str:
    """
    -213617 -> "-2136.17"
    """
    sign = "-" if cents < 0 else ""
    v = abs(cents)
    euros = v // 100
    c = v % 100
    return f"{sign}{euros}.{c:02d}"


def extract_all_lines(pdf_path: str) -> List[str]:
    lines: List[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            for l in txt.splitlines():
                l = l.strip()
                if l:
                    lines.append(l)
    return lines


def extract_sender(lines: List[str]) -> str:
    for l in lines[:80]:
        if "Erstellt am" in l:
            candidate = l.split("Erstellt am", 1)[0].strip()
            if len(candidate) >= 3:
                return candidate
    for l in lines[:80]:
        if re.fullmatch(r"[A-ZÄÖÜß][A-ZÄÖÜß ]{2,}", l):
            return l.strip()
    return ""


def is_noise_line(line: str) -> bool:
    if not line:
        return True
    if line == "Beschreibung Verbuchungsdatum Betrag":
        return True
    if line.startswith(
            (
                    "Vorläufiger Kontoauszug",
                    "Kontoauszug",
                    "Zusammenfassung",
                    "Spaces Zusammenfassung",
                    "Vorläufiger Space Kontoauszug",
            )
    ):
        return True
    if DATE_RANGE_RE.match(line):
        return True
    if PAGE_NO_RE.match(line):
        return True
    if line.startswith(
            (
                    "Dein alter Kontostand",
                    "Ausgehende Transaktionen",
                    "Einkommende Transaktionen",
                    "Dein neuer Kontostand",
                    "Space:",
                    "Datum geöffnet:",
            )
    ):
        return True
    if "Erstellt am" in line:
        return True
    if line.startswith("Friedenauer Höhe"):
        return True
    if line.startswith("IBAN: DE3110") and "BIC:" in line:
        return True
    return False


def classify(details: List[str], merchant: str) -> Tuple[str, str, str]:
    mc_line = next((d for d in details if "Mastercard" in d), None)
    if mc_line:
        typ = "card"
        category = ""
        if "•" in mc_line:
            category = mc_line.split("•", 1)[1].strip()

        additional = []
        for d in details:
            if d == mc_line or d.startswith("Wertstellung"):
                continue
            additional.append(d)
        return typ, category, " | ".join(additional).strip()

    typ = "sepa"
    sepa_kind = next((d for d in details if d in SEPA_TYPE_WORDS), None)
    if sepa_kind:
        category = sepa_kind
    elif merchant.startswith("An ") or merchant.startswith("Von "):
        category = "Transfer"
    else:
        category = ""

    additional = []
    for d in details:
        if d.startswith("Wertstellung"):
            continue
        if sepa_kind and d == sepa_kind:
            continue
        additional.append(d)

    return typ, category, " | ".join(additional).strip()


def parse_transactions_from_lines(lines: List[str], sender: str) -> List[Txn]:
    txns: List[Txn] = []
    i, n = 0, len(lines)

    while i < n:
        line = lines[i].strip()
        m = MERCHANT_LINE_RE.match(line)
        if m and not is_noise_line(line):
            merchant = m.group("merchant").strip()
            date = m.group("date")
            amount_cents = parse_amount_de_to_cents(m.group("amt"))

            details: List[str] = []
            i += 1
            while i < n:
                nxt = lines[i].strip()
                if MERCHANT_LINE_RE.match(nxt) and not is_noise_line(nxt):
                    break
                if not is_noise_line(nxt):
                    details.append(nxt)
                i += 1

            typ, category, additional = classify(details, merchant)
            txns.append(Txn(date, amount_cents, merchant, typ, category, sender, additional))
        else:
            i += 1

    return txns


def write_csv(txns: List[Txn], out_csv: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(out_csv)) or ".", exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Amount", "Merchant", "Type", "Category", "Sender", "Additional payment info"])
        for t in txns:
            w.writerow(
                [
                    t.date,
                    format_cents_to_eur(t.amount_cents),
                    t.merchant,
                    t.typ,
                    t.category,
                    t.sender,
                    t.additional_info,
                ]
            )


def expand_inputs(pdfs: List[str], input_dir: str) -> List[str]:
    """
    If explicit pdf patterns/paths are provided, expand them.
    Otherwise default to input_dir/*.pdf.
    """
    patterns = pdfs if pdfs else [os.path.join(input_dir, "*.pdf")]

    paths: List[str] = []
    for p in patterns:
        expanded = glob.glob(p)
        if expanded:
            paths.extend(expanded)
        else:
            # treat as literal path
            paths.append(p)

    seen = set()
    uniq: List[str] = []
    for p in paths:
        ap = os.path.abspath(p)
        if ap not in seen and ap.lower().endswith(".pdf") and os.path.exists(ap):
            seen.add(ap)
            uniq.append(ap)
    return uniq


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "pdfs",
        nargs="*",
        help="Optional PDF path(s) or glob pattern(s). If omitted, uses --input-dir/*.pdf",
    )
    ap.add_argument("--input-dir", default="../inputs", help="Default input folder when no PDFs are specified")
    ap.add_argument("--output-dir", default="../outputs", help="Output folder for CSV files")
    ap.add_argument("--out", help="Output CSV file (only when exactly 1 PDF is given)")
    args = ap.parse_args()

    pdf_paths = expand_inputs(args.pdfs, args.input_dir)
    if not pdf_paths:
        raise SystemExit(f"No PDF files found (looked in {os.path.abspath(args.input_dir)}).")

    if args.out and len(pdf_paths) != 1:
        raise SystemExit("--out can be used only with exactly one input PDF. Use --output-dir for multiple PDFs.")

    os.makedirs(args.output_dir, exist_ok=True)

    for pdf_path in pdf_paths:
        lines = extract_all_lines(pdf_path)
        sender = extract_sender(lines)
        txns = parse_transactions_from_lines(lines, sender)

        if args.out:
            out_csv = args.out
        else:
            base = os.path.splitext(os.path.basename(pdf_path))[0]
            out_csv = os.path.join(args.output_dir, f"{base}.csv")

        write_csv(txns, out_csv)
        print(f"Wrote {len(txns)} transactions -> {out_csv}")


if __name__ == "__main__":
    main()
