import type { Schemas } from "@/shared/api";

export type Role = Schemas["Role"];

// The UI works with this shape; `api/mappers.ts` is the only place that knows the wire format.
export interface User {
  id: string;
  email: string;
  username: string | null;
  bio: string | null;
  avatarUrl: string | null;
  role: Role;
  isOnboarded: boolean;
  banned: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ProfilePatch {
  username?: string | null;
  bio?: string | null;
}

export interface UsersQuery {
  search?: string;
  role?: Role;
  banned?: boolean;
}

export interface UsersPage {
  items: User[];
  nextCursor: string | null;
}

export const displayName = (user: Pick<User, "username" | "email">): string =>
  user.username || user.email;

export const isAdmin = (user: Pick<User, "role"> | null | undefined): boolean => user?.role === "admin";
