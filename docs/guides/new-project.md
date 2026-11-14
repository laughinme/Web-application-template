# Новый проект на основе шаблона

Шаблон даёт бэкенд, фронтенд, инфраструктуру, тесты, CI и договорённости о контексте. Проект
забирает всё это и меняет только своё: продукт, дизайн, фичи.

## Шаги

1. Создать репозиторий из шаблона (GitHub «Use this template» или копия без `.git`), ветку
   `legacy` не переносить.
2. Переименовать: `name:` в `docker-compose.yml`, `title` в `backend/app/main.py`, `metadata` в
   `frontend/app/layout.tsx`, `Monolith` в `widgets/app-header` и `_pages/auth`, `app =` в
   `backend/fly.toml`.
3. `make install && make up`, затем `make check`: всё зелёное до первой правки.
4. Контекст из [docs/templates/](../templates/):
   - `AGENTS.md`: заменить описание шаблона описанием проекта, оставить ритуал, карту, правила;
   - `CLAUDE.md`: оставить как есть (`@AGENTS.md` и заметки для Claude);
   - `docs/STATUS.md` и `docs/DECISIONS.md` с первой записью «D-001. Основа: Monolith-template»;
   - материалы заказчика в `docs/case/` (только чтение), выжимка требований в `docs/case/BRIEF.md`.
5. Продукт и дизайн: `PRODUCT.md`, затем направление через `design-studio` и `DESIGN.md`
   ([design.md](design.md)). Нейтральный UI шаблона заменяется по токенам из `DESIGN.md`.
6. Удалить лишнее: если нет админки, убрать `api/v1/admin`, `service/moderation`,
   `service/stats`, `widgets/users-table`, `widgets/user-stats` и их тесты; если нет аватаров,
   S3 и RustFS из compose. `make check` после каждого удаления.
7. Фичи добавлять по [рецепту](../backend/new-feature.md) (скилл `add-feature`).
8. Деплой: на домашний сервер через `home-server-deploy` ([deploy.md](deploy.md)).

## Что не трогать без причины

Формат ошибок, UoW и одну транзакцию на запрос, outbox, схему аутентификации, контракты
import-linter и steiger. Если причина есть, сначала запись в `docs/DECISIONS.md`.

## Что взять в существующий проект

Шаблон можно использовать и как образец для старого кода: сравнить с
[backend/architecture.md](../backend/architecture.md) и перенести по частям. Сначала формат ошибок
и UoW, потом слои и контракты import-linter (контракты сразу показывают, где код нарушает границы).
