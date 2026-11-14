import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { updateMe, userKeys, type ProfilePatch } from "@/entities/user";

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (patch: ProfilePatch) => updateMe(patch),
    onSuccess: (user) => {
      queryClient.setQueryData(userKeys.me(), user);
      toast.success("Профиль обновлён");
    },
    onError: () => toast.error("Не удалось обновить профиль"),
  });
}
