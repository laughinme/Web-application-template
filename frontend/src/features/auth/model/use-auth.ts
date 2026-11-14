import { useMutation } from "@tanstack/react-query";
import { login, register, useSession, type Credentials, type Registration } from "@/entities/session";
import { problemMessage } from "@/shared/api";

export function useLogin() {
  const session = useSession();
  return useMutation({
    mutationFn: (credentials: Credentials) => login(credentials),
    onSuccess: (tokens) => session.start(tokens.access_token),
  });
}

export function useRegister() {
  const session = useSession();
  return useMutation({
    mutationFn: (registration: Registration) => register(registration),
    onSuccess: (tokens) => session.start(tokens.access_token),
  });
}

export const authErrorMessage = (error: unknown): string =>
  problemMessage(error, {
    WRONG_CREDENTIALS: "Неверный email или пароль",
    EMAIL_TAKEN: "Этот email уже зарегистрирован",
    REQUEST_VALIDATION_ERROR: "Проверьте email; пароль — не короче 8 символов",
  });
