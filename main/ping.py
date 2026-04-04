import os
from contextlib import asynccontextmanager
from typing import Generator

import sentry_sdk
from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    status,
)
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, create_engine, select

from .models import Link, LinkCreate, LinkRead, LinkUpdate

load_dotenv()

SHORT_NAME_CONFLICT = "short_name already exists"
LINK_NOT_FOUND = "Link not found"

# Инициализация Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,  # Для трейсинга запросов (опционально)
    send_default_pii=True,  # Отправлять ли данные пользователей (IP, заголовки)
)

router = APIRouter()


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


def build_short_url(base_url: str, short_name: str) -> str:
    return f"{base_url}/r/{short_name}"


def serialize_link(link: Link, base_url: str) -> LinkRead:
    return LinkRead(
        id=link.id,
        original_url=link.original_url,
        short_name=link.short_name,
        short_url=build_short_url(base_url, link.short_name),
    )


def raise_link_not_found() -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=LINK_NOT_FOUND,
    )


def raise_short_name_conflict() -> None:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=SHORT_NAME_CONFLICT,
    )


def get_session(request: Request) -> Generator[Session, None, None]:
    with Session(request.app.state.engine) as session:
        yield session


@router.get("/ping")
def ping():
    return "pong"


@router.get("/api/links", response_model=list[LinkRead])
def list_links(
    request: Request,
    session: Session = Depends(get_session),
) -> list[LinkRead]:
    links = session.exec(select(Link).order_by(Link.id)).all()
    return [
        serialize_link(link=link, base_url=request.app.state.base_url)
        for link in links
    ]


@router.post(
    "/api/links",
    response_model=LinkRead,
    status_code=status.HTTP_201_CREATED,
)
def create_link(
    payload: LinkCreate,
    request: Request,
    session: Session = Depends(get_session),
) -> LinkRead:
    link = Link(
        original_url=payload.original_url,
        short_name=payload.short_name,
    )
    session.add(link)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise_short_name_conflict()
    session.refresh(link)
    return serialize_link(link=link, base_url=request.app.state.base_url)


@router.get("/api/links/{link_id}", response_model=LinkRead)
def get_link_by_id(
    link_id: int,
    request: Request,
    session: Session = Depends(get_session),
) -> LinkRead:
    link = session.get(Link, link_id)
    if link is None:
        raise_link_not_found()
    return serialize_link(link=link, base_url=request.app.state.base_url)


@router.put("/api/links/{link_id}", response_model=LinkRead)
def update_link(
    link_id: int,
    payload: LinkUpdate,
    request: Request,
    session: Session = Depends(get_session),
) -> LinkRead:
    link = session.get(Link, link_id)
    if link is None:
        raise_link_not_found()

    link.original_url = payload.original_url
    link.short_name = payload.short_name
    session.add(link)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise_short_name_conflict()
    session.refresh(link)
    return serialize_link(link=link, base_url=request.app.state.base_url)


@router.delete(
    "/api/links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_link(
    link_id: int,
    session: Session = Depends(get_session),
) -> Response:
    link = session.get(Link, link_id)
    if link is None:
        raise_link_not_found()
    session.delete(link)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/fail")
def fail():
    raise HTTPException(status_code=400, detail="Something went wrong?")


@router.get("/sentry-debug")
def trigger_error():
    """
    Эндпоинт для тестирования интеграции Sentry.
    Генерирует ZeroDivisionError для проверки отправки ошибок.
    """
    return 1 / 0


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
    application.include_router(router)
    return application


app = create_app()
