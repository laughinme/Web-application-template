import { Suspense, type ReactNode } from "react";
import { AuthGuard, SessionLoading } from "@/app/providers/auth/AuthGuard";

export default function ProtectedLayout({ children }: { children: ReactNode }) {
  return (
    <Suspense fallback={<SessionLoading />}>
      <AuthGuard>{children}</AuthGuard>
    </Suspense>
  );
}
