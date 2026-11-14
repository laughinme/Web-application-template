import { useQuery } from "@tanstack/react-query";
import { api, type Schemas } from "@/shared/api";

export type UsersSummary = Schemas["UsersSummaryOut"];
export type DailyCount = Schemas["DailyCountOut"];

export const statsKeys = {
  all: ["stats"] as const,
  summary: () => [...statsKeys.all, "users"] as const,
  registrations: (days: number) => [...statsKeys.all, "registrations", days] as const,
};

export function useUsersSummary() {
  return useQuery({
    queryKey: statsKeys.summary(),
    queryFn: async () => (await api.get<UsersSummary>("/admin/stats/users")).data,
  });
}

export function useRegistrations(days: number) {
  return useQuery({
    queryKey: statsKeys.registrations(days),
    queryFn: async () =>
      (await api.get<DailyCount[]>("/admin/stats/registrations", { params: { days } })).data,
  });
}
