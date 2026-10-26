# AI Coding Guidelines

## Context & Documentation (Context7 MCP)

Always use Context7 MCP for library/API documentation, code generation, setup, and configuration questions without requiring the user to explicitly ask.
If the user provides an explicit Context7 library ID (for example, `/supabase/supabase`), skip library resolution and query that library directly.
If the user specifies a library version, prefer that version's documentation.
If Context7 is unavailable, state that briefly and fall back to official documentation.

## Backend architecture (read docs/ARCHITECTURE.md before changing backend code)

- Layers: `api -> service -> domain`; `db` and `infra` are adapters. `domain/` never imports FastAPI,
  SQLAlchemy or Pydantic; `service/` never imports FastAPI; `api/` never builds SQL or touches ORM models.
- One transaction per request: only the UoW owner commits (`UowDep`, worker, CLI). Services call
  `await uow.flush()`, never `commit()`.
- ORM objects stay inside `db/` and `service/`. Services return domain dataclasses; routers return
  `XxxOut.from_domain(...)`.
- Side effects (HTTP calls, emails, file deletion) go through the outbox (`uow.outbox.add`), never
  inside the request transaction.
- No `Settings()` or clients created at import time; everything long-lived is built in `create_app()`.
- Expected errors subclass `DomainError` with an `ErrorCode`; never raise `HTTPException` from services.
- Permissions are checked with `require(Permission.X)`, data-dependent rules live in `domain/`.
- New tables and columns: model change + `make migration m="..."`, read the generated file, keep a
  working `downgrade()`.
- Every endpoint gets at least one integration test; domain rules get unit tests.
- Before committing: `make check` must be green.

## Style

- Python 3.13, full type hints, `ruff format` (line length 100), `mypy --strict`.
- No module docstrings or header comments at the top of files. Comments explain "why", not "what".
- No commented-out code and no empty placeholder packages.
