import { useInfiniteQuery, useQuery } from "@tanstack/react-query";
import type { UsersQuery } from "../model/types";
import { fetchMe, listUsers } from "./user-api";

// One place for cache keys, so features can invalidate exactly what they changed.
export const userKeys = {
  all: ["users"] as const,
  me: () => [...userKeys.all, "me"] as const,
  list: (query: UsersQuery) => [...userKeys.all, "list", query] as const,
};

export function useMe({ enabled = true }: { enabled?: boolean } = {}) {
  return useQuery({ queryKey: userKeys.me(), queryFn: fetchMe, enabled, staleTime: 60_000 });
}

export function useUsers(query: UsersQuery) {
  return useInfiniteQuery({
    queryKey: userKeys.list(query),
    queryFn: ({ pageParam }) => listUsers(query, pageParam),
    initialPageParam: null as string | null,
    getNextPageParam: (page) => page.nextCursor,
  });
}
