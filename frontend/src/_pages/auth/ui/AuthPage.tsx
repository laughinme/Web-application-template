import { AuthCard } from "@/features/auth";

export function AuthPage() {
  return (
    <main className="flex min-h-svh flex-col items-center justify-center gap-6 bg-muted/40 px-4 py-12">
      <p className="text-sm font-bold tracking-widest uppercase">Monolith</p>
      <AuthCard />
    </main>
  );
}
