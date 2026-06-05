#!/usr/bin/env python3
"""ASN Label Generator – 30 × 15 mm labels with QR code."""

import argparse
import io
import math

import qrcode
from reportlab.lib.units import mm, inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

LABEL_W = 30 * mm
LABEL_H = 15 * mm

SHEET_W = 4 * inch   # 4 Zoll Breite
SHEET_H = 6 * inch   # 6 Zoll Höhe
SHEET_MARGIN = 2 * mm


def asn_str(n: int) -> str:
    return f"ASN{n:05d}"


def make_qr(text: str) -> ImageReader:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=0,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def draw_label(c: canvas.Canvas, n: int, x: float, y: float) -> None:
    """Zeichnet ein einzelnes Label an Position (x, y) – untere linke Ecke."""
    label = asn_str(n)
    qr_img = make_qr(label)

    pad = 1.2 * mm
    qr_size = LABEL_H - 2 * pad

    c.drawImage(qr_img, x + pad, y + pad, width=qr_size, height=qr_size)

    text_x = x + qr_size + 2 * pad
    text_w = LABEL_W - (qr_size + 3 * pad)
    cx = text_x + text_w / 2

    c.setFont("Helvetica-Bold", 5.5)
    c.drawCentredString(cx, y + LABEL_H / 2 + 1.5 * mm, "ASN")

    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(cx, y + LABEL_H / 2 - 3 * mm, f"{n:05d}")


def build_pdf(numbers: list[int], output: str) -> None:
    """Ein Label pro Seite – für den Rollendrucker."""
    c = canvas.Canvas(output, pagesize=(LABEL_W, LABEL_H))
    for n in numbers:
        draw_label(c, n, 0, 0)
        c.showPage()
    c.save()


def build_sheet_pdf(numbers: list[int], output: str) -> None:
    """Mehrere Labels pro Seite auf einem 4 × 6 Zoll Testblatt."""
    usable_w = SHEET_W - 2 * SHEET_MARGIN
    usable_h = SHEET_H - 2 * SHEET_MARGIN

    cols = int(usable_w // LABEL_W)
    rows = int(usable_h // LABEL_H)
    per_page = cols * rows

    # Labels horizontal zentrieren
    grid_w = cols * LABEL_W
    offset_x = (SHEET_W - grid_w) / 2

    pages = math.ceil(len(numbers) / per_page)
    c = canvas.Canvas(output, pagesize=(SHEET_W, SHEET_H))

    for page in range(pages):
        chunk = numbers[page * per_page : (page + 1) * per_page]

        for i, n in enumerate(chunk):
            col = i % cols
            row = i // cols
            x = offset_x + col * LABEL_W
            # Von oben nach unten: erstes Label oben
            y = SHEET_H - SHEET_MARGIN - (row + 1) * LABEL_H
            draw_label(c, n, x, y)

            # Schnittlinien
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.setLineWidth(0.2)
            c.rect(x, y, LABEL_W, LABEL_H)

        c.showPage()

    c.save()
    print(f"  Raster: {cols} Spalten × {rows} Zeilen = {per_page} Labels/Seite, {pages} Seite(n)")


def main() -> None:
    p = argparse.ArgumentParser(
        description="ASN-Labels (30 × 15 mm) als PDF erzeugen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python asn_labels.py 1 100                        # Rollendrucker: 1 Label/Seite
  python asn_labels.py 1 100 --reverse              # umgekehrte Reihenfolge für Rolle
  python asn_labels.py 1 100 --sheet                # Testblatt 4×6 Zoll, mehrere Labels/Seite
  python asn_labels.py 1 50 -o regal.pdf --sheet    # eigene Ausgabedatei
        """,
    )
    p.add_argument("start", type=int, help="Erste ASN-Nummer")
    p.add_argument("end", type=int, help="Letzte ASN-Nummer")
    p.add_argument(
        "-r", "--reverse",
        action="store_true",
        help="Umgekehrte Reihenfolge (Rolle beginnt vorne mit der kleinsten Nummer)",
    )
    p.add_argument(
        "-s", "--sheet",
        action="store_true",
        help="Testblatt-Modus: mehrere Labels auf 4 × 6 Zoll Seite",
    )
    p.add_argument(
        "-o", "--output",
        default=None,
        help="Ausgabedatei (Standard: asn_labels.pdf / asn_testblatt.pdf)",
    )
    args = p.parse_args()

    if args.start > args.end:
        p.error("start muss ≤ end sein")

    numbers = list(range(args.start, args.end + 1))
    if args.reverse:
        numbers.reverse()

    if args.sheet:
        output = args.output or "asn_testblatt.pdf"
        build_sheet_pdf(numbers, output)
        order = "umgekehrt" if args.reverse else "vorwärts"
        print(f"✓  {len(numbers)} Labels ({order}) auf Testblatt (4×6 Zoll)  →  {output}")
    else:
        output = args.output or "asn_labels.pdf"
        build_pdf(numbers, output)
        order = "umgekehrt (Rolle: vorne = kleinste Nummer)" if args.reverse else "vorwärts"
        print(f"✓  {len(numbers)} Label ({order})  →  {output}")


if __name__ == "__main__":
    main()
