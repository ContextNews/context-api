from datetime import datetime

from context_db.models import TgPost
from sqlalchemy.orm import Session


def query_posts(
    db: Session,
    channel_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[TgPost]:
    q = db.query(TgPost)
    if channel_id is not None:
        q = q.filter(TgPost.channel_id == channel_id)
    if from_date:
        q = q.filter(TgPost.date >= from_date)
    if to_date:
        q = q.filter(TgPost.date <= to_date)
    return q.order_by(TgPost.date.desc()).offset(offset).limit(limit).all()  # type: ignore[no-any-return]
