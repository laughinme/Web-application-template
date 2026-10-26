import { expect, test, type Page } from "@playwright/test";
import type { UserDto } from "../src/shared/api/profile";

async function mockApi(page: Page) {
  let session = false;
  let refreshes = 0;
  let profile: UserDto = {
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
  const tokens = { access_token: "test-access-token", refresh_token: null, token_type: "bearer", expires_in: 900 };

  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    if (["/api/v1/auth/login", "/api/v1/auth/register"].includes(path)) {
      session = true;
      await route.fulfill({
        status: path.endsWith("register") ? 201 : 200,
        json: tokens,
        headers: { "set-cookie": "csrf_token=test-csrf-token; Path=/; SameSite=Lax" },
      });
    } else if (path === "/api/v1/auth/refresh") {
      refreshes++;
      expect(request.headers()["x-csrf-token"]).toBe("test-csrf-token");
      await route.fulfill({ status: session ? 200 : 401, json: session ? tokens : {} });
    } else if (path === "/api/v1/auth/logout") {
      session = false;
      await route.fulfill({ status: 204 });
    } else if (path === "/api/v1/users/me") {
      expect(request.headers().authorization).toBe("Bearer test-access-token");
      if (request.method() === "PATCH") profile = { ...profile, ...request.postDataJSON() };
      await route.fulfill({ json: profile });
    } else {
      throw new Error(`Unexpected API request: ${request.method()} ${path}`);
    }
  });
  return { refreshes: () => refreshes };
}

async function signIn(page: Page, register = false) {
  if (register) await page.getByRole("button", { name: "Sign up", exact: true }).click();
  await page.getByLabel("Email", { exact: true }).fill("member@example.com");
  await page.getByLabel("Password", { exact: true }).fill("StrongPassword123!");
  await page.getByRole("button", { name: register ? "Create Account" : "Login", exact: true }).click();
}

test("registration, profile updates, session restore and logout preserve navigation", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const api = await mockApi(page);
  await page.goto("/profile?tab=details");
  await expect(page).toHaveURL(/\/auth\?next=%2Fprofile%3Ftab%3Ddetails$/);
  await expect(page.getByRole("button", { name: "Login", exact: true })).toBeVisible();
  await signIn(page, true);
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
  await expect(page).toHaveURL(/\/profile\?tab=details$/);
  expect(api.refreshes()).toBe(1);
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);

  await page.getByRole("link", { name: "Dashboard", exact: true }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText("Total Visitors", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Меню пользователя" }).click();
  await page.getByRole("menuitem", { name: "Account", exact: true }).click();
  await expect(page).toHaveURL(/\/profile$/);
  await page.getByRole("button", { name: "Меню пользователя" }).click();
  await page.getByRole("menuitem", { name: "Log out", exact: true }).click();
  await expect(page).toHaveURL(/\/auth\?next=%2Fprofile$/);
  await page.reload();
  await signIn(page);
  await expect(page).toHaveURL(/\/profile$/);
  expect(api.refreshes()).toBe(1);
  expect(errors).toEqual([]);
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
