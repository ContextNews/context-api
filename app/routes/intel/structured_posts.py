from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.intel import TgStructuredPostListSchema
from app.services.intel.structured_posts_service import list_structured_posts

router = APIRouter(prefix="/structured-posts", tags=["intel"])


@router.get("", response_model=TgStructuredPostListSchema)
def get_structured_posts(
    channel_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    min_priority: int | None = None,
    max_priority: int | None = None,
    has_coordinates: bool | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> TgStructuredPostListSchema:
    return list_structured_posts(
        db,
        channel_id=channel_id,
        from_date=from_date,
        to_date=to_date,
        min_priority=min_priority,
        max_priority=max_priority,
        has_coordinates=has_coordinates,
        limit=limit,
        offset=offset,
    )
