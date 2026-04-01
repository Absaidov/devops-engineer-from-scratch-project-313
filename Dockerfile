FROM python:3.12-slim

WORKDIR /app

# Установка uv
RUN pip install --no-cache-dir uv

# Копируем pyproject.toml и uv.lock
COPY pyproject.toml uv.lock ./

# Создаём виртуальное окружение и устанавливаем зависимости
RUN uv sync --frozen

COPY . .

RUN uv pip install --system -e .

EXPOSE $PORT

CMD ["uv", "run", "uvicorn", "main.ping:app", "--host", "0.0.0.0", "--port", "${PORT}"]