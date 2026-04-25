from datetime import datetime

from sqlalchemy.orm import Session

from app.queries.intel.structured_posts_queries import query_structured_posts
from app.schemas.intel import TgStructuredPostListSchema, TgStructuredPostSchema


def list_structured_posts(
    db: Session,
    channel_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    min_priority: int | None = None,
    max_priority: int | None = None,
    has_coordinates: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> TgStructuredPostListSchema:
    rows = query_structured_posts(
        db,
        channel_id=channel_id,
        from_date=from_date,
        to_date=to_date,
        min_priority=min_priority,
        max_priority=max_priority,
        has_coordinates=has_coordinates,
        limit=limit + 1,
        offset=offset,
    )
    has_more = len(rows) > limit
    items = [_to_schema(sp, post) for sp, post in rows[:limit]]
    return TgStructuredPostListSchema(items=items, has_more=has_more)


def _to_schema(sp: object, post: object) -> TgStructuredPostSchema:
    return TgStructuredPostSchema(
        post_id=sp.post_id,  # type: ignore[attr-defined]
        channel_id=post.channel_id,  # type: ignore[attr-defined]
        message_id=post.message_id,  # type: ignore[attr-defined]
        text=post.text,  # type: ignore[attr-defined]
        date=post.date,  # type: ignore[attr-defined]
        label=sp.label,  # type: ignore[attr-defined]
        priority=sp.priority,  # type: ignore[attr-defined]
        latitude=sp.latitude,  # type: ignore[attr-defined]
        longitude=sp.longitude,  # type: ignore[attr-defined]
        location_name=sp.location_name,  # type: ignore[attr-defined]
        story_id=sp.story_id,  # type: ignore[attr-defined]
    )
