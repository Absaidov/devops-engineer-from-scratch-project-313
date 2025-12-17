run:
	uv run uvicorn main:app --reload --port 8080

lint:
	uv run ruff check main

test:
	uv run pytest