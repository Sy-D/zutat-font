#!/usr/bin/env python3
"""Create the reusable Zutat Sans 0.6 Next.js/npm package."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "build" / "zutat-font-v0.6"
RELEASE_FONTS = ROOT / "fonts"
OUT = ROOT / "packages" / "zutat-font"
STYLES = ("Regular", "Medium", "SemiBold", "Bold")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "font").mkdir(parents=True)
    (OUT / "files").mkdir()
    (OUT / "files" / "subsets").mkdir()

    # A standalone release repository already contains reviewed, checksummed
    # binaries under fonts/. Reuse those exact files instead of producing
    # byte-different WOFF2 output during npm packaging. The development
    # workspace falls back to the current build directory.
    full_source = RELEASE_FONTS / "woff2" if RELEASE_FONTS.exists() else SOURCE
    subset_source = (
        RELEASE_FONTS / "web" / "latin"
        if RELEASE_FONTS.exists()
        else SOURCE / "subsets"
    )

    for style in STYLES:
        shutil.copy2(full_source / f"ZutatSans-{style}.woff2", OUT / "files")
        shutil.copy2(
            subset_source / f"ZutatSans-{style}-latin.woff2",
            OUT / "files" / "subsets",
        )
    shutil.copy2(SOURCE / "OFL-1.1.txt", OUT / "LICENSE.txt")

    package = {
        "name": "zutat-font",
        "version": "0.6.1",
        "description": "Zutat Sans — quiet authority and editorial precision for digital products and brands.",
        "type": "module",
        "types": "./font/sans.d.ts",
        "style": "./style.css",
        "exports": {
            ".": {
                "types": "./font/sans.d.ts",
                "default": "./font/sans.js",
            },
            "./font/sans": {
                "types": "./font/sans.d.ts",
                "default": "./font/sans.js",
            },
            "./font/sans-latin": {
                "types": "./font/sans-latin.d.ts",
                "default": "./font/sans-latin.js",
            },
            "./style.css": "./style.css",
            "./style-latin.css": "./style-latin.css",
            "./files/*": "./files/*",
        },
        "files": ["font", "files", "style.css", "style-latin.css", "README.md", "LICENSE.txt", "NOTICE.md"],
        "sideEffects": ["./style.css", "./style-latin.css"],
        "author": "Simon Doba",
        "contributors": [
            "Vercel",
            "basement.studio",
            "Geist contributors",
        ],
        "license": "OFL-1.1",
        "homepage": "https://github.com/Sy-D/zutat-font#readme",
        "bugs": {"url": "https://github.com/Sy-D/zutat-font/issues"},
        "repository": {
            "type": "git",
            "url": "git+https://github.com/Sy-D/zutat-font.git",
            "directory": "packages/zutat-font",
        },
        "engines": {"node": ">=18.18.0"},
        "publishConfig": {"access": "public", "provenance": True},
        "keywords": [
            "font",
            "sans-serif",
            "typeface",
            "webfont",
            "woff2",
            "next.js",
            "next-font",
            "typography",
            "zutat-font",
        ],
    }
    (OUT / "package.json").write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")

    (OUT / "font" / "sans.js").write_text('''import localFont from "next/font/local";

export const ZutatSans = localFont({
  src: [
    { path: "../files/ZutatSans-Regular.woff2", weight: "400", style: "normal" },
    { path: "../files/ZutatSans-Medium.woff2", weight: "500", style: "normal" },
    { path: "../files/ZutatSans-SemiBold.woff2", weight: "600", style: "normal" },
    { path: "../files/ZutatSans-Bold.woff2", weight: "700", style: "normal" },
  ],
  variable: "--font-zutat",
  display: "swap",
  preload: true,
  fallback: [
    "ui-sans-serif",
    "system-ui",
    "-apple-system",
    "BlinkMacSystemFont",
    "Segoe UI",
    "Arial",
    "sans-serif",
  ],
});

export default ZutatSans;
''', encoding="utf-8")

    (OUT / "font" / "sans-latin.js").write_text('''import localFont from "next/font/local";

export const ZutatSansLatin = localFont({
  src: [
    { path: "../files/subsets/ZutatSans-Regular-latin.woff2", weight: "400", style: "normal" },
    { path: "../files/subsets/ZutatSans-Medium-latin.woff2", weight: "500", style: "normal" },
    { path: "../files/subsets/ZutatSans-SemiBold-latin.woff2", weight: "600", style: "normal" },
    { path: "../files/subsets/ZutatSans-Bold-latin.woff2", weight: "700", style: "normal" },
  ],
  variable: "--font-zutat",
  display: "swap",
  preload: true,
  fallback: [
    "ui-sans-serif",
    "system-ui",
    "-apple-system",
    "BlinkMacSystemFont",
    "Segoe UI",
    "Arial",
    "sans-serif",
  ],
});

export default ZutatSansLatin;
''', encoding="utf-8")

    (OUT / "font" / "sans.d.ts").write_text('''export interface ZutatFontWithVariable {
  className: string;
  style: { fontFamily: string; fontWeight?: number; fontStyle?: string };
  variable: string;
}

export declare const ZutatSans: ZutatFontWithVariable;
export default ZutatSans;
''', encoding="utf-8")

    (OUT / "font" / "sans-latin.d.ts").write_text('''export interface ZutatFontWithVariable {
  className: string;
  style: { fontFamily: string; fontWeight?: number; fontStyle?: string };
  variable: string;
}

export declare const ZutatSansLatin: ZutatFontWithVariable;
export default ZutatSansLatin;
''', encoding="utf-8")

    css = '''@font-face {
  font-family: "Zutat Sans";
  src: url("./files/ZutatSans-Regular.woff2") format("woff2");
  font-style: normal;
  font-weight: 400;
  font-display: swap;
}

@font-face {
  font-family: "Zutat Sans";
  src: url("./files/ZutatSans-Medium.woff2") format("woff2");
  font-style: normal;
  font-weight: 500;
  font-display: swap;
}

@font-face {
  font-family: "Zutat Sans";
  src: url("./files/ZutatSans-SemiBold.woff2") format("woff2");
  font-style: normal;
  font-weight: 600;
  font-display: swap;
}

@font-face {
  font-family: "Zutat Sans";
  src: url("./files/ZutatSans-Bold.woff2") format("woff2");
  font-style: normal;
  font-weight: 700;
  font-display: swap;
}

:root {
  --font-zutat: "Zutat Sans", ui-sans-serif, system-ui, -apple-system,
    BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
}
'''
    (OUT / "style.css").write_text(css, encoding="utf-8")

    latin_css = css.replace("./files/ZutatSans-", "./files/subsets/ZutatSans-")
    for style in STYLES:
        latin_css = latin_css.replace(
            f"ZutatSans-{style}.woff2", f"ZutatSans-{style}-latin.woff2"
        )
    latin_unicode_range = (
        "U+0000-024F, U+02B0-036F, U+039B, U+03BB, U+1D00-1DBF, "
        "U+1E00-1EFF, U+2000-22FF, U+2500-25FF, U+3003, "
        "U+FB00-FB06, U+FEFF, U+FFFD"
    )
    latin_css = latin_css.replace(
        "  font-display: swap;\n}",
        f"  font-display: swap;\n  unicode-range: {latin_unicode_range};\n}}",
    )
    (OUT / "style-latin.css").write_text(latin_css, encoding="utf-8")

    readme = '''# Zutat Sans

Zutat Sans is a contemporary sans-serif shaped by quiet authority, editorial precision, and restrained character.

## Install

```sh
npm install zutat-font
```

## Next.js

```tsx
import { ZutatSans } from "zutat-font/font/sans";

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={ZutatSans.variable}>
      <body>{children}</body>
    </html>
  );
}
```

```css
body {
  font-family: var(--font-zutat);
}
```

For a smaller Latin-only payload, use `zutat-font/font/sans-latin` and
`ZutatSansLatin`. The complete family remains available through `font/sans`.

For Next.js versions below 15, add `transpilePackages: ["zutat-font"]` to `next.config.js` if your build reports an ESM loader error.

`next` is intentionally not installed by this package. The JavaScript font
exports are for applications that already use Next.js; CSS-only consumers can
use the stylesheet exports without pulling in the Next.js dependency tree.

## Plain CSS

```js
import "zutat-font/style.css";
```

Use `zutat-font/style-latin.css` for the Latin web subset.

Or link the stylesheet directly and use `font-family: "Zutat Sans", sans-serif`.

## Included weights

- Regular 400
- Medium 500
- SemiBold 600
- Bold 700

## License

Zutat Sans is derived from Geist and distributed under the SIL Open Font License 1.1. See `LICENSE.txt` and `NOTICE.md`.
'''
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    (OUT / "NOTICE.md").write_text('''# Attribution

Zutat Sans is a modified typeface derived from Geist by Vercel, basement.studio, and contributors. Zutat Sans is distributed under the SIL Open Font License 1.1.
''', encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
