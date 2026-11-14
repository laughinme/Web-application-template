"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { useSession } from "@/entities/session";
import { isAdmin, useMe } from "@/entities/user";
import { routes } from "@/shared/config";
import { safeReturnPath } from "@/shared/lib/navigation";
import { Button } from "@/shared/ui/button";

export function SessionLoading() {
  return (
    <div className="flex min-h-svh items-center justify-center" role="status">
      <p className="text-muted-foreground">Загрузка…</p>
    </div>
  );
}

/** Signed-in area. Anonymous visitors go to /auth and come back to the same URL afterwards. */
export function RequireSession({ children }: { children: ReactNode }) {
  const session = useSession();
  const me = useMe({ enabled: session.status === "authenticated" });
  const router = useRouter();
  const pathname = usePathname();
  const search = useSearchParams().toString();
  const anonymous = session.status === "anonymous";

  useEffect(() => {
    if (!anonymous) return;
    const next = `${pathname}${search ? `?${search}` : ""}`;
    router.replace(`${routes.auth}?next=${encodeURIComponent(next)}`);
  }, [anonymous, pathname, search, router]);

  if (me.isError) {
    return (
      <div className="flex min-h-svh flex-col items-center justify-center gap-3" role="alert">
        <p className="text-muted-foreground">Не удалось загрузить данные</p>
        <Button variant="outline" onClick={() => void me.refetch()}>
          Повторить
        </Button>
      </div>
    );
  }
  if (!me.data) return <SessionLoading />;
  return children;
}

/** Sign-in page: a signed-in user is sent on to `?next=` (local paths only) or home. */
export function RequireGuest({ children }: { children: ReactNode }) {
  const session = useSession();
  const router = useRouter();
  const next = useSearchParams().get("next");
  const signedIn = session.status === "authenticated";

  useEffect(() => {
    if (signedIn) router.replace(safeReturnPath(next, routes.auth));
  }, [signedIn, next, router]);

  if (session.status !== "anonymous") return <SessionLoading />;
  return children;
}

/** Hides admin screens from members. The API enforces the same permissions on every call. */
export function RequireAdmin({ children }: { children: ReactNode }) {
  const { data: user } = useMe();
  if (!isAdmin(user)) {
    return <p className="py-20 text-center text-muted-foreground">Этот раздел доступен только администраторам</p>;
  }
  return children;
}
