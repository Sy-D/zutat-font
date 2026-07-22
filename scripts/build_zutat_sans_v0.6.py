#!/usr/bin/env python3
"""Build the production-hardened Zutat Sans 0.6 static family."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

import zutat_design as design

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "references" / "geist-font" / "fonts" / "Geist"
OUT = ROOT / "build" / "zutat-font-v0.6"

STYLES = {
    "Regular": {"source": "Regular", "weight": 400, "tracking": 14, "round_inset": 5, "m_rsb": 6},
    "Medium": {"source": "Medium", "weight": 500, "tracking": 10, "round_inset": 3, "m_rsb": 5},
    "SemiBold": {"source": "SemiBold", "weight": 600, "tracking": 6, "round_inset": 2, "m_rsb": 4},
    "Bold": {"source": "Bold", "weight": 700, "tracking": 3, "round_inset": 0, "m_rsb": 4},
}
VERSION = "0.600"
REVISION = 0.60


def set_names(font: TTFont, style: str, weight: int) -> None:
    postscript = f"ZutatSans-{style}"
    values = {
        1: "Zutat Sans",
        2: style,
        3: f"{VERSION};ZUTAT;{postscript}",
        4: f"Zutat Sans {style}",
        5: f"Version {VERSION}",
        6: postscript,
        8: "Simon Doba",
        9: "Vercel, basement.studio and contributors; custom cut by Simon Doba with OpenAI",
        10: "Zutat Sans editorial precision custom cut, derived from Geist under SIL OFL 1.1.",
        13: "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
        14: "https://openfontlicense.org",
        16: "Zutat Sans",
        17: style,
    }
    for record in font["name"].names:
        if record.nameID not in values:
            continue
        try:
            record.string = values[record.nameID].encode(record.getEncoding())
        except (LookupError, UnicodeEncodeError):
            record.string = values[record.nameID].encode("utf_16_be")

    font["head"].fontRevision = REVISION
    font["OS/2"].sxHeight = design.X_HEIGHT_TARGET
    font["OS/2"].usWeightClass = weight
    font["OS/2"].achVendID = "SDOB"
    font["OS/2"].xAvgCharWidth = font["OS/2"].recalcAvgCharWidth(font)
    # Cover every transformed descender on Windows. The family hhea/typo
    # descent is already -295, so using 295 does not change normal line height.
    font["OS/2"].usWinDescent = max(font["OS/2"].usWinDescent, 295)

    if "CFF " in font:
        cff = font["CFF "].cff
        cff.fontNames[0] = postscript
        top = cff.topDictIndex[0]
        top.FamilyName = "Zutat Sans"
        top.FullName = f"Zutat Sans {style}"


def metrics(font: TTFont, glyph_name: str, tracking: int, round_inset: int, m_rsb: int):
    advance, old_lsb = font["hmtx"][glyph_name]
    scale = design.horizontal_scale(glyph_name)
    # Combining marks and other zero-advance glyphs must remain zero-width.
    # Applying the family's tracking to them makes GPOS marks consume layout
    # space even though they are classified as marks in GDEF.
    new_advance = 0 if advance == 0 else max(0, round(advance * scale + tracking))
    char = design.base_character(glyph_name)
    decomposed = design.unicodedata.normalize("NFD", char)[0] if char else ""
    if decomposed in {"O", "o"}:
        new_advance -= 2 * round_inset
    shift = (new_advance - advance * scale) / 2
    new_lsb = round(old_lsb * scale + shift)
    if decomposed == "m":
        new_advance += m_rsb
    return new_advance, new_lsb, scale, shift


def transform_ttf(font: TTFont, tracking: int, round_inset: int, m_rsb: int) -> None:
    glyph_set = font.getGlyphSet()
    glyphs, new_metrics = {}, {}
    for name in font.getGlyphOrder():
        advance, lsb, scale, shift = metrics(font, name, tracking, round_inset, m_rsb)
        recording = DecomposingRecordingPen(glyph_set)
        glyph_set[name].draw(recording)
        output = TTGlyphPen(None)
        recording.replay(design.WarpPen(output, name, scale, shift))
        glyphs[name] = output.glyph()
        new_metrics[name] = (advance, lsb)
    for name, glyph in glyphs.items():
        font["glyf"][name] = glyph
    font["hmtx"].metrics.update(new_metrics)
    for table in ("cvt ", "fpgm", "prep", "LTSH", "hdmx", "VDMX"):
        if table in font:
            del font[table]


def transform_otf(font: TTFont, tracking: int, round_inset: int, m_rsb: int) -> None:
    glyph_set = font.getGlyphSet()
    top = font["CFF "].cff.topDictIndex[0]
    replacements, new_metrics = {}, {}
    for name in font.getGlyphOrder():
        advance, lsb, scale, shift = metrics(font, name, tracking, round_inset, m_rsb)
        recording = DecomposingRecordingPen(glyph_set)
        glyph_set[name].draw(recording)
        output = T2CharStringPen(advance, None)
        recording.replay(design.WarpPen(output, name, scale, shift))
        replacements[name] = output.getCharString(
            private=top.Private, globalSubrs=top.GlobalSubrs
        )
        new_metrics[name] = (advance, lsb)
    for name, char_string in replacements.items():
        top.CharStrings[name] = char_string
    font["hmtx"].metrics.update(new_metrics)


def transformation_map(font: TTFont, config: dict) -> dict[str, tuple[float, float]]:
    result = {}
    for glyph_name in font.getGlyphOrder():
        _, _, scale, shift = metrics(
            font,
            glyph_name,
            config["tracking"],
            config["round_inset"],
            config["m_rsb"],
        )
        result[glyph_name] = (scale, shift)
    return result


def transform_anchor(anchor, glyph_name: str, transforms: dict) -> bool:
    if anchor is None:
        return False
    scale, shift = transforms[glyph_name]
    old_x, old_y = anchor.XCoordinate, anchor.YCoordinate
    anchor.XCoordinate = round(old_x * scale + shift)
    anchor.YCoordinate = round(design.map_y(old_y, design.is_lowercase_glyph(glyph_name)))
    return (anchor.XCoordinate, anchor.YCoordinate) != (old_x, old_y)


def class_scale_groups(class_def, glyphs: list[str], transforms: dict) -> dict[int, float]:
    groups = defaultdict(list)
    for glyph_name in glyphs:
        class_id = class_def.classDefs.get(glyph_name, 0)
        groups[class_id].append(transforms[glyph_name][0])
    global_average = sum(scale for scale, _ in transforms.values()) / len(transforms)
    return {
        class_id: sum(scales) / len(scales) if scales else global_average
        for class_id, scales in groups.items()
    } | {0: sum(groups[0]) / len(groups[0]) if groups[0] else global_average}


def adjust_pair_positioning(subtable, transforms: dict) -> int:
    changed = 0
    if subtable.Format == 1:
        for first_glyph, pair_set in zip(subtable.Coverage.glyphs, subtable.PairSet):
            first_scale = transforms[first_glyph][0]
            for record in pair_set.PairValueRecord:
                second_scale = transforms[record.SecondGlyph][0]
                value = record.Value1
                if value is not None and getattr(value, "XAdvance", 0):
                    value.XAdvance = round(value.XAdvance * (first_scale + second_scale) / 2)
                    changed += 1
    elif subtable.Format == 2:
        first_scales = class_scale_groups(
            subtable.ClassDef1, list(subtable.Coverage.glyphs), transforms
        )
        second_scales = class_scale_groups(
            subtable.ClassDef2, list(transforms), transforms
        )
        global_average = sum(scale for scale, _ in transforms.values()) / len(transforms)
        for class1, row in enumerate(subtable.Class1Record):
            for class2, record in enumerate(row.Class2Record):
                value = record.Value1
                if value is None or not getattr(value, "XAdvance", 0):
                    continue
                scale1 = first_scales.get(class1, global_average)
                scale2 = second_scales.get(class2, global_average)
                value.XAdvance = round(value.XAdvance * (scale1 + scale2) / 2)
                changed += 1
    return changed


def adjust_mark_to_base(subtable, transforms: dict) -> int:
    changed = 0
    for glyph, record in zip(subtable.MarkCoverage.glyphs, subtable.MarkArray.MarkRecord):
        changed += transform_anchor(record.MarkAnchor, glyph, transforms)
    for glyph, record in zip(subtable.BaseCoverage.glyphs, subtable.BaseArray.BaseRecord):
        for anchor in record.BaseAnchor:
            changed += transform_anchor(anchor, glyph, transforms)
    return changed


def adjust_mark_to_ligature(subtable, transforms: dict) -> int:
    changed = 0
    for glyph, record in zip(subtable.MarkCoverage.glyphs, subtable.MarkArray.MarkRecord):
        changed += transform_anchor(record.MarkAnchor, glyph, transforms)
    for glyph, attach in zip(
        subtable.LigatureCoverage.glyphs, subtable.LigatureArray.LigatureAttach
    ):
        for component in attach.ComponentRecord:
            for anchor in component.LigatureAnchor:
                changed += transform_anchor(anchor, glyph, transforms)
    return changed


def adjust_mark_to_mark(subtable, transforms: dict) -> int:
    changed = 0
    for glyph, record in zip(subtable.Mark1Coverage.glyphs, subtable.Mark1Array.MarkRecord):
        changed += transform_anchor(record.MarkAnchor, glyph, transforms)
    for glyph, record in zip(subtable.Mark2Coverage.glyphs, subtable.Mark2Array.Mark2Record):
        for anchor in record.Mark2Anchor:
            changed += transform_anchor(anchor, glyph, transforms)
    return changed


def adjust_gpos(font: TTFont, transforms: dict) -> tuple[int, int]:
    kern_values = 0
    anchors = 0
    for lookup in font["GPOS"].table.LookupList.Lookup:
        for subtable in lookup.SubTable:
            if lookup.LookupType == 2:
                kern_values += adjust_pair_positioning(subtable, transforms)
            elif lookup.LookupType == 4:
                anchors += adjust_mark_to_base(subtable, transforms)
            elif lookup.LookupType == 5:
                anchors += adjust_mark_to_ligature(subtable, transforms)
            elif lookup.LookupType == 6:
                anchors += adjust_mark_to_mark(subtable, transforms)
    return kern_values, anchors


def repair_default_one_features(font: TTFont) -> int:
    """Keep numeric features working after one.ss09 becomes the cmap default."""
    repaired = 0
    gsub = font["GSUB"].table
    feature_records = {record.FeatureTag: record.Feature for record in gsub.FeatureList.FeatureRecord}
    for tag in ("dnom", "frac", "numr", "sinf", "subs", "sups", "tnum"):
        feature = feature_records.get(tag)
        if feature is None:
            continue
        for lookup_index in feature.LookupListIndex:
            lookup = gsub.LookupList.Lookup[lookup_index]
            if lookup.LookupType != 1:
                continue
            for subtable in lookup.SubTable:
                mapping = getattr(subtable, "mapping", None)
                if mapping is not None and "one" in mapping and "one.ss09" not in mapping:
                    mapping["one.ss09"] = mapping["one"]
                    repaired += 1

    # Returning from tabular to proportional figures should restore the
    # approved default one, not Geist's unselected one.
    pnum = feature_records.get("pnum")
    if pnum is not None:
        for lookup_index in pnum.LookupListIndex:
            lookup = gsub.LookupList.Lookup[lookup_index]
            if lookup.LookupType != 1:
                continue
            for subtable in lookup.SubTable:
                mapping = getattr(subtable, "mapping", None)
                if mapping is not None and mapping.get("one.tf") == "one":
                    mapping["one.tf"] = "one.ss09"
                    repaired += 1
    return repaired


def adjust_gdef_ligature_carets(font: TTFont, transforms: dict) -> int:
    gdef = font.get("GDEF")
    if gdef is None or gdef.table.LigCaretList is None:
        return 0
    changed = 0
    caret_list = gdef.table.LigCaretList
    for glyph_name, lig_glyph in zip(caret_list.Coverage.glyphs, caret_list.LigGlyph):
        scale, shift = transforms[glyph_name]
        for caret in lig_glyph.CaretValue:
            if caret.Format not in (1, 3):
                continue
            old = caret.Coordinate
            caret.Coordinate = round(old * scale + shift)
            changed += caret.Coordinate != old
    return changed


def autohint(ttf_path: Path) -> None:
    hinted_path = ttf_path.with_suffix(".hinted.ttf")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "ttfautohint",
            "--no-info",
            "--increase-x-height=0",
            str(ttf_path),
            str(hinted_path),
        ],
        check=True,
    )
    os.replace(hinted_path, ttf_path)


def build_style(style: str, config: dict) -> None:
    source = config["source"]
    weight = config["weight"]

    ttf = TTFont(REFERENCE / "ttf" / f"Geist-{source}.ttf")
    ttf_transforms = transformation_map(ttf, config)
    transform_ttf(
        ttf, config["tracking"], config["round_inset"], config["m_rsb"]
    )
    kern_count, anchor_count = adjust_gpos(ttf, ttf_transforms)
    caret_count = adjust_gdef_ligature_carets(ttf, ttf_transforms)
    design.bake_character_system(ttf)
    numeric_repairs = repair_default_one_features(ttf)
    set_names(ttf, style, weight)
    ttf_path = OUT / f"ZutatSans-{style}.ttf"
    ttf.save(ttf_path)
    autohint(ttf_path)

    web = TTFont(ttf_path)
    web.flavor = "woff2"
    web.save(OUT / f"ZutatSans-{style}.woff2")

    otf = TTFont(REFERENCE / "otf" / f"Geist-{source}.otf")
    otf_transforms = transformation_map(otf, config)
    transform_otf(
        otf, config["tracking"], config["round_inset"], config["m_rsb"]
    )
    adjust_gpos(otf, otf_transforms)
    adjust_gdef_ligature_carets(otf, otf_transforms)
    design.bake_character_system(otf)
    repair_default_one_features(otf)
    set_names(otf, style, weight)
    otf.save(OUT / f"ZutatSans-{style}.otf")
    print(
        f"{style}: adjusted {kern_count} kerning values, {anchor_count} anchors, "
        f"{caret_count} ligature carets, and {numeric_repairs} numeric substitutions"
    )


def write_checksums() -> None:
    files = sorted(path for path in OUT.iterdir() if path.name != "SHA256SUMS.txt")
    rows = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}" for path in files]
    (OUT / "SHA256SUMS.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for style, config in STYLES.items():
        build_style(style, config)

    shutil.copy2(ROOT / "references" / "geist-font" / "LICENSE.txt", OUT / "OFL-1.1.txt")
    css = "\n\n".join(
        f'''@font-face {{
  font-family: "Zutat Sans";
  src: url("ZutatSans-{style}.woff2") format("woff2");
  font-style: normal;
  font-weight: {config["weight"]};
  font-display: swap;
}}'''
        for style, config in STYLES.items()
    ) + "\n"
    (OUT / "zutat-font.css").write_text(css, encoding="utf-8")
    (OUT / "README.md").write_text(
        """# Zutat Sans 0.6

Zutat Sans 0.6 is the production-hardened release of the upright static family.
It includes recalibrated kerning and mark positioning, Windows-safe vertical
metrics, TrueType screen hinting, validated OpenType numeral features, and four
static weights in TTF, OTF, and WOFF2 formats.

Zutat Sans is a modified Geist-derived font distributed under the SIL Open
Font License 1.1. See `OFL-1.1.txt` for the complete license and copyright
notice.
""",
        encoding="utf-8",
    )
    write_checksums()
    print(OUT)


if __name__ == "__main__":
    main()
