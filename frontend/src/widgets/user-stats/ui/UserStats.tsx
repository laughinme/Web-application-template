"use client";

import { Bar, BarChart, CartesianGrid, XAxis } from "recharts";
import { useRegistrations, useUsersSummary, type DailyCount } from "@/entities/user-activity";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent, type ChartConfig } from "@/shared/ui/chart";
import { Skeleton } from "@/shared/ui/skeleton";

const DAYS = 30;
const chartConfig = { count: { label: "Регистрации", color: "var(--primary)" } } satisfies ChartConfig;

// The API returns only days that had registrations; the chart needs every day of the range.
function lastDays(rows: DailyCount[], days: number): DailyCount[] {
  const counts = new Map(rows.map((row) => [row.day, row.count]));
  const today = new Date();
  return Array.from({ length: days }, (_, index) => {
    const date = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate() - (days - 1 - index)));
    const day = date.toISOString().slice(0, 10);
    return { day, count: counts.get(day) ?? 0 };
  });
}

function Counter({ label, value }: { label: string; value: number | undefined }) {
  return (
    <Card className="gap-2 py-4">
      <CardHeader className="px-4">
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-3xl tabular-nums">
          {value === undefined ? <Skeleton className="h-9 w-16" /> : value.toLocaleString("ru-RU")}
        </CardTitle>
      </CardHeader>
    </Card>
  );
}

export function UserStats() {
  const summary = useUsersSummary().data;
  const registrations = useRegistrations(DAYS);
  const shortDate = (day: string) =>
    new Date(day).toLocaleDateString("ru-RU", { day: "numeric", month: "short", timeZone: "UTC" });

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Counter label="Всего пользователей" value={summary?.total} />
        <Counter label="Новые за 24 часа" value={summary?.registered_last_24h} />
        <Counter label="Прошли онбординг" value={summary?.onboarded} />
        <Counter label="Заблокированы" value={summary?.banned} />
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Регистрации</CardTitle>
          <CardDescription>За последние {DAYS} дней, по UTC</CardDescription>
        </CardHeader>
        <CardContent>
          {registrations.data ? (
            <ChartContainer config={chartConfig} className="aspect-auto h-64 w-full">
              <BarChart data={lastDays(registrations.data, DAYS)} margin={{ left: 0, right: 0 }}>
                <CartesianGrid vertical={false} />
                <XAxis dataKey="day" tickLine={false} axisLine={false} tickMargin={8} minTickGap={24} tickFormatter={shortDate} />
                <ChartTooltip content={<ChartTooltipContent labelFormatter={(day) => shortDate(String(day))} />} />
                <Bar dataKey="count" fill="var(--color-count)" radius={4} />
              </BarChart>
            </ChartContainer>
          ) : (
            <Skeleton className="h-64 w-full" />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
