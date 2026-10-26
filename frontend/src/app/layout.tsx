import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Providers } from "./providers";
import "./styles/index.css";

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
