# Fullstack monolith template

Шаблон веб-приложения и справочник договорённостей для новых проектов. Бэкенд: FastAPI,
SQLAlchemy 2 (async), Postgres, Redis, S3-совместимое хранилище, outbox-воркер. Фронтенд: Next.js,
React, TypeScript, Feature-Sliced Design. Перед ними nginx. Из коробки есть регистрация и вход
(web и mobile), профиль с аватаром, админка со статистикой и модерацией, миграции, тесты на
настоящей инфраструктуре и CI.

Документация: [docs/README.md](docs/README.md). Правила для агентов: [AGENTS.md](AGENTS.md).
Новый проект на основе шаблона: [docs/guides/new-project.md](docs/guides/new-project.md).

## Быстрый старт

Нужны Docker, Node.js 22+, [uv](https://docs.astral.sh/uv/) и `make`.

```bash
make install                      # зависимости Python и Node.js, backend/.env, JWT-ключи
make up                           # весь стек: http://localhost, API на :8080
make admin email=me@example.com   # первый администратор
```

Документация API в dev: <http://localhost:8080/api/docs>

## Команды

```bash
make help            # все команды
make check           # всё, что гоняет CI: ruff, import-linter, mypy, тесты, ESLint, tsc, steiger, vitest, build
make test-unit       # unit-тесты бэкенда без Docker, около секунды
make test            # все тесты бэкенда; сам поднимет Postgres, Redis и S3
make frontend-test   # Playwright на 1440, 1366 и 390 px (нужен Playwright Chromium)
make frontend-dev    # Next.js с hot reload на :3000
make run / worker    # API с перезагрузкой и воркер outbox локально
make migration m="add posts"   # миграция по изменениям моделей
make migrate         # применить миграции
make openapi         # frontend/openapi.json и TS-типы после изменения API
make up / down / logs          # стек в Docker
```

## Структура

```text
backend/app/
  api/v1/<группа>/   HTTP: эндпоинты, схемы, зависимости группы
  service/<зона>/    сценарии использования; не знают про HTTP; не коммитят
  domain/<зона>/     типы, ошибки и правила без фреймворков
  ports/             абстракции внешнего мира (хранилище, уведомления)
  infra/             адаптеры: S3, Telegram, rate limit
  db/                ORM-модели, репозитории, Unit of Work
  core/              настройки, ошибки, логи, безопасность
backend/migrations/  Alembic
backend/tests/       unit/ и integration/
frontend/app/        маршруты Next.js (только реэкспорт страниц)
frontend/src/        _app, _pages, widgets, features, entities, shared (FSD)
docs/                статус, решения, архитектура, гайды, шаблоны файлов
nginx/               прокси Next.js, /api и медиа
```

Границы слоёв проверяют import-linter (бэкенд) и steiger (фронтенд) в `make check` и CI.

## Переменные окружения

Все настройки с комментариями: [backend/.env.example](backend/.env.example) и
[backend/app/core/config.py](backend/app/core/config.py). В `APP_STAGE=prod` приложение не
стартует с dev-секретами. Деплой: [docs/guides/deploy.md](docs/guides/deploy.md).

Старая версия шаблона лежит в ветке `legacy`.
