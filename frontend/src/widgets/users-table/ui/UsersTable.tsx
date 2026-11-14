"use client";

import { useDeferredValue, useState } from "react";
import { displayName, RoleBadge, UserAvatar, useUsers, type User, type UsersQuery } from "@/entities/user";
import { ModerationActions } from "@/features/moderate-user";
import { formatDate } from "@/shared/lib/format";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/ui/select";
import { Skeleton } from "@/shared/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";

type Status = "all" | "active" | "banned";

function StatusBadge({ banned }: { banned: boolean }) {
  return banned ? <Badge variant="destructive">Заблокирован</Badge> : <Badge variant="outline">Активен</Badge>;
}

function Identity({ user }: { user: User }) {
  return (
    <div className="flex min-w-0 items-center gap-3">
      <UserAvatar user={user} className="size-8" />
      <div className="min-w-0">
        <p className="truncate font-medium">{displayName(user)}</p>
        <p className="truncate text-xs text-muted-foreground">{user.email}</p>
      </div>
    </div>
  );
}

const STATUS_FILTER: Record<Status, boolean | undefined> = { all: undefined, active: false, banned: true };

/** Search, filter and cursor paging over /admin/users, with moderation actions per row. */
export function UsersTable() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<Status>("all");
  const query: UsersQuery = { search: useDeferredValue(search.trim()), banned: STATUS_FILTER[status] };
  const users = useUsers(query);
  const rows = users.data?.pages.flatMap((page) => page.items) ?? [];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2 sm:flex-row">
        <Input
          type="search"
          aria-label="Поиск по email или имени"
          placeholder="Email или имя"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          className="sm:max-w-xs"
        />
        <Select value={status} onValueChange={(value) => setStatus(value as Status)}>
          <SelectTrigger className="w-full sm:w-44" aria-label="Статус">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Все</SelectItem>
            <SelectItem value="active">Активные</SelectItem>
            <SelectItem value="banned">Заблокированные</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Phones get cards: a five-column table cannot fit 390 px without hiding the actions. */}
      <ul className="flex flex-col gap-3 md:hidden">
        {rows.map((user) => (
          <li key={user.id} data-user={user.email} className="flex flex-col gap-3 rounded-lg border p-3">
            <Identity user={user} />
            <div className="flex flex-wrap gap-2">
              <RoleBadge role={user.role} />
              <StatusBadge banned={user.banned} />
            </div>
            <ModerationActions user={user} />
          </li>
        ))}
        {users.isPending ? <Skeleton className="h-28 w-full" /> : null}
        {!users.isPending && rows.length === 0 ? (
          <li className="py-10 text-center text-muted-foreground">
            {users.isError ? "Не удалось загрузить пользователей" : "Никого не нашли"}
          </li>
        ) : null}
      </ul>

      <div className="hidden rounded-lg border md:block">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Пользователь</TableHead>
              <TableHead>Роль</TableHead>
              <TableHead>Статус</TableHead>
              <TableHead className="hidden md:table-cell">Регистрация</TableHead>
              <TableHead className="text-right">Действия</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.isPending
              ? Array.from({ length: 4 }, (_, index) => (
                  <TableRow key={index}>
                    <TableCell colSpan={5}>
                      <Skeleton className="h-8 w-full" />
                    </TableCell>
                  </TableRow>
                ))
              : rows.map((user) => (
                  <TableRow key={user.id} data-user={user.email}>
                    <TableCell>
                      <Identity user={user} />
                    </TableCell>
                    <TableCell>
                      <RoleBadge role={user.role} />
                    </TableCell>
                    <TableCell>
                      <StatusBadge banned={user.banned} />
                    </TableCell>
                    <TableCell className="hidden md:table-cell">{formatDate(user.createdAt)}</TableCell>
                    <TableCell>
                      <ModerationActions user={user} />
                    </TableCell>
                  </TableRow>
                ))}
            {!users.isPending && rows.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="py-10 text-center text-muted-foreground">
                  {users.isError ? "Не удалось загрузить пользователей" : "Никого не нашли"}
                </TableCell>
              </TableRow>
            ) : null}
          </TableBody>
        </Table>
      </div>

      {users.hasNextPage ? (
        <Button
          variant="outline"
          className="self-center"
          disabled={users.isFetchingNextPage}
          onClick={() => void users.fetchNextPage()}
        >
          {users.isFetchingNextPage ? "Загрузка…" : "Показать ещё"}
        </Button>
      ) : null}
    </div>
  );
}
