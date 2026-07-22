import localFont from "next/font/local";

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
