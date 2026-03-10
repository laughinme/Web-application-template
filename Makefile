.PHONY: backend-install backend-test-keys backend-lint backend-test-unit backend-test-integration test-up test-down

BACKEND_DIR := backend
TEST_COMPOSE_FILE := docker-compose.test.yml
TEST_COMPOSE_PROJECT := monolith-template-test

backend-install:
	cd $(BACKEND_DIR) && poetry install --with dev --no-root

backend-test-keys:
	@mkdir -p $(BACKEND_DIR)/secrets
	@if [ ! -f "$(BACKEND_DIR)/secrets/jwt_private_key.pem" ]; then \
		openssl genrsa -out "$(BACKEND_DIR)/secrets/jwt_private_key.pem" 2048; \
	fi
	@if [ ! -f "$(BACKEND_DIR)/secrets/jwt_public_key.pem" ]; then \
		openssl rsa -in "$(BACKEND_DIR)/secrets/jwt_private_key.pem" -pubout -out "$(BACKEND_DIR)/secrets/jwt_public_key.pem"; \
	fi

backend-lint:
	cd $(BACKEND_DIR) && poetry run ruff check src tests --select E9,F63,F7

backend-test-unit: backend-test-keys
	cd $(BACKEND_DIR) && poetry run pytest -m unit -q

test-up:
	docker compose -p $(TEST_COMPOSE_PROJECT) -f $(TEST_COMPOSE_FILE) up -d

test-down:
	docker compose -p $(TEST_COMPOSE_PROJECT) -f $(TEST_COMPOSE_FILE) down -v

backend-test-integration: backend-test-keys
	@bash -lc 'set -euo pipefail; \
	COMPOSE_FILE="$$(pwd)/$(TEST_COMPOSE_FILE)"; \
	PROJECT_NAME="$(TEST_COMPOSE_PROJECT)"; \
	docker compose -p "$$PROJECT_NAME" -f "$$COMPOSE_FILE" down -v >/dev/null 2>&1 || true; \
	docker compose -p "$$PROJECT_NAME" -f "$$COMPOSE_FILE" up -d; \
	trap "docker compose -p \"$$PROJECT_NAME\" -f \"$$COMPOSE_FILE\" down -v" EXIT; \
	cd $(BACKEND_DIR); \
	poetry run pytest -m integration -q'
