import { defineConfig } from "@playwright/test";

const baseURL = process.env.E2E_BASE_URL ?? "http://127.0.0.1:3100";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : undefined,
  use: { baseURL, trace: "retain-on-failure", reducedMotion: "reduce" },
  projects: [
    { name: "desktop", use: { viewport: { width: 1440, height: 900 } } },
    { name: "laptop", use: { viewport: { width: 1366, height: 768 } } },
    { name: "mobile", use: { viewport: { width: 390, height: 844 }, isMobile: true } },
  ],
  webServer: process.env.E2E_BASE_URL ? undefined : {
    command: "npm run build && npm start",
    url: baseURL,
    env: { PORT: "3100", HOSTNAME: "127.0.0.1", NEXT_PUBLIC_API_BASE_URL: "" },
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
