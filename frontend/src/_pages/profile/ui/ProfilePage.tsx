"use client";

import { displayName, RoleBadge, useMe } from "@/entities/user";
import { ProfileEditForm } from "@/features/edit-profile";
import { AvatarUpload } from "@/features/upload-avatar";
import { formatDate } from "@/shared/lib/format";
import { Badge } from "@/shared/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/ui/card";
import { Skeleton } from "@/shared/ui/skeleton";

export function ProfilePage() {
  const { data: user, isPending, isError } = useMe();

  if (isPending) return <Skeleton className="h-80 w-full rounded-xl" />;
  if (isError || !user) {
    return <p className="text-muted-foreground">Не удалось загрузить профиль. Обновите страницу.</p>;
  }

  return (
    <div className="grid gap-6 md:grid-cols-[18rem_1fr]">
      <Card>
        <CardContent className="flex flex-col items-center gap-4 text-center">
          <AvatarUpload user={user} />
          <div className="w-full min-w-0">
            <h1 className="truncate text-xl font-semibold">{displayName(user)}</h1>
            {user.username ? <p className="truncate text-sm text-muted-foreground">{user.email}</p> : null}
          </div>
          <div className="flex flex-wrap justify-center gap-2">
            <RoleBadge role={user.role} />
            {user.banned ? <Badge variant="destructive">Заблокирован</Badge> : null}
          </div>
          <p className="text-xs text-muted-foreground">С нами с {formatDate(user.createdAt)}</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Личная информация</CardTitle>
          <CardDescription>Изменения видны всем, кто видит ваш профиль</CardDescription>
        </CardHeader>
        <CardContent>
          {/* key: a saved profile resets the form to the server values */}
          <ProfileEditForm key={`${user.username}:${user.bio}`} profile={user} />
        </CardContent>
      </Card>
    </div>
  );
}
