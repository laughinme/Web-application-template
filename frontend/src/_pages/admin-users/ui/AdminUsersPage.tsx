import { UsersTable } from "@/widgets/users-table";

export function AdminUsersPage() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold tracking-tight">Пользователи</h1>
      <UsersTable />
    </div>
  );
}
