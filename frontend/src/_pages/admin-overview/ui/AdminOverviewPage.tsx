import { UserStats } from "@/widgets/user-stats";

export function AdminOverviewPage() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold tracking-tight">Статистика</h1>
      <UserStats />
    </div>
  );
}
