import fsd from "@feature-sliced/steiger-plugin";
import { defineConfig } from "steiger";

// FSD boundaries for src/: layers import only downward, slices only through their index.ts.
export default defineConfig([
  ...fsd.configs.recommended,
  {
    // Next.js reserves app/ and pages/, so the FSD layers are `_app` and `_pages` (official guide).
    files: ["./src/_app/**", "./src/_pages/**"],
    rules: { "fsd/typo-in-layer-name": "off" },
  },
  {
    // In the template every feature has exactly one screen; slices exist to show the pattern.
    // Turn this back on once the app has grown: a slice used once is usually part of its user.
    files: ["./src/**"],
    rules: { "fsd/insignificant-slice": "off" },
  },
]);
