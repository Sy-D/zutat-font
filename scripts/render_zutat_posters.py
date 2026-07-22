#!/usr/bin/env python3
"""Create deterministic Zutat Sans SVG posters and matching PNG previews."""

from __future__ import annotations

from pathlib import Path

import cairosvg
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "build" / "zutat-font-v0.6"
OUT = ROOT / "posters"


class VectorFont:
    """Shape text with HarfBuzz and emit the exact font outlines as SVG paths."""

    def __init__(self, style: str):
        self.path = FONTS / f"ZutatSans-{style}.ttf"
        data = self.path.read_bytes()
        self.face = hb.Face(data)
        self.hb_font = hb.Font(self.face)
        self.hb_font.scale = (self.face.upem, self.face.upem)
        self.tt_font = TTFont(self.path)
        self.glyph_set = self.tt_font.getGlyphSet()
        self.glyph_order = self.tt_font.getGlyphOrder()
        self.upem = self.face.upem

    def paths(
        self,
        value: str,
        x: float,
        baseline: float,
        size: float,
        fill: str,
        letter_spacing: float = 0,
        anchor: str = "start",
        opacity: float = 1,
    ) -> str:
        buffer = hb.Buffer()
        buffer.add_str(value)
        buffer.guess_segment_properties()
        hb.shape(self.hb_font, buffer)
        infos = buffer.glyph_infos
        positions = buffer.glyph_positions
        scale = size / self.upem
        total = sum(position.x_advance * scale for position in positions)
        total += max(0, len(positions) - 1) * letter_spacing
        cursor = x - total if anchor == "end" else x
        output = []

        for index, (info, position) in enumerate(zip(infos, positions)):
            glyph_name = self.glyph_order[info.codepoint]
            pen = SVGPathPen(self.glyph_set)
            self.glyph_set[glyph_name].draw(pen)
            commands = pen.getCommands()
            if commands:
                glyph_x = cursor + position.x_offset * scale
                glyph_y = baseline - position.y_offset * scale
                output.append(
                    f'<path d="{commands}" transform="translate({glyph_x:.3f} {glyph_y:.3f}) '
                    f'scale({scale:.7f} {-scale:.7f})" fill="{fill}" opacity="{opacity}"/>'
                )
            cursor += position.x_advance * scale
            if index < len(positions) - 1:
                cursor += letter_spacing
        return "\n".join(output)


REGULAR = VectorFont("Regular")
MEDIUM = VectorFont("Medium")
SEMIBOLD = VectorFont("SemiBold")
BOLD = VectorFont("Bold")


