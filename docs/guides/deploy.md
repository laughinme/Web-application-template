# Деплой

## Варианты

| Куда | Когда | Как |
| --- | --- | --- |
| Домашний сервер (по умолчанию) | демо, хакатоны, пет-проекты, всё без особых требований к SLA | скилл `home-server-deploy` |
| Fly.io | нужен публичный облачный хостинг с регионами | `backend/fly.toml`, workflow `.github/workflows/backend.yml` (ручной запуск) |
| Любой хост с Docker | свой VPS | `docker compose up -d` из корня |

## Домашний сервер

Ubuntu и Coolify дома, домен `<app>.prooood.ru`, HTTPS через Let's Encrypt, автодеплой из GitHub
Actions: образы собираются в GHCR с тегом SHA коммита, сервер по Tailscale получает команду
`sara-deploy <app> <sha>` и ждёт healthy-контейнеров. Сам сервер ничего не собирает.

Агенту достаточно попросить «задеплой на мой сервер»: скилл `home-server-deploy` знает шаги
(файлы в `deploy/home/`, workflow `deploy-home.yml`, `sara-onboard`, DNS, секреты CI, откат).
Устройство сервера, правила общего хостинга и список проектов лежат в
`/Users/laughinme/Code/python/sara-hosting` (`AGENTS.md`, `CONTEXT.md`, `docs/DEPLOY-GUIDE.md`).

Что шаблон уже даёт для этого пути:

- отдельные Dockerfile для бэкенда (uv, multi-stage, не root) и фронтенда (Next standalone);
- `/api/health` без авторизации и внешних ключей;
- миграции отдельным одноразовым сервисом `migrate`;
- настройки только из окружения, приложение стартует без ключей Telegram и прочих внешних сервисов.

Ограничения сервера: 4 ядра без AVX, без GPU, около 1 ГиБ памяти на проект, наружу открыты только
80 и 443. Локальные LLM и тяжёлые ML-зависимости туда не подходят, модели вызываются по API.

## Fly.io

`backend/fly.toml` описывает процессы `app` и `worker` и `release_command` с миграциями. Секреты
задаются через `fly secrets set`. Workflow `backend.yml` запускается вручную, чтобы пуш в `main` не
деплоил шаблон.

## Чек-лист перед первым деплоем

- `APP_STAGE=prod`, свои `CSRF_HMAC_KEY` и ключи хранилища, `COOKIE_SECURE=true`: иначе приложение
  не стартует (так задумано).
- JWT-ключи из секрет-менеджера (`JWT_PRIVATE_KEY`, `JWT_PUBLIC_KEY`), а не из файлов в образе.
- `LOG_JSON=true`, `API_DOCS_ENABLED=false`, если документация API не должна быть публичной.
- Бэкап Postgres настроен (на домашнем сервере сервис `db-backup` из шаблона скилла).
