import { cpSync, existsSync } from "node:fs";

// Next.js leaves these assets outside standalone output for CDN deployments.
cpSync(".next/static", ".next/standalone/.next/static", { recursive: true });
if (existsSync("public")) {
  cpSync("public", ".next/standalone/public", { recursive: true });
}
