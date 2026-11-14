# Фронтенд

Next.js (App Router), React 19, TypeScript strict, Tailwind CSS 4, TanStack Query, shadcn/ui.
Код разложен по Feature-Sliced Design. Нужен Node.js 22 или новее.

```bash
npm ci
cp env-presets/local-backend.env .env.local
npm run dev            # http://localhost:3000, /api проксируется на бэкенд
npm run check          # ESLint, TypeScript, steiger (границы FSD), vitest, production build
npm run test:e2e       # Playwright на 1440, 1366 и 390 px (нужен: npx playwright install chromium)
npm run api:types      # типы API из openapi.json; из корня то же делает make openapi
```

Как устроены слои, куда класть новый код и как добавить экран:
[docs/frontend/architecture.md](../docs/frontend/architecture.md).
Прокси API, HTTPS и пресеты окружения: [README-dev.md](README-dev.md).

## Карта

```text
app/                 маршруты Next.js; каждый файл реэкспортирует страницу или layout из src/
src/
  _app/              провайдеры, layout'ы и guard'ы (вход, гость, админ), глобальные стили
  _pages/            экраны: home, auth, profile, admin-overview, admin-users, not-found
  widgets/           крупные блоки экранов: app-header, users-table, user-stats
  features/          действия пользователя: auth, logout, edit-profile, upload-avatar, moderate-user
  entities/          данные предметной области: session, user, user-activity
  shared/            api (http, ошибки, типы из OpenAPI), ui (shadcn), lib, config
tests/               Playwright со своим моком API
```

Слой импортирует только слои ниже себя. Слайс открывает наружу только свой `index.ts`.
Это проверяет `npm run check:architecture`.
