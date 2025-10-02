.PHONY: up up-build down logs migrate test deploy

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

deploy: down up-build migrate
	@echo "Деплой выполнен успешно!"
