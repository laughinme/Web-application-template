# Monolith-template

Шаблон и справочник для новых проектов владельца: FastAPI-монолит, Next.js на Feature-Sliced
Design, Postgres, Redis, S3, outbox-воркер, тесты на настоящей инфраструктуре, CI и договорённости
о том, как мы ведём код, документы и контекст для агентов. Общайся с пользователем на русском.

Если тебя привели сюда из другого проекта («сделай как в шаблоне»), начни с
[docs/README.md](docs/README.md) и [docs/guides/new-project.md](docs/guides/new-project.md).

## Ритуал сессии

1. Прочитай [docs/STATUS.md](docs/STATUS.md) и [docs/DECISIONS.md](docs/DECISIONS.md), затем
   документ своей части: [бэкенд](docs/backend/architecture.md), [фронтенд](docs/frontend/architecture.md).
2. Перед изменением подхода проверь DECISIONS: причина, скорее всего, уже записана.
3. В конце заметного этапа перепиши `docs/STATUS.md` и добавь решения в `docs/DECISIONS.md`
   (D-NNN: решение, почему, что отвергли). Журналы сессий не ведём.

## Карта

| Где | Что |
| --- | --- |
| `backend/` | FastAPI: слои `api → service → domain`, `db`, `infra`, `ports`; правила в [backend/AGENTS.md](backend/AGENTS.md) |
| `frontend/` | Next.js + FSD; правила в [frontend/AGENTS.md](frontend/AGENTS.md) |
| `docs/` | статус, решения, архитектура частей, гайды, шаблоны файлов: [оглавление](docs/README.md) |
| `nginx/`, `docker-compose*.yml`, `Makefile` | стек в Docker, тестовая инфраструктура, команды |
| `.github/workflows/` | CI бэкенда и фронтенда, ручной деплой на Fly |
| `.claude/skills/add-feature` | процедура новой фичи от таблицы до экрана |

## Правила

- Код, идентификаторы и коммиты на английском; интерфейс и документация на русском.
- Документацию библиотек бери через Context7 MCP, а не по памяти. Если Context7 недоступен, скажи
  об этом и иди в официальную документацию.
- Визуальная работа начинается со скилла `design-studio` ([docs/guides/design.md](docs/guides/design.md)).
  Тексты для людей проходят через скилл `humanizer` ([docs/guides/writing.md](docs/guides/writing.md)).
- Деплой по умолчанию на домашний сервер через скилл `home-server-deploy` ([docs/guides/deploy.md](docs/guides/deploy.md)).
- Архитектурные границы проверяют import-linter (бэкенд) и steiger (фронтенд). Если контракт мешает,
  сначала запись в DECISIONS, потом изменение контракта, а не обход.
- Никаких шапок и модульных докстрингов в начале файлов; комментарий объясняет «почему». Без
  закомментированного кода и пустых пакетов.
- Коммиты по ходу работы: один законченный шаг на коммит, Conventional Commits, только свои файлы
  (`git add <пути>`), без подписей ассистентов. Секреты (`backend/secrets/`, `.env`) не коммитим.
- Перед коммитом `make check` зелёный; для UI ещё `make frontend-test` и скриншоты 1440 и 390 px.

## Команды

```bash
make install                      # зависимости, backend/.env, JWT-ключи
make up                           # весь стек: http://localhost, API на :8080, /api/docs
make check                        # ruff, import-linter, mypy, тесты бэкенда, ESLint, tsc, steiger, vitest, build
make test                         # тесты бэкенда (сам поднимет Postgres, Redis, S3)
make frontend-test                # Playwright на трёх ширинах
make migration m="add posts"      # миграция по моделям; прочитать файл глазами
make openapi                      # frontend/openapi.json и TS-типы после изменения API
make admin email=me@example.com   # первый администратор
```

## Куда записывать

| Что произошло | Куда |
| --- | --- |
| Решение | `docs/DECISIONS.md` |
| Закончили заметный кусок | `docs/STATUS.md`, переписать коротко |
| Поменялся API | `make openapi`, документ части |
| Новое правило для агентов | сначала попробовать сделать его проверкой (линтер, тест), иначе сюда или в `AGENTS.md` части |
| Повторяемая процедура | скилл в `.claude/skills/` |
