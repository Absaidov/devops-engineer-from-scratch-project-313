from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from ..models import LinkCreate, LinkRead, LinkUpdate
from ..repositories.links import (
    DuplicateShortNameError,
)
from ..repositories.links import (
    create_link as create_link_record,
)
from ..repositories.links import (
    delete_link as delete_link_record,
)
from ..repositories.links import (
    get_link_by_id as get_link_by_id_record,
)
from ..repositories.links import (
    get_link_by_short_name as get_link_by_short_name_record,
)
from ..repositories.links import (
    list_links as list_links_records,
)
from ..repositories.links import (
    update_link as update_link_record,
)
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
    start, end = parse_range_param(range_param)
    if range_param is not None:
        links, total_links = list_links_records(
            session,
            start=start,
            end=end,
        )
        content_range = f"links {start}-{end}/{total_links}"
    else:
        links, total_links = list_links_records(session)
        content_range_end = total_links if total_links > 0 else 0
        content_range = f"links 0-{content_range_end}/{total_links}"

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
    try:
        link = create_link_record(
            session,
            original_url=payload.original_url,
            short_name=payload.short_name,
        )
    except DuplicateShortNameError:
        raise_short_name_conflict()
    return serialize_link(link=link, base_url=request.app.state.base_url)


@router.get("/api/links/{link_id}", response_model=LinkRead)
def get_link_by_id(
    link_id: int,
    request: Request,
    session: Session = Depends(get_session),
) -> LinkRead:
    link = get_link_by_id_record(session, link_id)
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
    link = get_link_by_id_record(session, link_id)
    if link is None:
        raise_link_not_found()

    try:
        updated_link = update_link_record(
            session,
            link=link,
            original_url=payload.original_url,
            short_name=payload.short_name,
        )
    except DuplicateShortNameError:
        raise_short_name_conflict()
    return serialize_link(
        link=updated_link,
        base_url=request.app.state.base_url,
    )


@router.delete(
    "/api/links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_link(
    link_id: int,
    session: Session = Depends(get_session),
) -> Response:
    link = get_link_by_id_record(session, link_id)
    if link is None:
        raise_link_not_found()
    delete_link_record(session, link=link)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/r/{short_name}")
def redirect_to_original_url(
    short_name: str,
    session: Session = Depends(get_session),
) -> RedirectResponse:
    link = get_link_by_short_name_record(session, short_name)
    if link is None:
        raise_link_not_found()
    return RedirectResponse(
        url=link.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
