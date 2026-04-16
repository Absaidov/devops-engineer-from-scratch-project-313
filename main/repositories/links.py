from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..models import Link


class DuplicateShortNameError(Exception):
    pass


def list_links(
    session: Session,
    *,
    start: int | None = None,
    end: int | None = None,
) -> tuple[list[Link], int]:
    total_links = session.exec(select(func.count()).select_from(Link)).one()
    query = select(Link).order_by(Link.id)
    if start is not None and end is not None:
        query = query.offset(start).limit(end - start)
    links = session.exec(query).all()
    return links, total_links


def create_link(
    session: Session,
    *,
    original_url: str,
    short_name: str,
) -> Link:
    link = Link(
        original_url=original_url,
        short_name=short_name,
    )
    session.add(link)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DuplicateShortNameError from error
    session.refresh(link)
    return link


def get_link_by_id(session: Session, link_id: int) -> Link | None:
    return session.get(Link, link_id)


def get_link_by_short_name(session: Session, short_name: str) -> Link | None:
    return session.exec(
        select(Link).where(Link.short_name == short_name),
    ).first()


def update_link(
    session: Session,
    *,
    link: Link,
    original_url: str,
    short_name: str,
) -> Link:
    link.original_url = original_url
    link.short_name = short_name
    session.add(link)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DuplicateShortNameError from error
    session.refresh(link)
    return link


def delete_link(session: Session, *, link: Link) -> None:
    session.delete(link)
    session.commit()
