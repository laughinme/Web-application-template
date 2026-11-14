import { isAxiosError } from "axios";
import type { ErrorCode, ProblemDto } from "./types";

// Every backend error is an RFC 7807 problem with a closed `error_code`. Screens map codes to
// their own wording; `detail` is a developer message and is only the last fallback.

export function toProblem(error: unknown): ProblemDto | null {
  if (!isAxiosError(error)) return null;
  const data: unknown = error.response?.data;
  if (typeof data === "object" && data !== null && "error_code" in data && "status" in data) {
    return data as ProblemDto;
  }
  return null;
}

export function errorCode(error: unknown): ErrorCode | null {
  return toProblem(error)?.error_code ?? null;
}

export function problemMessage(
  error: unknown,
  messages: Partial<Record<ErrorCode, string>>,
  fallback = "Что-то пошло не так. Попробуйте ещё раз",
): string {
  const problem = toProblem(error);
  if (!problem) return isAxiosError(error) && !error.response ? "Нет связи с сервером" : fallback;
  return messages[problem.error_code] ?? COMMON_MESSAGES[problem.error_code] ?? fallback;
}

const COMMON_MESSAGES: Partial<Record<ErrorCode, string>> = {
  RATE_LIMITED: "Слишком много попыток, подождите минуту",
  FORBIDDEN: "Недостаточно прав",
  ACCOUNT_BANNED: "Аккаунт заблокирован",
  INTERNAL_ERROR: "Ошибка на сервере. Мы уже знаем",
};
