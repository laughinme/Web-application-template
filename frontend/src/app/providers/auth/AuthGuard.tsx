"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { useAuth } from "./useAuth";

function safeReturnPath(value: string | null): string {
  if (!value || !value.startsWith("/") || value.startsWith("//") || /[\\\s]/.test(value)) {
    return "/";
  }
  const url = new URL(value, "http://localhost");
  return url.pathname.replace(/\/+$/, "") === "/auth" ? "/" : value;
}

export function SessionLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50" role="status">
      <p className="text-lg text-slate-500">Загрузка сессии...</p>
    </div>
  );
}

export function AuthGuard({ children, guest = false }: { children: ReactNode; guest?: boolean }) {
  const auth = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const loading = !auth || auth.isRestoringSession || auth.isUserLoading;
  const hasUser = Boolean(auth?.user);
  const allowed = guest ? !hasUser : hasUser;
  const search = searchParams.toString();
  const returnPath = `${pathname}${search ? `?${search}` : ""}`;
  const destination = guest
    ? safeReturnPath(searchParams.get("next"))
    : `/auth?next=${encodeURIComponent(returnPath)}`;

  useEffect(() => {
    if (!loading && !allowed) router.replace(destination);
  }, [loading, allowed, destination, router]);

  if (loading || !allowed) return <SessionLoading />;
  return children;
}
