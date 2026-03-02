import type { Metadata } from "next";
import type { ReactNode } from "react";
import "../src/index.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "Monolith Frontend",
  description: "Frontend приложение на Next.js"
};

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="ru">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
