# Тесты бэкенда

```bash
make test-unit   # только unit, без Docker, около секунды
make test        # всё: поднимет Postgres, Redis и S3 из docker-compose.test.yml, около 6 с
make test-down   # убрать тестовые контейнеры
make check       # ruff, import-linter, mypy, тесты бэкенда и все проверки фронтенда: то же, что CI
cd backend && uv run pytest tests/integration/api/test_auth.py -k refresh   # один файл или тест
```

Тестовые контейнеры слушают другие порты (5439, 6380, 9002) и не мешают dev-стеку. Postgres в них
живёт в `tmpfs`.

## Что каким уровнем

| Что проверяем | Уровень | Где |
| --- | --- | --- |
| правило («нельзя банить админа»), курсор, токены, пароли | unit | `tests/unit/domain`, `tests/unit/core` |
| сценарий с ветками (замена аватара, PATCH) | unit, сервис с фейками | `tests/unit/service` |
| SQL, транзакции, cookies, заголовки, формат ошибок | integration | `tests/integration/api` |
| outbox, миграции, контракт OpenAPI | integration или unit | `tests/integration`, `tests/unit/test_openapi.py` |

У каждого эндпоинта есть хотя бы один интеграционный тест на успех и один на главную ошибку.

Интеграционные тесты работают с настоящим приложением через `httpx.ASGITransport` (lifespan и
middleware включены, сети нет) и настоящими Postgres, Redis и S3. Схему создают настоящие
миграции, так что тесты заодно проверяют их. Всё в `tests/integration/` автоматически получает
маркер `integration`.

## Фикстуры

| Фикстура | Что даёт |
| --- | --- |
| `client` | `httpx.AsyncClient` к приложению; база и Redis очищены перед тестом |
| `user`, `admin` | зарегистрированный аккаунт: `.headers`, `.refresh_token`, `.email` |
| `db`, `storage` | `Database` и `ObjectStorage` приложения |
| `run_outbox` | `await run_outbox()`: одна итерация воркера |
| `notifier` | `RecordingNotifier`: что «ушло в Telegram»; `fail_with` для проверки ретраев |
| `app_factory` | приложение с другими настройками: `async with app_factory(rate_limit_enabled=True) as (app, client)` |
| `make_settings` | `Settings` для тестов с переопределениями |

Помощники для данных лежат в `tests/factories.py`: `register`, `login`, `promote`.

## Примеры

```python
async def test_ban_kills_sessions_and_blocks_login(admin: Account, user: Account, client: AsyncClient) -> None:
    banned = await client.post(f"/api/v1/admin/users/{user.id}/ban", headers=admin.headers)
    assert banned.json()["banned"] is True

    me = await client.get("/api/v1/users/me", headers=user.headers)
    assert me.status_code == 401
```

```python
async def test_registration_notifies_after_commit(client, db, notifier, run_outbox) -> None:
    await register(client, email="new@example.com")
    assert notifier.messages == []          # из запроса ничего не отправлено
    assert await run_outbox() == 1
    assert notifier.messages == ["New user registered: new@example.com"]
```

Сервис без базы: он получает UoW и порты в конструкторе, поэтому хватает фейков
(`tests/unit/service/test_profile.py`):

```python
service = ProfileService(FakeUow(user), FakeStorage(), presign_expires_sec=60, max_avatar_bytes=1024)
```

## Строгость

`filterwarnings = error::DeprecationWarning:app.*`: устаревший API в нашем коде роняет тесты.
`test_models_match_migrations` падает, если модель поменяли без миграции.
`test_openapi_publishes_the_error_contract` следит, что фронтенд получает полный список `ErrorCode`.
