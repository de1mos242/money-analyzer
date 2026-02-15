from __future__ import annotations

from pathlib import Path


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf_with_text_lines(lines: list[str]) -> bytes:
    content_parts = ["BT", "/F1 12 Tf", "36 780 Td"]
    for index, line in enumerate(lines):
        if index > 0:
            content_parts.append("0 -16 Td")
        content_parts.append(f"({_escape_pdf_text(line)}) Tj")
    content_parts.append("ET")
    stream = ("\n".join(content_parts) + "\n").encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010} 00000 n \n".encode("ascii"))

    pdf.extend(b"trailer\n")
    pdf.extend(f"<< /Size {len(offsets)} /Root 1 0 R >>\n".encode("ascii"))
    pdf.extend(b"startxref\n")
    pdf.extend(f"{xref_offset}\n".encode("ascii"))
    pdf.extend(b"%%EOF\n")
    return bytes(pdf)


def generate_fixtures(output_dir: Path) -> None:
    fixtures: dict[str, list[str]] = {
        "n26_synthetic_statement.pdf": [
            "N26 Bank",
            "Kontoauszug Januar",
            "01.01.2026 Grocery Store -42,33 EUR",
            "02.01.2026 Salary January 2500,00 EUR",
        ],
        "n26_synthetic_multiline_statement.pdf": [
            "ALEX EXAMPLE",
            "Sampleweg 42, 10115 Berlin",
            "IBAN: DE00999900001111222233 - BIC: NTSBDEB1XXX",
            "Erstellt am",
            "26.01.2026",
            "1 / 1",
            "Beschreibung Verbuchungsdatum Betrag",
            "NORTH STAR SUPERMARKET",
            "Mastercard - Groceries",
            "Wertstellung 03.01.2026",
            "03.01.2026 -41,27 EUR",
            "BLUE RIVER ELECTRIC",
            "Lastschriften",
            "IBAN: DE00888877776666555544 - BIC: TESTDEFFXXX",
            "Abo Januar 2026",
            "Wertstellung 04.01.2026",
            "04.01.2026 -87,45 EUR",
            "From Rainy Day Space",
            "Wertstellung 04.01.2026",
            "04.01.2026 +520,00 EUR",
            "Vorlaeufiger Kontoauszug",
            "01.01.2026 bis 26.01.2026",
        ],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, lines in fixtures.items():
        (output_dir / filename).write_bytes(_build_pdf_with_text_lines(lines))


if __name__ == "__main__":
    generate_fixtures(Path(__file__).parent / "statements_pdf")
