.PHONY: up up-build down logs migrate migration db-connect test deploy \
		celery-worker celery-beat celery-flower celery-logs health check-health

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
