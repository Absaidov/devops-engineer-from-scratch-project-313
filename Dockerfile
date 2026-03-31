FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir uv && uv pip install -e .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main.ping:app", "--host", "127.0.0.1", "--port", "8080"]