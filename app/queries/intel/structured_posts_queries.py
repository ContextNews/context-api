from datetime import datetime

from context_db.models import TgPost, TgStructuredPost
from sqlalchemy.orm import Session


def query_structured_posts(
    db: Session,
    channel_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    min_priority: int | None = None,
    max_priority: int | None = None,
    has_coordinates: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[tuple[TgStructuredPost, TgPost]]:
    q = db.query(TgStructuredPost, TgPost).join(
        TgPost, TgStructuredPost.post_id == TgPost.id
    )
    if channel_id is not None:
        q = q.filter(TgPost.channel_id == channel_id)
    if from_date:
        q = q.filter(TgPost.date >= from_date)
    if to_date:
        q = q.filter(TgPost.date <= to_date)
    if min_priority is not None:
        q = q.filter(TgStructuredPost.priority <= min_priority)
    if max_priority is not None:
        q = q.filter(TgStructuredPost.priority >= max_priority)
    if has_coordinates is True:
        q = q.filter(TgStructuredPost.latitude.isnot(None))
    elif has_coordinates is False:
        q = q.filter(TgStructuredPost.latitude.is_(None))
    return q.order_by(TgPost.date.desc()).offset(offset).limit(limit).all()  # type: ignore[no-any-return]
