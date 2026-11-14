"use client";

import { isAxiosError } from "axios";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MotionConfig } from "motion/react";
import { ThemeProvider } from "next-themes";
import { useState, type ReactNode } from "react";
import { SessionProvider } from "@/entities/session";
import { Toaster } from "@/shared/ui/sonner";

// A 4xx will not change on retry; only network errors and 5xx are retried, once.
const retry = (failures: number, error: unknown) =>
  failures < 1 && !(isAxiosError(error) && (error.response?.status ?? 500) < 500);

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () => new QueryClient({ defaultOptions: { queries: { retry, staleTime: 30_000 }, mutations: { retry: false } } }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
        <MotionConfig reducedMotion="user">
          <SessionProvider>{children}</SessionProvider>
          <Toaster />
        </MotionConfig>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
