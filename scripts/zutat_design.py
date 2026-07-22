"""Zutat Sans outline proportions and signature character system."""

from __future__ import annotations

import unicodedata

from fontTools.agl import toUnicode


X_HEIGHT_SOURCE = 530
X_HEIGHT_TARGET = 515
ASCENDER_TOP = 710
DESCENDER_SCALE = 1.08


def base_character(glyph_name: str) -> str:
    plain = glyph_name.split(".", 1)[0]
    try:
        value = toUnicode(plain)
        return value[0] if value else ""
    except Exception:
        return ""


def horizontal_scale(glyph_name: str) -> float:
    char = base_character(glyph_name)
    base = glyph_name.split(".", 1)[0]
    if base in {"S", "s"}:
        return 0.940
    if base in {"ampersand", "at"}:
        return 0.930
    if char in "MW":
        return 0.930
    if char in "mw":
        return 0.945
    if char in "CGOQU":
        return 0.958
    if char in "cosue":
        return 0.976
    if char in "rt":
        return 0.985
    category = unicodedata.category(char) if char else ""
    if category == "Lu":
        return 0.948
    if category == "Ll":
        return 0.968
    if category == "Nd":
        return 0.952
    if category.startswith("P"):
        return 0.935
    return 0.965


def is_lowercase_glyph(glyph_name: str) -> bool:
    char = base_character(glyph_name)
    return bool(char and unicodedata.category(char) == "Ll")


def map_y(y: float, lowercase: bool) -> float:
    if not lowercase:
        return y
    if y < 0:
        return y * DESCENDER_SCALE
    if y <= X_HEIGHT_SOURCE:
        return y * X_HEIGHT_TARGET / X_HEIGHT_SOURCE
    if y < ASCENDER_TOP:
        return X_HEIGHT_TARGET + (y - X_HEIGHT_SOURCE) * (
            ASCENDER_TOP - X_HEIGHT_TARGET
        ) / (ASCENDER_TOP - X_HEIGHT_SOURCE)
    return y


class WarpPen:
    def __init__(self, out_pen, glyph_name: str, scale: float, shift: float):
        self.out = out_pen
        self.base = glyph_name.split(".", 1)[0]
        self.scale = scale
        self.shift = shift
        self.lowercase = is_lowercase_glyph(glyph_name)
        self.contour = 0

    def point(self, point):
        if point is None:
            return None
        x, y = point
        original_y = y
        x = x * self.scale + self.shift
        y = map_y(y, self.lowercase)
        if self.base == "e" and self.contour == 1:
            y -= 11
        if self.base == "Q" and original_y < 0:
            x += 34 * min(1, abs(original_y) / 65)
        if self.base == "seven" and original_y > 650:
            x += 8
        return round(x), round(y)

    def moveTo(self, point):
        self.out.moveTo(self.point(point))

    def lineTo(self, point):
        self.out.lineTo(self.point(point))

    def curveTo(self, *points):
        self.out.curveTo(*(self.point(point) for point in points))

    def qCurveTo(self, *points):
        self.out.qCurveTo(*(self.point(point) for point in points))

    def closePath(self):
        self.out.closePath()
        self.contour += 1

    def endPath(self):
        self.out.endPath()
        self.contour += 1

    def addComponent(self, glyphName, transformation):
        raise RuntimeError("Components must be decomposed before warping")


def bake_character_system(font) -> None:
    glyphs = set(font.getGlyphOrder())
    direct = {
        "a": ".ss01",
        "G": ".ss06",
        "R": ".ss04",
        "I": ".ss05",
        "l": ".ss03",
        "one": ".ss09",
    }
    for table in font["cmap"].tables:
        for codepoint, original in list(table.cmap.items()):
            current = original
            for base, suffix in direct.items():
                if current == base or current.startswith(base):
                    candidate = current + suffix
                    if candidate in glyphs:
                        current = candidate
                    break
            square_dot = current + ".ss08"
            if square_dot in glyphs:
                current = square_dot
            table.cmap[codepoint] = current
