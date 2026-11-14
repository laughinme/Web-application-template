import type { Schemas } from "@/shared/api";
import type { ProfilePatch, User, UsersPage } from "../model/types";

export const toUser = (dto: Schemas["UserOut"]): User => ({
  id: dto.id,
  email: dto.email,
  username: dto.username ?? null,
  bio: dto.bio ?? null,
  avatarUrl: dto.avatar_url ?? null,
  role: dto.role,
  isOnboarded: dto.is_onboarded,
  banned: dto.banned,
  createdAt: dto.created_at,
  updatedAt: dto.updated_at,
});

export const toUsersPage = (dto: Schemas["CursorPage_UserOut_"]): UsersPage => ({
  items: dto.items.map(toUser),
  nextCursor: dto.next_cursor ?? null,
});

// PATCH semantics: a missing key keeps the value, `null` clears it.
export const toProfileUpdate = (patch: ProfilePatch): Schemas["ProfileUpdate"] => {
  const dto: Schemas["ProfileUpdate"] = {};
  if (patch.username !== undefined) dto.username = patch.username;
  if (patch.bio !== undefined) dto.bio = patch.bio;
  return dto;
};
