FROM python:3.11-slim

WORKDIR /app

# Установка uv
RUN pip install --no-cache-dir uv

# Копируем pyproject.toml и устанавливаем зависимости через uv
COPY pyproject.toml .
RUN uv sync --frozen

COPY . .

RUN uv pip install --system -e .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main.ping:app", "--host", "127.0.0.1", "--port", "8080"]