def minimal_svg() -> str:
    body = [
        "Zutat Sans combines quiet authority",
        "with editorial precision.",
        "Open forms, measured spacing,",
        "and restrained details create",
        "a voice that remains distinct",
        "without becoming loud.",
    ]
    body_paths = "\n".join(
        REGULAR.paths(line, 660, 91 + index * 31, 23, "#11120F")
        for index, line in enumerate(body)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1088" height="1408" viewBox="0 0 1088 1408">
  <rect width="1088" height="1408" fill="#F2F1EC"/>
  {SEMIBOLD.paths("ZUTAT SANS / 01", 72, 78, 15, "#28523D", letter_spacing=0.6)}
  {body_paths}
  <line x1="1008" y1="1002" x2="1008" y2="1286" stroke="#28523D" stroke-width="4"/>
  {SEMIBOLD.paths("Zutat", 495, 1116, 190, "#11120F", letter_spacing=-4)}
  {SEMIBOLD.paths("Sans", 620, 1287, 190, "#11120F", letter_spacing=-4)}
  {REGULAR.paths("REGULAR 400 — SEMIBOLD 600", 72, 1340, 14, "#777970", letter_spacing=0.3)}
  {REGULAR.paths("2026", 1008, 1340, 14, "#777970", anchor="end")}
</svg>'''


def scattered_svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1088" height="1408" viewBox="0 0 1088 1408">
  <rect width="1088" height="1408" fill="#B5B5B2"/>
  {SEMIBOLD.paths("Zutat Sans / 0.6", 72, 82, 18, "#11120F")}
  {SEMIBOLD.paths("Z72", 690, 154, 72, "#11120F")}
  {SEMIBOLD.paths("U48", 855, 235, 52, "#11120F")}
  {SEMIBOLD.paths("T32", 755, 332, 42, "#11120F")}
  {SEMIBOLD.paths("A24", 930, 382, 34, "#11120F")}
  {SEMIBOLD.paths("T18", 72, 434, 28, "#11120F")}
  {REGULAR.paths("Weight 600 / Optical size 72 / Tracking -2", 72, 472, 15, "#11120F")}

  <rect x="360" y="520" width="656" height="816" fill="#F1F0EB"/>
  {SEMIBOLD.paths("Z", 410, 708, 190, "#11120F")}
  {SEMIBOLD.paths("u", 720, 703, 128, "#11120F")}
  {SEMIBOLD.paths("t", 902, 703, 96, "#11120F")}
  {SEMIBOLD.paths("a", 410, 974, 150, "#11120F")}
  {SEMIBOLD.paths("t", 724, 968, 112, "#11120F")}
  {REGULAR.paths("Open forms. Measured spacing.", 410, 1085, 24, "#11120F")}
  {REGULAR.paths("Quiet authority without sterility.", 410, 1120, 24, "#11120F")}
  <line x1="410" y1="1176" x2="966" y2="1176" stroke="#A8A8A4" stroke-width="1"/>
  {REGULAR.paths("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 410, 1230, 21, "#777970")}
  {REGULAR.paths("abcdefghijklmnopqrstuvwxyz 0123456789", 410, 1262, 21, "#777970")}
  {REGULAR.paths("ÄÖÜ äöü ß  Ææ  Λλ  •  @ & ? →", 410, 1294, 21, "#777970")}
</svg>'''


def ingredients_svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1088" height="1408" viewBox="0 0 1088 1408">
  <rect width="1088" height="1408" fill="#153B2D"/>
  <line x1="72" y1="106" x2="1016" y2="106" stroke="#D9DDCF" stroke-width="1" opacity="0.35"/>
  <line x1="72" y1="1248" x2="1016" y2="1248" stroke="#D9DDCF" stroke-width="1" opacity="0.35"/>
  {MEDIUM.paths("ZUTAT SANS / INGREDIENTS", 72, 78, 15, "#D9DDCF", letter_spacing=0.7)}
  {REGULAR.paths("01", 1016, 78, 15, "#D9DDCF", anchor="end")}
  {BOLD.paths("FORM", 72, 360, 188, "#F3F0E7", letter_spacing=-5)}
  {REGULAR.paths("Open counters", 76, 414, 22, "#9DB5A5")}
  {BOLD.paths("RAUM", 260, 650, 188, "#F3F0E7", letter_spacing=-5)}
  {REGULAR.paths("Measured spacing", 264, 704, 22, "#9DB5A5")}
  {BOLD.paths("STIMME", 72, 940, 170, "#F3F0E7", letter_spacing=-5)}
  {REGULAR.paths("Restrained character", 76, 994, 22, "#9DB5A5")}
  <circle cx="930" cy="1124" r="74" fill="none" stroke="#C7D3C8" stroke-width="2"/>
  {SEMIBOLD.paths("Aa", 881, 1145, 58, "#F3F0E7", letter_spacing=-2)}
  {REGULAR.paths("400 / 500 / 600 / 700", 72, 1308, 16, "#D9DDCF", letter_spacing=0.3)}
  {REGULAR.paths("LATIN + CYRILLIC / UI + EDITORIAL", 1016, 1308, 16, "#D9DDCF", anchor="end")}
</svg>'''


def editorial_svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1088" height="1408" viewBox="0 0 1088 1408">
  <rect width="1088" height="1408" fill="#F0EDE4"/>
  <rect x="72" y="72" width="944" height="1264" fill="none" stroke="#BBB8AE" stroke-width="1"/>
  {MEDIUM.paths("ZUTAT / SPECIMEN 03", 100, 116, 14, "#38473D", letter_spacing=0.8)}
  {REGULAR.paths("A typeface is not decoration.", 100, 248, 42, "#11120F")}
  {REGULAR.paths("It is an ingredient.", 100, 300, 42, "#11120F")}
  <line x1="100" y1="374" x2="988" y2="374" stroke="#C85A3C" stroke-width="5"/>
  {SEMIBOLD.paths("Zutat", 92, 655, 246, "#11120F", letter_spacing=-7)}
  {SEMIBOLD.paths("Sans", 330, 875, 246, "#11120F", letter_spacing=-7)}
  {REGULAR.paths("Precise without becoming cold.", 100, 1030, 34, "#11120F")}
  {REGULAR.paths("Distinct without becoming loud.", 100, 1074, 34, "#11120F")}
  {REGULAR.paths("ÄÖÜ  Ææ  ẞß  0123456789", 100, 1198, 30, "#72736D")}
  {MEDIUM.paths("REGULAR", 100, 1290, 14, "#38473D", letter_spacing=0.6)}
  {MEDIUM.paths("MEDIUM", 348, 1290, 14, "#38473D", letter_spacing=0.6)}
  {MEDIUM.paths("SEMIBOLD", 584, 1290, 14, "#38473D", letter_spacing=0.6)}
  {MEDIUM.paths("BOLD", 876, 1290, 14, "#38473D", letter_spacing=0.6)}
</svg>'''


def glyph_field_svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1088" height="1408" viewBox="0 0 1088 1408">
  <rect width="1088" height="1408" fill="#10110F"/>
  <rect x="64" y="64" width="960" height="1280" rx="2" fill="#D9D7D0"/>
  <rect x="96" y="96" width="896" height="1216" fill="#10110F"/>
  {MEDIUM.paths("ZUTAT SANS / GLYPH FIELD", 128, 142, 14, "#A5B3A7", letter_spacing=0.7)}
  {BOLD.paths("Z", 118, 560, 480, "#F2EFE7")}
  {REGULAR.paths("a", 592, 554, 328, "#F2EFE7")}
  <line x1="128" y1="642" x2="960" y2="642" stroke="#718277" stroke-width="1"/>
  {SEMIBOLD.paths("A a", 128, 790, 118, "#F2EFE7", letter_spacing=-2)}
  {SEMIBOLD.paths("G g", 430, 790, 118, "#F2EFE7", letter_spacing=-2)}
  {SEMIBOLD.paths("R r", 730, 790, 118, "#F2EFE7", letter_spacing=-2)}
  {REGULAR.paths("minimum / rhythm / becoming", 128, 902, 38, "#C8CCC4")}
  {REGULAR.paths("000  1010  72  1.247,90", 128, 972, 38, "#C8CCC4")}
  {REGULAR.paths("Λ λ  Æ æ  ẞ ß  •  〃  →", 128, 1042, 38, "#C8CCC4")}
  <rect x="128" y="1134" width="832" height="2" fill="#718277"/>
  {REGULAR.paths("Quiet authority / editorial precision / restrained character", 128, 1208, 20, "#A5B3A7")}
  {MEDIUM.paths("0.6 / 2026", 960, 1260, 14, "#A5B3A7", anchor="end", letter_spacing=0.5)}
</svg>'''


def render_preview(svg_path: Path, png_path: Path) -> None:
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(png_path),
        output_width=1088,
        output_height=1408,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    posters = {
        "ZutatSans-Poster-Minimal": minimal_svg(),
        "ZutatSans-Poster-Scattered": scattered_svg(),
        "ZutatSans-Poster-Ingredients": ingredients_svg(),
        "ZutatSans-Poster-Editorial": editorial_svg(),
        "ZutatSans-Poster-Glyph-Field": glyph_field_svg(),
    }
    for name, source in posters.items():
        svg_path = OUT / f"{name}.svg"
        png_path = OUT / f"{name}.png"
        svg_path.write_text(source, encoding="utf-8")
        render_preview(svg_path, png_path)
        print(svg_path)
        print(png_path)


if __name__ == "__main__":
    main()
