# ASN Label Maker

Erzeugt ASN-Labels (30 × 15 mm) mit QR-Code als druckfertiges PDF.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/boebelix/asn-maker/blob/main/asn_labels.ipynb)

---

## Label-Layout

```
┌──────────────────────────────┐
│ ▄▄▄▄  │  ASN               │  30 mm
│ █  █  │  00001             │
│ ▀▀▀▀  │                    │  15 mm
└──────────────────────────────┘
```

- **Links:** QR-Code (Inhalt: `ASN00001`)
- **Rechts:** Präfix `ASN` + 5-stellige Nummer mit führenden Nullen

---

## Installation

Benötigt [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
git clone https://github.com/boebelix/asn-maker.git
cd asn-maker
uv sync
```

---

## Verwendung

```bash
# ASN00001 bis ASN00100 – vorwärts
uv run python asn_labels.py 1 100

# Rückwärts drucken: Rolle beginnt nach dem Abrollen bei 00001
uv run python asn_labels.py 1 100 --reverse

# Eigene Ausgabedatei
uv run python asn_labels.py 1 50 -r -o regal_a.pdf
```

### Optionen

| Argument | Beschreibung |
|---|---|
| `start` | Erste ASN-Nummer |
| `end` | Letzte ASN-Nummer |
| `-r`, `--reverse` | Umgekehrte Reihenfolge (für Rollen-Druck) |
| `-o`, `--output` | Ausgabedatei (Standard: `asn_labels.pdf`) |

### Warum `--reverse`?

Beim Rollen-Druck landet das **zuletzt gedruckte** Label außen auf der Rolle – also als erstes beim Abrollen sichtbar. Mit `--reverse` wird `ASN00100` zuerst gedruckt und `ASN00001` zuletzt, sodass du beim Abrollen direkt bei `00001` anfängst.

---

## Drucken

Das PDF an den Labeldrucker schicken und im Treiber **30 × 15 mm** als Labelgröße einstellen. Jede PDF-Seite entspricht genau einem Label.

---

## Google Colab

Ja – du kannst das Skript direkt in Colab ausführen und das fertige PDF herunterladen.

Entweder über den Badge oben (sobald das Notebook im Repo liegt), oder manuell:

```python
# Zelle 1 – Abhängigkeiten installieren
!pip install -q qrcode[pil] reportlab Pillow

# Zelle 2 – Skript laden
!wget -q https://raw.githubusercontent.com/boebelix/asn-maker/main/asn_labels.py

# Zelle 3 – Labels erzeugen
!python asn_labels.py 1 100 --reverse -o asn_labels.pdf

# Zelle 4 – PDF herunterladen
from google.colab import files
files.download("asn_labels.pdf")
```
