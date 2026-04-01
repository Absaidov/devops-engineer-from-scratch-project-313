import os
from fastapi import FastAPI, HTTPException
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Инициализация Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,  # Для трейсинга запросов (опционально)
    send_default_pii=True,  # Отправлять ли данные пользователей (IP, заголовки)
)

app = FastAPI()


@app.get("/ping")
def ping():
    return "pong"


@app.get("/fail")
def fail():
    raise HTTPException(status_code=400, detail="Something went wrong?")