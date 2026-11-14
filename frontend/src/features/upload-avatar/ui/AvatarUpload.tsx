"use client";

import { Camera } from "lucide-react";
import { useRef, type ChangeEvent } from "react";
import { AVATAR_TYPES, UserAvatar, type User } from "@/entities/user";
import { Button } from "@/shared/ui/button";
import { useRemoveAvatar, useUploadAvatar } from "../model/use-avatar";

export function AvatarUpload({ user }: { user: User }) {
  const input = useRef<HTMLInputElement>(null);
  const upload = useUploadAvatar();
  const remove = useRemoveAvatar();
  const busy = upload.isPending || remove.isPending;

  const pick = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) upload.mutate(file);
    event.target.value = "";
  };

  return (
    <div className="flex flex-col items-center gap-3">
      <button
        type="button"
        aria-label="Загрузить фото"
        onClick={() => input.current?.click()}
        disabled={busy}
        className="group relative rounded-full focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:outline-none disabled:opacity-60"
      >
        <UserAvatar user={user} className="size-28 text-3xl" />
        <span className="absolute inset-0 flex items-center justify-center rounded-full bg-black/50 opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100">
          <Camera className="size-6 text-white" aria-hidden />
        </span>
      </button>
      {user.avatarUrl ? (
        <Button type="button" variant="ghost" size="sm" disabled={busy} onClick={() => remove.mutate()}>
          Удалить фото
        </Button>
      ) : null}
      <input ref={input} type="file" accept={AVATAR_TYPES.join(",")} className="hidden" onChange={pick} />
    </div>
  );
}
