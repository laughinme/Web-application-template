"use client";

import Link from "next/link";
import { displayName, isAdmin, useMe } from "@/entities/user";
import { routes } from "@/shared/config";
import { Card, CardDescription, CardHeader, CardTitle } from "@/shared/ui/card";

const LINKS = [
  { href: routes.profile, title: "Профиль", text: "Имя, описание и фото", admin: false },
  { href: routes.admin, title: "Статистика", text: "Регистрации и счётчики", admin: true },
  { href: routes.adminUsers, title: "Пользователи", text: "Поиск, роли и блокировки", admin: true },
] as const;

export function HomePage() {
  const { data: user } = useMe();
  const links = LINKS.filter((link) => !link.admin || isAdmin(user));

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold tracking-tight">
        {user ? `Привет, ${displayName(user)}` : "Привет"}
      </h1>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {links.map((link) => (
          <Link key={link.href} href={link.href} className="rounded-xl focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none">
            <Card className="h-full transition-colors hover:bg-muted/50">
              <CardHeader>
                <CardTitle>{link.title}</CardTitle>
                <CardDescription>{link.text}</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
