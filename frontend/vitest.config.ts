import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

// Unit tests for pure code (mappers, error parsing, navigation). Screens are covered by Playwright.
export default defineConfig({
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
  test: { include: ["src/**/*.test.ts"], environment: "node" },
});
