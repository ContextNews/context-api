from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.intel import TgChannelSchema, TgPostListSchema
from app.services.intel.channels_service import get_channel, list_channels
from app.services.intel.posts_service import list_posts

router = APIRouter(prefix="/channels", tags=["intel"])


@router.get("", response_model=list[TgChannelSchema])
def get_channels(db: Session = Depends(get_db)) -> list[TgChannelSchema]:
    return list_channels(db)


@router.get("/{channel_id}", response_model=TgChannelSchema)
def get_channel_by_id(
    channel_id: int,
    db: Session = Depends(get_db),
) -> TgChannelSchema:
    channel = get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel


@router.get("/{channel_id}/posts", response_model=TgPostListSchema)
def get_channel_posts(
    channel_id: int,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> TgPostListSchema:
    return list_posts(
        db,
        channel_id=channel_id,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
