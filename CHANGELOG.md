# Changelog

## 0.6.1 — 2026-07-22

- Removed the open-ended Next.js peer dependency so installing the CSS/font
  package no longer resolves the complete Next.js, Sharp, SWC, and PostCSS
  dependency tree.
- Replaced the declaration-file import from Next.js internals with a local
  structural font type.
- Kept the existing `zutat-font/font/sans` integration for applications that
  already use Next.js.

## 0.6.0 — 2026-07-22

- Renamed the family to Zutat Sans.
- Recalibrated kerning for the custom horizontal proportions.
- Transformed mark, ligature, and mark-to-mark anchors with the outlines.
- Corrected Windows vertical metrics and retained TrueType autohinting.
- Repaired numeral substitutions and tabular figures.
- Added broad Latin web subsets and Next.js/npm exports.
- Added cross-browser 10–18 px Playwright regression tests.
- Added deterministic outline-based SVG specimen posters.
