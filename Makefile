run:
	uv run uvicorn main:app --reload --port 8080

start:
	uv run uvicorn main:app --host 127.0.0.1 --port 8080

lint:
	uv run ruff check main

test:
	uv run pytest