#!/usr/bin/env bash
set -euo pipefail

# Внешний порт контейнера занимает nginx (Render PORT=80)
# FastAPI запускаем на внутреннем порту
BACKEND_PORT=3000

uv run uvicorn main:app \
  --host 127.0.0.1 \
  --port "${BACKEND_PORT}" \
  --proxy-headers &
BACKEND_PID=$!

nginx -g 'daemon off;' &
NGINX_PID=$!

cleanup() {
  kill -TERM "$BACKEND_PID" "$NGINX_PID" 2>/dev/null || true
}

trap cleanup SIGINT SIGTERM

wait -n "$BACKEND_PID" "$NGINX_PID"
STATUS=$?

cleanup
wait || true

exit "$STATUS"