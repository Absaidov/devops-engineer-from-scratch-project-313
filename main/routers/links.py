from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..models import Link, LinkCreate, LinkRead, LinkUpdate
from .common import (
    get_session,
    parse_range_param,
    raise_link_not_found,
    raise_short_name_conflict,
    serialize_link,
)

router = APIRouter()


@router.get("/api/links", response_model=list[LinkRead])
def list_links(
    response: Response,
    request: Request,
    range_param: str | None = Query(default=None, alias="range"),
    session: Session = Depends(get_session),
) -> list[LinkRead]:
    total_links = session.exec(select(func.count()).select_from(Link)).one()
    start, end = parse_range_param(range_param)
    links_query = select(Link).order_by(Link.id)

    if range_param is not None:
        links_query = links_query.offset(start).limit(end - start)
        content_range = f"links {start}-{end}/{total_links}"
    else:
        content_range_end = total_links if total_links > 0 else 0
        content_range = f"links 0-{content_range_end}/{total_links}"

    links = session.exec(links_query).all()
    response.headers["Accept-Ranges"] = "links"
    response.headers["Content-Range"] = content_range
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
