import { useEffect, useState, type FormEvent, type ReactElement } from "react";
import { useAuth } from "../../context/useAuth";
import type { AuthCredentials } from "../../types/auth";

type Mode = "login" | "register";

const getErrorMessage = (error: unknown): string => {
  if (!error) {
    return "Произошла ошибка";
  }

  if (typeof error === "string") {
    return error;
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  if (typeof error === "object" && error !== null && "response" in error) {
    const response = (error as { response?: { data?: { detail?: unknown } } }).response;
    const detail = response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
  }

  return "Произошла ошибка";
};

export default function AuthPage(): ReactElement {
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [isVisible, setIsVisible] = useState<boolean>(false);

  const auth = useAuth();

  useEffect(() => {
    setIsVisible(true);
  }, []);

  if (!auth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-50 text-slate-700">
        <div className="rounded-2xl border border-red-200 bg-white p-6 shadow-lg">
          <h2 className="text-2xl font-semibold text-red-500">Контекст аутентификации не найден</h2>
          <p className="mt-2">Убедитесь, что используете компонент внутри `AuthProvider`.</p>
        </div>
      </div>
    );
  }

  const { login, register, isLoggingIn, loginError, isRegistering, registerError } = auth;

  const isLoading = isLoggingIn || isRegistering;
  const error = mode === "login" ? loginError : registerError;
  const errorMessage = error ? getErrorMessage(error) : null;
  const canSubmit = Boolean(email.trim() && password.trim() && !isLoading);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!canSubmit) {
      return;
    }

    const credentials: AuthCredentials = { email: email.trim(), password };

    try {
      if (mode === "login") {
        await login(credentials);
      } else {
        await register(credentials);
      }
    } catch (err) {
      console.error("Ошибка аутентификации:", err);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 via-white to-cyan-50" />
        <div className="absolute top-0 left-0 h-full w-full">
          <div className="absolute top-20 left-20 h-72 w-72 rounded-full bg-purple-300 opacity-70 mix-blend-multiply filter blur-xl animate-blob" />
          <div className="absolute top-40 right-20 h-72 w-72 rounded-full bg-yellow-300 opacity-70 mix-blend-multiply filter blur-xl animate-blob animation-delay-2000" />
          <div className="absolute -bottom-8 left-40 h-72 w-72 rounded-full bg-pink-300 opacity-70 mix-blend-multiply filter blur-xl animate-blob animation-delay-4000" />
        </div>
      </div>

      <div className="relative min-h-screen flex items-center justify-center px-4">
        <div
          className={`w-full max-w-md transform transition-all duration-1000 ${
            isVisible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
          }`}
        >
          <div className="relative rounded-3xl border border-white/30 bg-white/20 p-8 shadow-2xl backdrop-blur-lg">
            <div className="mb-8 text-center">
              <h1 className="mt-6 text-4xl font-bold leading-tight tracking-tight text-transparent md:text-5xl bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 bg-clip-text">
                {mode === "login" ? "Добро пожаловать" : "Создать аккаунт"}
              </h1>
              <p className="mt-3 text-lg font-medium text-gray-600">
                {mode === "login" ? "Рады видеть вас снова" : "Присоединяйтесь к нам"}
              </p>
            </div>

            <form className="space-y-6" onSubmit={submit}>
              {errorMessage ? (
                <div className="rounded-2xl border border-red-200 bg-red-50/80 p-4 text-center text-red-700">
                  <span>{errorMessage}</span>
                </div>
              ) : null}
              <input
                className="h-14 w-full rounded-2xl border border-white/50 bg-white/80 px-6 outline-none focus:ring-2 focus:ring-indigo-300"
                placeholder="Адрес электронной почты"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                disabled={isLoading}
                autoComplete="email"
                required
              />
              <input
                className="h-14 w-full rounded-2xl border border-white/50 bg-white/80 px-6 outline-none focus:ring-2 focus:ring-purple-300"
                placeholder="Пароль"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                disabled={isLoading}
                autoComplete="current-password"
                required
              />
              <button
                className="h-14 w-full rounded-2xl text-lg font-semibold text-white transition-all disabled:bg-gray-200 bg-gradient-to-r from-indigo-600 to-purple-600"
                type="submit"
                disabled={!canSubmit}
              >
                {isLoading ? "Загрузка..." : mode === "login" ? "Войти" : "Зарегистрироваться"}
              </button>
            </form>

            <div className="mt-8 text-center">
              {mode === "login" ? (
                <button
                  className="font-semibold text-indigo-600"
                  type="button"
                  onClick={() => setMode("register")}
                >
                  Нет аккаунта? Зарегистрироваться
                </button>
              ) : (
                <button className="font-semibold text-indigo-600" type="button" onClick={() => setMode("login")}>
                  Уже есть аккаунт? Войти
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
