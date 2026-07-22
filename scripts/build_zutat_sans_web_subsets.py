#!/usr/bin/env python3
"""Build production Latin WOFF2 subsets for Zutat Sans 0.6."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "build" / "zutat-font-v0.6"
OUT = SOURCE / "subsets"
STYLES = ("Regular", "Medium", "SemiBold", "Bold")

# Broad Latin support plus combining marks and UI punctuation/symbols. Lambda and
# the ditto mark are retained because they are part of Zutat Sans's documented set.
UNICODE_RANGES = (
    (0x0000, 0x00FF),
    (0x0100, 0x024F),
    (0x02B0, 0x02FF),
    (0x0300, 0x036F),
    (0x1D00, 0x1DBF),
    (0x1E00, 0x1EFF),
    (0x2000, 0x206F),
    (0x2070, 0x209F),
    (0x20A0, 0x20CF),
    (0x2100, 0x214F),
    (0x2190, 0x21FF),
    (0x2200, 0x22FF),
    (0x2500, 0x25FF),
    (0xFB00, 0xFB06),
)
EXTRA_CODEPOINTS = {0x039B, 0x03BB, 0x3003, 0xFEFF, 0xFFFD}


def selected_unicodes() -> set[int]:
    values = set(EXTRA_CODEPOINTS)
    for start, end in UNICODE_RANGES:
        values.update(range(start, end + 1))
    return values


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    requested = selected_unicodes()
    manifest: dict[str, object] = {
        "family": "Zutat Sans",
        "version": "0.6.0",
        "profile": "latin-web",
        "requestedUnicodeRanges": [
            f"U+{start:04X}-{end:04X}" for start, end in UNICODE_RANGES
        ] + [f"U+{value:04X}" for value in sorted(EXTRA_CODEPOINTS)],
        "files": [],
    }

    for style in STYLES:
        source_path = SOURCE / f"ZutatSans-{style}.ttf"
        output_path = OUT / f"ZutatSans-{style}-latin.woff2"
        font = TTFont(source_path)

        options = subset.Options()
        options.flavor = "woff2"
        options.layout_features = ["*"]
        options.name_IDs = ["*"]
        options.name_languages = ["*"]
        options.name_legacy = True
        options.recommended_glyphs = True
        options.notdef_glyph = True
        options.notdef_outline = True
        options.glyph_names = True
        options.hinting = True

        subsetter = subset.Subsetter(options=options)
        subsetter.populate(unicodes=requested)
        subsetter.subset(font)
        font.flavor = "woff2"
        font.save(output_path)

        check = TTFont(output_path)
        cmap = check.getBestCmap()
        required = "AZaz09ÄÖÜäöüßẞÆæ€•Λλ〃"
        missing = [char for char in required if ord(char) not in cmap]
        cyrillic = [cp for cp in cmap if 0x0400 <= cp <= 0x052F]
        if missing:
            raise RuntimeError(f"{output_path.name}: missing {missing}")
        if cyrillic:
            raise RuntimeError(f"{output_path.name}: unexpected Cyrillic codepoints")

        full_size = (SOURCE / f"ZutatSans-{style}.woff2").stat().st_size
        subset_size = output_path.stat().st_size
        manifest["files"].append({
            "file": output_path.name,
            "bytes": subset_size,
            "fullBytes": full_size,
            "reductionPercent": round((1 - subset_size / full_size) * 100, 1),
            "encodedCodepoints": len(cmap),
            "sha256": sha256(output_path),
        })
        print(
            f"{style}: {subset_size / 1024:.1f} KB "
            f"({(1 - subset_size / full_size) * 100:.1f}% smaller)"
        )

    manifest_path = OUT / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    checksum_path = SOURCE / "SHA256SUMS.txt"
    base_lines = [
        line for line in checksum_path.read_text(encoding="utf-8").splitlines()
        if "  subsets/" not in line
    ]
    subset_lines = [
        f"{sha256(path)}  {path.relative_to(SOURCE).as_posix()}"
        for path in sorted(OUT.iterdir())
        if path.is_file()
    ]
    checksum_path.write_text("\n".join(base_lines + subset_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
