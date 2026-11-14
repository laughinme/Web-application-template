import { Suspense, type ReactNode } from "react";
import { AppHeader } from "@/widgets/app-header";
import { RequireAdmin, RequireGuest, RequireSession, SessionLoading } from "./guards";

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <Suspense fallback={<SessionLoading />}>
      <RequireSession>
        <div className="flex min-h-svh flex-col">
          <AppHeader />
          <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6">{children}</main>
        </div>
      </RequireSession>
    </Suspense>
  );
}

export function GuestLayout({ children }: { children: ReactNode }) {
  return (
    <Suspense fallback={<SessionLoading />}>
      <RequireGuest>{children}</RequireGuest>
    </Suspense>
  );
}

export function AdminLayout({ children }: { children: ReactNode }) {
  return <RequireAdmin>{children}</RequireAdmin>;
}
