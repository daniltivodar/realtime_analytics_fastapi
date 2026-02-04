.PHONY: up up-build down logs migrate migration db-connect test deploy \
		celery-worker celery-beat celery-flower celery-logs health check-health \
		dev deps lint format check clean pre-commit-install pre-commit ci-local

up:
	docker compose up -d

up-build:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f api

migrate:
	docker compose run --rm api alembic upgrade head

migration:
	docker compose run --rm api alembic revision --autogenerate --rev-id "$(rev-id)" -m "$(name)"

db-connect:
	docker compose exec postgres psql -U user -d analytics

test:
	docker compose run --rm api pytest

check-health:
	curl -f http://localhost:8000/health

health: check-health
	@echo "API is healthy"

celery-worker:
	docker compose up -d celery-worker

celery-beat:
	docker compose up -d celery-beat

celery-reload:
	docker compose restart celery-worker celery-beat

celery-flower:
	docker compose --profile monitoring up -d celery-flower

celery-logs:
	docker compose logs -f celery-worker celery-beat

deploy: down up-build migrate
	@echo "Deploy complete!"

deps:
	poetry install --with dev

lint:
	poetry run black --check app tests
	poetry run ruff check app tests
	poetry run mypy app

format:
	poetry run black app tests
	poetry run ruff check --fix app

check: lint
	poetry run pytest --cov=app --cov-report=term

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".ruff_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true

pre-commit-install:
	poetry run pre-commit uninstall || true
	poetry run pre-commit install
	poetry run pre-commit install --hook-type pre-commit

pre-commit:
	poetry run pre-commit run --all-files

ci-local:
	act -P ubuntu-latest=catthehacker/ubuntu:act-latest -W .github/workflows/ci-local.yml
