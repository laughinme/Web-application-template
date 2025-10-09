import { useEffect, useState, type FormEvent, type ReactElement } from "react";
import { useAuth } from "../../context/useAuth";
import type { AuthCredentials } from "../../types/auth";
import { LoginForm } from "../login-form";
import { SignupForm } from "../signup-form";

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
    <div className="min-h-screen bg-muted flex items-center justify-center px-4 py-8">
      <div
        className={`w-full max-w-md transition-all duration-700 ease-out ${
          isVisible ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"
        }`}
      >
        {mode === "login" ? (
          <LoginForm
            email={email}
            password={password}
            onEmailChange={setEmail}
            onPasswordChange={setPassword}
            onSubmit={submit}
            submitLabel={isLoading ? "Загрузка..." : "Login"}
            disabled={isLoading}
            submitDisabled={!canSubmit}
            errorMessage={errorMessage}
            onSwitchToSignup={() => setMode("register")}
          />
        ) : (
          <SignupForm
            email={email}
            password={password}
            onEmailChange={setEmail}
            onPasswordChange={setPassword}
            onSubmit={submit}
            submitLabel={isLoading ? "Загрузка..." : "Create Account"}
            disabled={isLoading}
            submitDisabled={!canSubmit}
            errorMessage={errorMessage}
            onSwitchToLogin={() => setMode("login")}
          />
        )}
      </div>
    </div>
  );
}
