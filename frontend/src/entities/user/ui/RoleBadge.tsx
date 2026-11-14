import { Badge } from "@/shared/ui/badge";
import type { Role } from "../model/types";

const LABELS: Record<Role, string> = { member: "Участник", admin: "Администратор" };

export function RoleBadge({ role }: { role: Role }) {
  return <Badge variant={role === "admin" ? "default" : "secondary"}>{LABELS[role]}</Badge>;
}
