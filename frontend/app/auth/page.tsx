"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import AuthPage from "@/fsd/pages/auth/ui/AuthPage";
import { useAuth } from "@/app/providers/auth/AuthContext";

const LoadingScreen = ({ text }: { text: string }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <p className="text-lg text-slate-500">{text}</p>
    </div>
  );
};

export default function AuthRoutePage() {
  const router = useRouter();
  const auth = useAuth();

  useEffect(() => {
    if (!auth) {
      return;
    }

    if (!auth.isRestoringSession && !auth.isUserLoading && auth.user) {
      router.replace("/dashboard");
    }
  }, [auth, router]);

  if (!auth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-50 text-slate-700">
        <div className="rounded-2xl border border-red-200 bg-white p-6 shadow-lg">
          <h2 className="text-2xl font-semibold text-red-500">Контекст аутентификации не найден</h2>
        </div>
      </div>
    );
  }

  if (auth.isRestoringSession) {
    return <LoadingScreen text="Загрузка сессии..." />;
  }

  if (auth.isUserLoading) {
    return <LoadingScreen text="Загрузка пользователя..." />;
  }

  if (auth.user) {
    return <LoadingScreen text="Переадресация..." />;
  }

  return <AuthPage />;
}
