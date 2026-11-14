import { api, type Schemas } from "@/shared/api";
import type { ProfilePatch, Role, User, UsersPage, UsersQuery } from "../model/types";
import { toProfileUpdate, toUser, toUsersPage } from "./mappers";

type UserDto = Schemas["UserOut"];
type AvatarType = Schemas["AvatarPresignRequest"]["content_type"];

export const AVATAR_TYPES: readonly AvatarType[] = ["image/jpeg", "image/png", "image/webp"];

export async function fetchMe(): Promise<User> {
  return toUser((await api.get<UserDto>("/users/me")).data);
}

export async function updateMe(patch: ProfilePatch): Promise<User> {
  return toUser((await api.patch<UserDto>("/users/me", toProfileUpdate(patch))).data);
}

/** Presign → PUT straight to storage → confirm. The file never goes through the API. */
export async function uploadAvatar(file: File): Promise<User> {
  if (!AVATAR_TYPES.includes(file.type as AvatarType)) {
    throw new Error("Unsupported avatar type");
  }
  const { data: upload } = await api.post<Schemas["AvatarPresignResponse"]>(
    "/users/me/avatar/presign",
    { content_type: file.type as AvatarType, filename: file.name } satisfies Schemas["AvatarPresignRequest"],
  );
  const stored = await fetch(upload.upload_url, {
    method: "PUT",
    headers: { "Content-Type": file.type },
    body: file,
  });
  if (!stored.ok) throw new Error(`Avatar upload failed with status ${stored.status}`);
  const { data } = await api.post<UserDto>("/users/me/avatar/confirm", { object_key: upload.object_key });
  return toUser(data);
}

export async function removeAvatar(): Promise<User> {
  return toUser((await api.delete<UserDto>("/users/me/avatar")).data);
}

export async function listUsers(query: UsersQuery, cursor: string | null): Promise<UsersPage> {
  const params = { ...query, search: query.search || undefined, cursor: cursor ?? undefined, limit: 20 };
  return toUsersPage((await api.get<Schemas["CursorPage_UserOut_"]>("/admin/users", { params })).data);
}

export async function banUser(id: string): Promise<User> {
  return toUser((await api.post<UserDto>(`/admin/users/${id}/ban`)).data);
}

export async function unbanUser(id: string): Promise<User> {
  return toUser((await api.delete<UserDto>(`/admin/users/${id}/ban`)).data);
}

export async function setUserRole(id: string, role: Role): Promise<User> {
  return toUser((await api.put<UserDto>(`/admin/users/${id}/role`, { role })).data);
}
