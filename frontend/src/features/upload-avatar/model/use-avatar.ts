import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { removeAvatar, uploadAvatar, userKeys } from "@/entities/user";
import { problemMessage } from "@/shared/api";

const MESSAGES = {
  AVATAR_TOO_LARGE: "Файл слишком большой",
  AVATAR_TYPE_UNSUPPORTED: "Нужен JPEG, PNG или WebP",
} as const;

export function useUploadAvatar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => uploadAvatar(file),
    onSuccess: (user) => {
      queryClient.setQueryData(userKeys.me(), user);
      toast.success("Фото обновлено");
    },
    onError: (error) => toast.error(problemMessage(error, MESSAGES, "Не удалось загрузить фото")),
  });
}

export function useRemoveAvatar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: removeAvatar,
    onSuccess: (user) => queryClient.setQueryData(userKeys.me(), user),
    onError: () => toast.error("Не удалось удалить фото"),
  });
}
