"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { isAdmin, useMe } from "@/entities/user";
import { routes } from "@/shared/config";
import { cn } from "@/shared/lib/utils";
import { Skeleton } from "@/shared/ui/skeleton";
import { UserMenu } from "./UserMenu";

const NAV = [
  { href: routes.home, label: "Главная", admin: false },
  { href: routes.profile, label: "Профиль", admin: false },
  { href: routes.admin, label: "Статистика", admin: true },
  { href: routes.adminUsers, label: "Пользователи", admin: true },
] as const;

export function AppHeader() {
  const pathname = usePathname();
  const { data: user } = useMe();
  const links = NAV.filter((item) => !item.admin || isAdmin(user));

  return (
    <header className="sticky top-0 z-40 border-b bg-background/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-4 gap-y-1 px-4 py-2 sm:flex-nowrap sm:px-6">
        <Link href={routes.home} className="text-sm font-bold tracking-widest uppercase">
          Monolith
        </Link>
        <nav
          aria-label="Основная навигация"
          className="order-last -mx-2.5 flex w-full gap-1 overflow-x-auto sm:order-none sm:mx-0 sm:w-auto sm:flex-1"
        >
          {links.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              aria-current={pathname === item.href ? "page" : undefined}
              className={cn(
                "rounded-md px-2.5 py-1.5 text-sm whitespace-nowrap text-muted-foreground transition-colors hover:text-foreground",
                pathname === item.href && "bg-muted text-foreground",
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="ml-auto sm:ml-0">
          {user ? <UserMenu user={user} /> : <Skeleton className="size-8 rounded-full" />}
        </div>
      </div>
    </header>
  );
}
