"use client";

import type { Role, User } from "@/entities/user";
import { Button } from "@/shared/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/ui/select";
import { useSetRole, useToggleBan } from "../model/use-moderation";

const ROLES: { value: Role; label: string }[] = [
  { value: "member", label: "Участник" },
  { value: "admin", label: "Администратор" },
];

/** Role select and ban button for one row. The backend re-checks every rule. */
export function ModerationActions({ user }: { user: User }) {
  const toggleBan = useToggleBan();
  const setRole = useSetRole();

  return (
    <div className="flex flex-wrap items-center justify-end gap-2">
      <Select
        value={user.role}
        disabled={setRole.isPending}
        onValueChange={(role) => setRole.mutate({ user, role: role as Role })}
      >
        <SelectTrigger size="sm" className="w-40" aria-label={`Роль ${user.email}`}>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {ROLES.map((role) => (
            <SelectItem key={role.value} value={role.value}>
              {role.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Button
        size="sm"
        variant="outline"
        className={user.banned ? undefined : "text-destructive hover:text-destructive"}
        disabled={toggleBan.isPending}
        onClick={() => toggleBan.mutate(user)}
      >
        {user.banned ? "Разблокировать" : "Заблокировать"}
      </Button>
    </div>
  );
}
