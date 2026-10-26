.DEFAULT_GOAL := help
.PHONY: help install env keys run worker lint fmt typecheck test test-unit test-deps test-down \
	check migrate migration admin openapi up down logs

BACKEND := backend
UV := cd $(BACKEND) && uv run
TEST_COMPOSE := docker compose -p monolith-template-test -f docker-compose.test.yml

help: ## Show this help
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "} {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

# --- setup -------------------------------------------------------------------

install: ## Install backend dependencies (uv) and create .env and JWT keys if missing
	cd $(BACKEND) && uv sync
	@$(MAKE) --no-print-directory env keys

env: ## Create backend/.env from the example (never overwrites)
	@test -f $(BACKEND)/.env || (cp $(BACKEND)/.env.example $(BACKEND)/.env && echo "created backend/.env")

keys: ## Generate the RS256 key pair into backend/secrets (never overwrites)
	@mkdir -p $(BACKEND)/secrets
	@test -f $(BACKEND)/secrets/jwt_private_key.pem || ( \
		openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out $(BACKEND)/secrets/jwt_private_key.pem && \
		openssl rsa -in $(BACKEND)/secrets/jwt_private_key.pem -pubout -out $(BACKEND)/secrets/jwt_public_key.pem && \
		echo "generated backend/secrets/jwt_*.pem")

# --- local development ---------------------------------------------------------

run: ## Run the API with reload (needs `make up` or your own Postgres/Redis/S3)
	$(UV) uvicorn app.main:create_app --factory --reload --port 8080

worker: ## Run the outbox worker
	$(UV) python -m app.worker

migrate: ## Apply migrations to the database from backend/.env
	$(UV) alembic upgrade head

migration: ## New migration from model changes: make migration m="add orders"
	@test -n "$(m)" || (echo 'usage: make migration m="what changed"' && exit 1)
	$(UV) alembic revision --autogenerate -m "$(m)"

admin: ## Create or promote an admin: make admin email=you@example.com
	@test -n "$(email)" || (echo 'usage: make admin email=you@example.com' && exit 1)
	$(UV) python -m app.cli create-admin "$(email)"

openapi: ## Export the OpenAPI schema for the frontend (frontend/openapi.json)
	$(UV) python -c "import json; from app.main import create_app; print(json.dumps(create_app().openapi(), indent=2, ensure_ascii=False))" > ../frontend/openapi.json.tmp
	mv frontend/openapi.json.tmp frontend/openapi.json

# --- quality -----------------------------------------------------------------------

lint: ## Ruff lint and format check
	$(UV) ruff check .
	$(UV) ruff format --check .

fmt: ## Format and autofix
	$(UV) ruff format .
	$(UV) ruff check --fix .

typecheck: ## mypy --strict
	$(UV) mypy

test-unit: ## Unit tests only: no Docker needed, ~1 s
	$(UV) pytest tests/unit -q

test-deps: ## Start throwaway Postgres/Redis/S3 for integration tests (kept running between runs)
	$(TEST_COMPOSE) up -d --wait

test: test-deps ## All tests (starts test containers if needed)
	$(UV) pytest -q

test-down: ## Stop and remove the test containers
	$(TEST_COMPOSE) down -v

check: lint typecheck test ## Everything CI runs

# --- full stack in docker ------------------------------------------------------------

up: env keys ## Build and start the whole stack: http://localhost
	docker compose up -d --build

down: ## Stop the stack (data volumes are kept)
	docker compose down --remove-orphans

logs: ## Follow logs of the stack
	docker compose logs -f --tail=200
