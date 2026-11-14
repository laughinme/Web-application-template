"use client";

import { useState, type FormEvent } from "react";
import type { ProfilePatch, User } from "@/entities/user";
import { Button } from "@/shared/ui/button";
import { Field, FieldGroup, FieldLabel } from "@/shared/ui/field";
import { Input } from "@/shared/ui/input";
import { useUpdateProfile } from "../model/use-update-profile";

/** Sends only the fields that changed; an emptied field is sent as `null` and cleared. */
export function ProfileEditForm({ profile }: { profile: User }) {
  const [username, setUsername] = useState(profile.username ?? "");
  const [bio, setBio] = useState(profile.bio ?? "");
  const save = useUpdateProfile();

  const patch: ProfilePatch = {};
  if (username !== (profile.username ?? "")) patch.username = username.trim() || null;
  if (bio !== (profile.bio ?? "")) patch.bio = bio.trim() || null;
  const changed = Object.keys(patch).length > 0;

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (changed) save.mutate(patch);
  };

  const reset = () => {
    setUsername(profile.username ?? "");
    setBio(profile.bio ?? "");
  };

  return (
    <form onSubmit={submit}>
      <FieldGroup>
        <Field>
          <FieldLabel htmlFor="profile-username">Имя пользователя</FieldLabel>
          <Input
            id="profile-username"
            maxLength={64}
            placeholder="Как вас называть"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="profile-bio">О себе</FieldLabel>
          <textarea
            id="profile-bio"
            rows={4}
            maxLength={500}
            placeholder="Пара слов о себе"
            className="border-input placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 dark:bg-input/30 w-full min-w-0 resize-none rounded-md border bg-transparent px-3 py-2 text-base shadow-xs outline-none focus-visible:ring-[3px] md:text-sm"
            value={bio}
            onChange={(event) => setBio(event.target.value)}
          />
        </Field>
        <div className="flex justify-end gap-3">
          <Button type="button" variant="ghost" disabled={!changed || save.isPending} onClick={reset}>
            Отмена
          </Button>
          <Button type="submit" disabled={!changed || save.isPending}>
            {save.isPending ? "Сохранение…" : "Сохранить"}
          </Button>
        </div>
      </FieldGroup>
    </form>
  );
}
