import { expect, test, type Page } from "@playwright/test";
import type { Schemas } from "../src/shared/api/types";

type UserDto = Schemas["UserOut"];

const baseUser: UserDto = {
  id: "00000000-0000-0000-0000-000000000001",
  email: "member@example.com",
  username: null,
  bio: null,
  avatar_key: null,
  avatar_url: null,
  role: "member",
  is_onboarded: false,
  banned: false,
  created_at: "2026-10-01T00:00:00Z",
  updated_at: "2026-10-01T00:00:00Z",
};

/** A small in-memory backend with the same cookie behaviour as FastAPI. */
async function mockApi(page: Page, { role = "member" }: { role?: UserDto["role"] } = {}) {
  let session = false;
  let refreshes = 0;
  let profile: UserDto = { ...baseUser, role };
  const others: UserDto[] = [
    { ...baseUser, id: "00000000-0000-0000-0000-000000000002", email: "ann@example.com", username: "Ann" },
  ];
  const tokens = { access_token: "test-access-token", refresh_token: null, token_type: "bearer", expires_in: 900 };
  const setCsrf = { "set-cookie": "csrf_token=test-csrf-token; Path=/; SameSite=Lax" };
  const clearCsrf = { "set-cookie": "csrf_token=; Path=/; Max-Age=0" };

  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    const method = request.method();
    if (["/api/v1/auth/login", "/api/v1/auth/register"].includes(path)) {
      session = true;
      await route.fulfill({ status: path.endsWith("register") ? 201 : 200, json: tokens, headers: setCsrf });
    } else if (path === "/api/v1/auth/refresh") {
      refreshes++;
      expect(request.headers()["x-csrf-token"]).toBe("test-csrf-token");
      await route.fulfill({ status: session ? 200 : 401, json: session ? tokens : {} });
    } else if (path === "/api/v1/auth/logout") {
      session = false;
      await route.fulfill({ status: 204, headers: clearCsrf });
    } else if (path === "/api/v1/users/me") {
      expect(request.headers().authorization).toBe("Bearer test-access-token");
      if (method === "PATCH") profile = { ...profile, ...request.postDataJSON() };
      await route.fulfill({ json: profile });
    } else if (path === "/api/v1/admin/users") {
      await route.fulfill({ json: { items: [profile, ...others], next_cursor: null } });
    } else if (/\/api\/v1\/admin\/users\/[^/]+\/ban$/.test(path)) {
      const target = others[0];
      target.banned = method === "POST";
      await route.fulfill({ json: target });
    } else if (path === "/api/v1/admin/stats/users") {
      await route.fulfill({
        json: { generated_at: "2026-10-02T00:00:00Z", total: 2, onboarded: 0, banned: 0, registered_last_24h: 1 },
      });
    } else if (path === "/api/v1/admin/stats/registrations") {
      await route.fulfill({ json: [{ day: new Date().toISOString().slice(0, 10), count: 2 }] });
    } else {
      throw new Error(`Unexpected API request: ${method} ${path}`);
    }
  });
  return { refreshes: () => refreshes };
}

async function signIn(page: Page, { register = false } = {}) {
  if (register) await page.getByRole("button", { name: "Зарегистрироваться", exact: true }).click();
  await page.getByLabel("Email", { exact: true }).fill("member@example.com");
  await page.getByLabel("Пароль", { exact: true }).fill("StrongPassword123!");
  await page.getByRole("button", { name: register ? "Создать аккаунт" : "Войти", exact: true }).click();
}

test("registration, profile edit, session restore and logout keep the return URL", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const api = await mockApi(page);

  await page.goto("/profile?tab=details");
  await expect(page).toHaveURL(/\/auth\?next=%2Fprofile%3Ftab%3Ddetails$/);
  await signIn(page, { register: true });
  await expect(page).toHaveURL(/\/profile\?tab=details$/);

  await page.getByLabel("Имя пользователя").fill("Updated member");
  await page.getByLabel("О себе").fill("Next.js profile");
  const update = page.waitForRequest((request) => request.method() === "PATCH");
  await page.getByRole("button", { name: "Сохранить", exact: true }).click();
  expect((await update).postDataJSON()).toEqual({ username: "Updated member", bio: "Next.js profile" });
  await expect(page.getByRole("heading", { name: "Updated member" })).toBeVisible();
  await expect(page.getByText("Профиль обновлён", { exact: true })).toBeVisible();

  await page.reload();
  await expect(page.getByLabel("Имя пользователя")).toHaveValue("Updated member");
  expect(api.refreshes()).toBe(1);
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);

  await expect(page.getByRole("link", { name: "Пользователи" })).toHaveCount(0);
  await page.getByRole("button", { name: "Меню пользователя" }).click();
  await page.getByRole("menuitem", { name: "Выйти" }).click();
  await expect(page).toHaveURL(/\/auth\?next=%2Fprofile%3Ftab%3Ddetails$/);

  await page.reload();
  expect(api.refreshes()).toBe(1); // the CSRF cookie is gone, so no refresh is even attempted
  await signIn(page);
  await expect(page).toHaveURL(/\/profile\?tab=details$/);
  expect(errors).toEqual([]);
});

test("an admin sees stats and can ban a user", async ({ page }) => {
  await mockApi(page, { role: "admin" });
  await page.goto("/admin");
  await signIn(page);

  await expect(page.getByRole("heading", { name: "Статистика" })).toBeVisible();
  await expect(page.getByText("Всего пользователей")).toBeVisible();

  await page.getByRole("link", { name: "Пользователи" }).click();
  const row = page.locator('[data-user="ann@example.com"]').filter({ visible: true });
  await row.getByRole("button", { name: "Заблокировать" }).click();
  await expect(row.getByText("Заблокирован", { exact: true })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
});

test("members get a notice instead of admin screens", async ({ page }) => {
  await mockApi(page);
  await page.goto("/admin/users");
  await signIn(page);
  await expect(page.getByText("Этот раздел доступен только администраторам")).toBeVisible();
});

for (const next of ["//example.com", "/\\example.com", "/auth?next=/auth", "https://example.com"]) {
  test(`rejects unsafe return URL ${next}`, async ({ page, baseURL }) => {
    await mockApi(page);
    await page.goto(`/auth?next=${encodeURIComponent(next)}`);
    await signIn(page);
    await expect(page).toHaveURL(new URL("/", baseURL).href);
    await expect(page.getByRole("link", { name: "Monolith", exact: true })).toBeVisible();
  });
}

test("unknown routes return a 404 and a working home link", async ({ page }) => {
  await mockApi(page);
  const response = await page.goto("/missing-page");
  expect(response?.status()).toBe(404);
  await expect(page.getByRole("heading", { name: "Страница не найдена" })).toBeVisible();
  await page.getByRole("link", { name: "На главную" }).click();
  await expect(page).toHaveURL(/\/auth\?next=%2F$/);
});
