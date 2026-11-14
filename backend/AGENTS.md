# Backend rules

Read [docs/backend/architecture.md](../docs/backend/architecture.md) before changing code here.

- Layers: `api → service → domain`; `db`, `infra` and `ports` beside them. Each layer is split into
  zones (`api/v1/<group>/`, `service/<zone>/`, `domain/<zone>/`). `uv run lint-imports` enforces the
  boundaries; a broken contract is fixed in the code, not in the contract.
- Imports are absolute from `app.`. Outside a zone import its package (`from app.domain.users import
  Role`); inside a zone import the sibling module. `api/v1/<group>/__init__.py` assembles the router.
- One transaction per request: only the UoW owner commits (`UowDep`, worker, CLI, OutboxDispatcher).
  Services call `await uow.flush()`.
- ORM models stay in `db` and `service`. Services return domain dataclasses; routers return
  `XxxOut.from_domain(...)`. SQL lives in repositories only.
- External systems go behind a Protocol in `app/ports/`, implemented in `app/infra/`. Services never
  import infra or SDKs.
- Side effects (HTTP calls, emails, file deletion) go through the outbox: `uow.outbox.add(Topic.X, ...)`,
  a handler in `service/outbox/handlers.py`, idempotent.
- Expected errors subclass `DomainError` with an `ErrorCode`; never raise `HTTPException` from services.
  New codes also reach the frontend via `make openapi`.
- Permissions: `require(Permission.X)` on the endpoint; data-dependent rules in `domain/<zone>/rules.py`.
- No `Settings()` or clients at import time; long-lived objects are built in `create_app()`/the worker.
- New table or column: model + `make migration m="..."`, read the file, keep a working `downgrade()`.
- Every endpoint gets an integration test (success and the main error); domain rules get unit tests.
- Python 3.13, full type hints, `mypy --strict`, ruff (line length 100). No module docstrings or
  header comments; comments explain "why".
- New feature end to end: [docs/backend/new-feature.md](../docs/backend/new-feature.md) or the
  `add-feature` skill.
