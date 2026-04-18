from sqlalchemy.orm import Session

from app.queries.intel.channels_queries import query_channel, query_channels
from app.schemas.intel import TgChannelSchema


def list_channels(db: Session) -> list[TgChannelSchema]:
    rows = query_channels(db)
    return [_to_schema(r) for r in rows]


def get_channel(db: Session, channel_id: int) -> TgChannelSchema | None:
    row = query_channel(db, channel_id)
    if not row:
        return None
    return _to_schema(row)


def _to_schema(row: object) -> TgChannelSchema:
    return TgChannelSchema(
        id=row.id,  # type: ignore[attr-defined]
        username=row.username,  # type: ignore[attr-defined]
        channel_id=row.channel_id,  # type: ignore[attr-defined]
        title=row.title,  # type: ignore[attr-defined]
        resolved_at=row.resolved_at,  # type: ignore[attr-defined]
        created_at=row.created_at,  # type: ignore[attr-defined]
    )
