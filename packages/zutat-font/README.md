# Zutat Sans

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
