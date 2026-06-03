#!/usr/bin/env python3
"""ASN Label Generator – 30 × 15 mm labels with QR code."""

import argparse
import io

import qrcode
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

LABEL_W = 30 * mm
LABEL_H = 15 * mm


def asn_str(n: int) -> str:
    return f"ASN{n:05d}"


def make_qr(text: str) -> ImageReader:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def build_pdf(numbers: list[int], output: str) -> None:
    c = canvas.Canvas(output, pagesize=(LABEL_W, LABEL_H))

    for n in numbers:
        label = asn_str(n)
        qr_img = make_qr(label)

        pad = 1 * mm
        qr_size = LABEL_H - 2 * pad  # 13 mm Quadrat

        # QR-Code links
        c.drawImage(qr_img, pad, pad, width=qr_size, height=qr_size)

        # Text rechts
        text_x = qr_size + 2 * pad
        text_w = LABEL_W - text_x - pad
        cx = text_x + text_w / 2

        c.setFont("Helvetica-Bold", 5.5)
        c.drawCentredString(cx, LABEL_H / 2 + 1.5 * mm, "ASN")

        c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(cx, LABEL_H / 2 - 3 * mm, f"{n:05d}")

        c.showPage()

    c.save()


def main() -> None:
    p = argparse.ArgumentParser(
        description="ASN-Labels (30 × 15 mm) als PDF erzeugen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python asn_labels.py 1 100              # ASN00001 bis ASN00100 vorwärts
  python asn_labels.py 1 100 --reverse    # 100→1, beim Abrollen beginnt die Rolle mit 00001
  python asn_labels.py 1 50 -o regal.pdf  # eigene Ausgabedatei
        """,
    )
    p.add_argument("start", type=int, help="Erste ASN-Nummer")
    p.add_argument("end", type=int, help="Letzte ASN-Nummer")
    p.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="Umgekehrte Reihenfolge drucken (Rolle beginnt vorne mit der kleinsten Nummer)",
    )
    p.add_argument(
        "-o",
        "--output",
        default="asn_labels.pdf",
        help="Ausgabedatei (Standard: asn_labels.pdf)",
    )
    args = p.parse_args()

    if args.start > args.end:
        p.error("start muss ≤ end sein")

    numbers = list(range(args.start, args.end + 1))
    if args.reverse:
        numbers.reverse()

    build_pdf(numbers, args.output)

    count = len(numbers)
    order = "umgekehrt (Rolle: vorne = kleinste Nummer)" if args.reverse else "vorwärts"
    print(f"✓  {count} Label ({order})  →  {args.output}")


if __name__ == "__main__":
    main()
