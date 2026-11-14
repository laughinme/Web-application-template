"use client";

import { LogOut, UserRound } from "lucide-react";
import Link from "next/link";
import { displayName, UserAvatar, type User } from "@/entities/user";
import { useLogout } from "@/features/logout";
import { routes } from "@/shared/config";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/shared/ui/dropdown-menu";

export function UserMenu({ user }: { user: User }) {
  const logout = useLogout();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        aria-label="Меню пользователя"
        className="rounded-full focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:outline-none"
      >
        <UserAvatar user={user} className="size-8" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" sideOffset={8} className="w-56">
        <DropdownMenuLabel className="font-normal">
          <p className="truncate text-sm font-medium">{displayName(user)}</p>
          <p className="truncate text-xs text-muted-foreground">{user.email}</p>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href={routes.profile}>
            <UserRound aria-hidden />
            Профиль
          </Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem variant="destructive" onSelect={() => logout.mutate()}>
          <LogOut aria-hidden />
          Выйти
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
