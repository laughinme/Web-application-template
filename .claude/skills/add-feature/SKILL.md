---
name: add-feature
description: Add a feature to a project built on Monolith-template, end to end - domain types and rules, ORM model and Alembic migration, repository, service, API group with schemas, tests, OpenAPI types and the frontend slices (entity, feature, page, route). Use when asked to add an entity, resource, CRUD, endpoint or screen ("добавь посты", "новая сущность", "сделай эндпоинт и экран").
---

# Add a feature

Follow `docs/backend/new-feature.md` step by step; it is the source of truth and has code for every
step. Read `docs/backend/architecture.md` and `docs/frontend/architecture.md` first if you have not
in this session.

Order (the project builds after each step):

1. `domain/<zone>/`: models.py, errors.py (+ `ErrorCode` values in `core/errors.py`), rules.py,
   `__init__.py` with `__all__`. New permissions go into `Permission`.
2. `db/models/<zone>.py` + import in `db/models/__init__.py`; `make migration m="add <zone>"`;
   read the migration and check `downgrade()`.
3. `db/repositories/<zone>.py` with all SQL; register it on `UnitOfWork` in `db/uow.py`.
4. `service/<zone>/`: service class returning domain dataclasses, `flush()` only, external calls via
   `app/ports`, side effects via `uow.outbox.add` + handler.
5. `api/v1/<zone>/`: endpoint files, schemas.py, deps.py, `__init__.py` assembling the router;
   mount it in `api/v1/__init__.py`. Guard with `require(Permission.X)`.
6. Tests: unit for rules, integration for every endpoint (success + main error).
7. `make openapi`; frontend `entities/<zone>` (mapper, api, query keys), `features/<verb-object>`,
   `_pages/<name>`, route in `app/`, link in `widgets/app-header`, Playwright test.
8. `make check` and `make frontend-test` green; screenshots at 1440 and 390 px for new screens.
   Record a decision in `docs/DECISIONS.md` if the feature changed an approach.

Commit after each meaningful step (backend slice, frontend slice), Conventional Commits, no assistant
attribution.
