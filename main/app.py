import os
from contextlib import asynccontextmanager

import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sqlmodel import SQLModel, create_engine

from .routers import debug_router, links_router, ping_router

load_dotenv()

DEFAULT_CORS_ORIGIN = "http://localhost:5173"

# Инициализация Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,  # Для трейсинга запросов (опционально)
    send_default_pii=True,  # Отправлять ли данные пользователей (IP, заголовки)
)


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def get_database_url(explicit_database_url: str | None = None) -> str:
    raw_database_url = explicit_database_url or os.getenv(
        "DATABASE_URL",
        "sqlite:///./app.db",
    )
    return normalize_database_url(raw_database_url)


def get_base_url(explicit_base_url: str | None = None) -> str:
    if explicit_base_url:
        return explicit_base_url.rstrip("/")
    env_base_url = os.getenv("BASE_URL")
    if env_base_url:
        return env_base_url.rstrip("/")
    port = os.getenv("PORT", "8080")
    return f"http://127.0.0.1:{port}"


def get_cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS")
    if raw_origins:
        parsed_origins = [
            item.strip().rstrip("/")
            for item in raw_origins.split(",")
            if item.strip()
        ]
        if parsed_origins:
            return parsed_origins
    return [DEFAULT_CORS_ORIGIN]


def create_app(
    *,
    database_url: str | None = None,
    base_url: str | None = None,
) -> FastAPI:
    resolved_database_url = get_database_url(database_url)
    resolved_base_url = get_base_url(base_url)
    connect_args = (
        {"check_same_thread": False}
        if resolved_database_url.startswith("sqlite")
        else {}
    )
    engine = create_engine(resolved_database_url, connect_args=connect_args)

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        application.state.engine = engine
        application.state.base_url = resolved_base_url
        SQLModel.metadata.create_all(engine)
        yield

    application = FastAPI(lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    application.include_router(ping_router)
    application.include_router(links_router)
    application.include_router(debug_router)
    return application


app = create_app()
