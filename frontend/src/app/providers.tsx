"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MotionConfig } from "motion/react";
import { ThemeProvider } from "next-themes";
import { useState, type ReactNode } from "react";
import { Toaster } from "@/shared/components/ui/sonner";
import { AuthProvider } from "./providers/auth/AuthContext";

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
        <MotionConfig reducedMotion="user">
          <AuthProvider>{children}</AuthProvider>
          <Toaster />
        </MotionConfig>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
