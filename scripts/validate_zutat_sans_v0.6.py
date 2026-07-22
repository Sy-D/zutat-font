#!/usr/bin/env python3
"""Regression checks for the Zutat Sans 0.6 production release."""

from __future__ import annotations

from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "build" / "zutat-font-v0.6"
STYLES = {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700}
REQUIRED_CODEPOINTS = {
    0x2022: "bullet",
    0x039B: "Lambda",
    0x03BB: "lambda",
    0x00C6: "AE",
    0x00E6: "ae",
    0x1E9E: "capital sharp S",
    0x3003: "ditto mark",
    0x1EA0: "Vietnamese uppercase",
    0x1EF9: "Vietnamese lowercase",
}


def shape(path: Path, value: str, features=None):
    data = path.read_bytes()
    face = hb.Face(data)
    font = hb.Font(face)
    font.scale = (face.upem, face.upem)
    buffer = hb.Buffer()
    buffer.add_str(value)
    buffer.guess_segment_properties()
    hb.shape(font, buffer, features or {})
    return [
        (font.get_glyph_name(info.codepoint), pos.x_advance, pos.x_offset, pos.y_offset)
        for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions)
    ]


def validate_style(style: str, weight: int) -> None:
    new_path = NEW / f"ZutatSans-{style}.ttf"
    new = TTFont(new_path)

    names = {record.nameID: record.toUnicode() for record in new["name"].names}
    assert names[1] == "Zutat Sans"
    assert names[2] == style
    assert names[5] == "Version 0.600"
    assert names[6] == f"ZutatSans-{style}"
    assert new["OS/2"].usWeightClass == weight
    assert new["OS/2"].usWinAscent >= new["head"].yMax
    assert new["OS/2"].usWinDescent >= -new["head"].yMin
    assert all(table in new for table in ("cvt ", "fpgm", "prep", "gasp", "GSUB", "GPOS"))

    cmap = new.getBestCmap()
    assert len(new.getGlyphOrder()) == 975
    assert len(cmap) == 728
    assert all(codepoint in cmap for codepoint in REQUIRED_CODEPOINTS)
    assert sum(1 for codepoint in cmap if 0x0400 <= codepoint <= 0x052F) == 134

    gdef_classes = new["GDEF"].table.GlyphClassDef.classDefs
    mark_glyphs = [name for name, glyph_class in gdef_classes.items() if glyph_class == 3]
    assert mark_glyphs
    assert all(new["hmtx"][name][0] == 0 for name in mark_glyphs)

    tabular = shape(new_path, "0123456789", {"tnum": True})
    assert len({item[1] for item in tabular}) == 1
    assert shape(new_path, "1", {"sups": True})[0][0] == "uni00B9"
    assert shape(new_path, "1", {"subs": True})[0][0] == "uni2081"
    assert shape(new_path, "1", {"numr": True})[0][0] == "one.numr"
    assert shape(new_path, "1", {"dnom": True})[0][0] == "one.dnom"
    assert [item[0] for item in shape(new_path, "1/2", {"frac": True})] == [
        "one.numr", "fraction", "two.dnom"
    ]

    kern_off = sum(item[1] for item in shape(new_path, "ÁV Tô Wā", {"kern": False}))
    kern_on = sum(item[1] for item in shape(new_path, "ÁV Tô Wā", {"kern": True}))
    assert kern_on != kern_off
    mark_shape = shape(new_path, "x\u0301")
    assert len(mark_shape) == 2
    assert any(item[2] or item[3] for item in mark_shape)
    assert mark_shape[1][1] == 0

    for extension in ("otf", "woff2"):
        font = TTFont(NEW / f"ZutatSans-{style}.{extension}")
        if extension == "woff2":
            assert all(table in font for table in ("cvt ", "fpgm", "prep", "gasp"))
        else:
            cff = font["CFF "].cff
            top = cff.topDictIndex[0]
            assert cff.fontNames[0] == f"ZutatSans-{style}"
            assert top.FamilyName == "Zutat Sans"

    print(f"PASS {style}: outlines, metrics, shaping, symbols, formats")


def main() -> None:
    for style, weight in STYLES.items():
        validate_style(style, weight)
    print("PASS Zutat Sans 0.6 production regression suite")


if __name__ == "__main__":
    main()
