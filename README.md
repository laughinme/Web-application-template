# Fullstack monolith template

Шаблон веб-приложения: FastAPI + SQLAlchemy 2 (async) + Postgres + Redis + S3-совместимое хранилище
на бэкенде, React SPA на фронте, nginx перед ними. Из коробки: регистрация и вход (web и mobile),
профиль с аватаром, админка, фоновый воркер, миграции, тесты на настоящей инфраструктуре и CI.

**Как всё устроено и почему: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).** Там слои, транзакции,
аутентификация, тесты, рецепт добавления фичи и сравнение со старой версией (она в ветке `legacy`).

## Быстрый старт

Нужны Docker, [uv](https://docs.astral.sh/uv/) и `make`.

```bash
make install                      # зависимости, backend/.env, JWT-ключи
make up                           # весь стек: http://localhost (SPA), API на :8080
make admin email=me@example.com   # первый администратор
```

Документация API в dev: <http://localhost:8080/api/docs>

## Команды

```bash
make help        # все команды
make test-unit   # unit-тесты без Docker, ~1 с
make test        # все тесты: сам поднимет Postgres/Redis/S3 для тестов, ~5 с
make check       # lint + mypy --strict + все тесты (то же, что CI)
make fmt         # отформатировать и автоисправить
make run         # API с автоперезагрузкой локально
make worker      # воркер outbox локально
make migration m="add posts"   # миграция по изменениям моделей
make migrate     # применить миграции
make openapi     # обновить frontend/openapi.json
make up / down / logs          # стек в Docker
```

## Структура

```text
backend/
  app/
    api/        HTTP: роутеры, схемы, зависимости, формат ошибок, middleware
    service/    сценарии использования; не знают про HTTP; не коммитят
    domain/     правила и типы без FastAPI и SQLAlchemy
    db/         ORM-модели, репозитории, Unit of Work
    infra/      S3, Telegram, rate limit
    core/       настройки, ошибки, логи, безопасность
    main.py     create_app()
    worker.py   фоновый процесс (outbox)
  migrations/   Alembic
  tests/        unit/ и integration/
frontend/       React SPA
nginx/          SPA + прокси /api и медиа
```

## Переменные окружения

Все настройки с комментариями: [backend/.env.example](backend/.env.example) и
[backend/app/core/config.py](backend/app/core/config.py). В `APP_STAGE=prod` приложение не стартует
с dev-секретами.
