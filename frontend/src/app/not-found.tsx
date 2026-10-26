import Link from "next/link";

export default function NotFound() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-semibold">Страница не найдена</h1>
      <Link href="/" className="underline underline-offset-4">На главную</Link>
    </main>
  );
}
