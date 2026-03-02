"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import DashboardPage from "@/fsd/pages/Dashboard";
import { useAuth } from "@/app/providers/auth/AuthContext";

const LoadingScreen = ({ text }: { text: string }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <p className="text-lg text-slate-500">{text}</p>
    </div>
  );
};

export default function DashboardRoutePage() {
  const router = useRouter();
  const auth = useAuth();

  useEffect(() => {
    if (!auth) {
      return;
    }

    if (!auth.isRestoringSession && !auth.isUserLoading && !auth.user) {
      router.replace("/auth");
    }
  }, [auth, router]);

  if (!auth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-100">
        <div className="p-8 bg-white rounded-lg shadow-md text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-2">Ошибка конфигурации</h1>
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

  if (!auth.user) {
    return <LoadingScreen text="Переадресация..." />;
  }

  return <DashboardPage />;
}
