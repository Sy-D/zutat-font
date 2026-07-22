#!/usr/bin/env python3
"""Render presentation and production-QA specimens for Zutat Sans 0.6."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "build" / "zutat-font-v0.6"
OUT = ROOT / "specimens"
BG, INK, MUTED, GREEN, LINE = "#F1EFE9", "#11120F", "#767970", "#28523D", "#CAC9C1"


def font(style, size):
    return ImageFont.truetype(str(FONTS / f"ZutatSans-{style}.ttf"), size=size)


def family_specimen():
    image = Image.new("RGB", (2200, 3000), BG)
    d = ImageDraw.Draw(image)

    def text(value, xy, style, size, fill=INK, features=None):
        d.text(xy, value, font=font(style, size), fill=fill, features=features)

    text("ZUTAT SANS / FAMILY 0.6", (100, 66), "Medium", 28, GREEN)
    text("PRODUCTION HARDENED", (1710, 66), "Regular", 26, MUTED)
    d.line((100, 126, 2100, 126), fill=LINE, width=2)
    text("Quiet authority,", (85, 180), "Regular", 205)
    text("made distinctive.", (85, 370), "Regular", 205)
    text("Precise without becoming cold. Distinct without noise.", (100, 665), "Regular", 42, MUTED)

    y = 820
    for style, weight in [("Regular", 400), ("Medium", 500), ("SemiBold", 600), ("Bold", 700)]:
        text(f"{style.upper()} / {weight}", (100, y), "Medium", 24, GREEN)
        text("Grace under pressure. Structure without sterility.", (100, y + 45), style, 68)
        y += 160

    d.rectangle((100, 1510, 2100, 2030), fill="#11130F")
    text("Time rewards clarity.", (160, 1580), "Regular", 122, "#F5F3ED")
    text("Built for language, interface, and identity.", (160, 1730), "Medium", 72, "#F5F3ED")
    text("Λ λ  Æ æ  ẞ ß  •  〃  Ä Ö Ü  0123456789", (160, 1900), "Regular", 52, "#AEB6AD")

    text("ABCDEFGHIJKLMNOPQRSTUVWXYZ", (100, 2160), "Medium", 52)
    text("abcdefghijklmnopqrstuvwxyz", (100, 2245), "Regular", 52)
    text("000 1010 1234567890", (100, 2330), "Regular", 52, features=["tnum"])
    text("TABULAR FIGURES / tnum", (1200, 2340), "Medium", 22, GREEN)

    d.line((100, 2470, 2100, 2470), fill=LINE, width=2)
    text("INTERFACE SAMPLE", (100, 2530), "Medium", 24, MUTED)
    text("Build with greater intention", (100, 2585), "SemiBold", 62)
    text("A restrained visual system can still own a recognizable voice.", (100, 2675), "Regular", 38, MUTED)
    d.rounded_rectangle((1650, 2550, 2100, 2685), radius=68, fill=GREEN)
    text("Continue  →", (1750, 2588), "Medium", 36, "#F5F3ED")

    path = OUT / "ZutatSans-Family-v0.6.png"
    image.save(path)
    return path


def qa_specimen():
    image = Image.new("RGB", (2400, 1900), BG)
    d = ImageDraw.Draw(image)
    d.text((100, 70), "ZUTAT SANS / 0.6 PRODUCTION QA", font=font("Medium", 28), fill=GREEN)
    d.text((100, 135), "Kerning, accents, figures, and vertical metrics", font=font("Regular", 64), fill=INK)
    d.line((100, 250, 2300, 250), fill=LINE, width=2)

    samples = [
        ("Regular", "ÁVATAR  Tô  Wā  À propos  minimum"),
        ("Medium", "ÄÖÜ  Æther  Straße  Λambda  λ"),
        ("SemiBold", "Grace under pressure — ẞ • 〃"),
        ("Bold", "Time rewards clarity. 2026"),
    ]
    y = 330
    for style, value in samples:
        d.text((100, y), style.upper(), font=font("Medium", 23), fill=GREEN)
        d.text((420, y - 20), value, font=font(style, 70), fill=INK)
        y += 160

    d.rectangle((100, 1040, 2300, 1740), fill="#11130F")
    d.text((155, 1100), "PROPORTIONAL", font=font("Medium", 22), fill="#84A18F")
    d.text((520, 1080), "000 1010 1234567890", font=font("Regular", 88), fill="#F5F3ED")
    d.text((155, 1250), "TABULAR / tnum", font=font("Medium", 22), fill="#84A18F")
    d.text((520, 1230), "000 1010 1234567890", font=font("Regular", 88), fill="#F5F3ED", features=["tnum"])
    d.text((155, 1400), "DIACRITICS", font=font("Medium", 22), fill="#84A18F")
    d.text((520, 1380), "À Á Â Ã Ä Å  Ç Ć Č  Ð Ñ Ő Œ", font=font("Regular", 72), fill="#F5F3ED")
    d.text((155, 1550), "CYRILLIC", font=font("Medium", 22), fill="#84A18F")
    d.text((520, 1530), "Беларуская Български Українська", font=font("Regular", 64), fill="#F5F3ED")

    path = OUT / "ZutatSans-v0.6-Production-QA.png"
    image.save(path)
    return path


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    print(family_specimen())
    print(qa_specimen())
