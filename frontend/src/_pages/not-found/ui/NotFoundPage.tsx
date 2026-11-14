import Link from "next/link";
import { routes } from "@/shared/config";

export function NotFoundPage() {
  return (
    <main className="flex min-h-svh flex-col items-center justify-center gap-4 px-4 text-center">
      <h1 className="text-2xl font-semibold">Страница не найдена</h1>
      <Link href={routes.home} className="underline underline-offset-4">
        На главную
      </Link>
    </main>
  );
}
