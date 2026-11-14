import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Providers } from "@/_app";
import "@/_app/styles/index.css";

// Routing only: every file in app/ re-exports a page or layout from src/ (FSD layers).
export const metadata: Metadata = {
  title: "Monolith",
  description: "Fullstack monolith template",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
