import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { statsKeys } from "@/entities/user-activity";
import { banUser, setUserRole, unbanUser, userKeys, type Role, type User } from "@/entities/user";
import { problemMessage } from "@/shared/api";

const MESSAGES = {
  SELF_MODERATION: "Нельзя менять роль или блокировать самого себя",
  ADMIN_PROTECTED: "Администратора нельзя заблокировать: сначала снимите роль",
} as const;

function useAfterModeration() {
  const queryClient = useQueryClient();
  return {
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: userKeys.all });
      void queryClient.invalidateQueries({ queryKey: statsKeys.all });
    },
    onError: (error: unknown) => toast.error(problemMessage(error, MESSAGES)),
  };
}

export function useToggleBan() {
  const callbacks = useAfterModeration();
  return useMutation({
    mutationFn: (user: User) => (user.banned ? unbanUser(user.id) : banUser(user.id)),
    ...callbacks,
  });
}

export function useSetRole() {
  const callbacks = useAfterModeration();
  return useMutation({
    mutationFn: ({ user, role }: { user: User; role: Role }) => setUserRole(user.id, role),
    ...callbacks,
  });
}
