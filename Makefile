FRAMEWORK ?= fastapi
BACKEND_PORT ?= 8080
API_URL ?= http://127.0.0.1:$(BACKEND_PORT)

run:
	uv run uvicorn main:app --host 0.0.0.0 --port $(BACKEND_PORT)

start:
	uv run uvicorn main:app --host 127.0.0.1 --port $(BACKEND_PORT)

frontend:
	FRAMEWORK=$(FRAMEWORK) API_URL=$(API_URL) npx start-hexlet-devops-deploy-crud-frontend

dev:
	npx concurrently -k -n backend,frontend -c blue,green \
		"make run BACKEND_PORT=$(BACKEND_PORT)" \
		"make frontend FRAMEWORK=$(FRAMEWORK) API_URL=$(API_URL)"

lint:
	uv run ruff check main

lint-fix:
	uv run ruff check main --fix

test:
	uv run pytest
