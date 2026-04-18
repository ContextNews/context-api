from datetime import datetime

from sqlalchemy.orm import Session

from app.queries.intel.posts_queries import query_posts
from app.schemas.intel import TgPostListSchema, TgPostSchema


def list_posts(
    db: Session,
    channel_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> TgPostListSchema:
    rows = query_posts(
        db,
        channel_id=channel_id,
        from_date=from_date,
        to_date=to_date,
        limit=limit + 1,
        offset=offset,
    )
    has_more = len(rows) > limit
    items = [_to_schema(r) for r in rows[:limit]]
    return TgPostListSchema(items=items, has_more=has_more)


def _to_schema(row: object) -> TgPostSchema:
    return TgPostSchema(
        id=row.id,  # type: ignore[attr-defined]
        channel_id=row.channel_id,  # type: ignore[attr-defined]
        message_id=row.message_id,  # type: ignore[attr-defined]
        text=row.text,  # type: ignore[attr-defined]
        date=row.date,  # type: ignore[attr-defined]
        edit_date=row.edit_date,  # type: ignore[attr-defined]
        has_media=row.has_media,  # type: ignore[attr-defined]
        media_type=row.media_type,  # type: ignore[attr-defined]
        collected_at=row.collected_at,  # type: ignore[attr-defined]
    )
