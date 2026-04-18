from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.intel import TgPostListSchema
from app.services.intel.posts_service import list_posts

router = APIRouter(prefix="/posts", tags=["intel"])


@router.get("", response_model=TgPostListSchema)
def get_posts(
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> TgPostListSchema:
    return list_posts(
        db,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
