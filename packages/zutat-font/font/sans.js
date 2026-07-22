import localFont from "next/font/local";

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
