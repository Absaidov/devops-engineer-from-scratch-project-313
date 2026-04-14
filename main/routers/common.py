import json
from typing import Generator

from fastapi import HTTPException, Request, status
from sqlmodel import Session

from ..models import Link, LinkRead

SHORT_NAME_CONFLICT = "short_name already exists"
LINK_NOT_FOUND = "Link not found"
INVALID_RANGE = "Invalid range parameter"


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


def parse_range_param(range_param: str | None) -> tuple[int, int]:
    if range_param is None:
        return 0, 0

    try:
        parsed = json.loads(range_param)
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_RANGE,
        ) from error

    if not isinstance(parsed, list) or len(parsed) != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_RANGE,
        )

    start, end = parsed
    if not isinstance(start, int) or isinstance(start, bool):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_RANGE,
        )
    if not isinstance(end, int) or isinstance(end, bool):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_RANGE,
        )
    if start < 0 or end < start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_RANGE,
        )

    return start, end
