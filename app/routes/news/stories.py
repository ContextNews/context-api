from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.enums import FilterPeriod, FilterRegion
from app.schemas.news import NewsStory, StoryCard
from app.services.news.stories_service import (
    list_stories as list_stories_service,
    get_story as get_story_service,
    get_story_feed as get_story_feed_service,
)

router = APIRouter(prefix="/stories")


@router.get("", response_model=list[NewsStory])
async def list_stories(
    db: Session = Depends(get_db),
    period: FilterPeriod = FilterPeriod.today,
    region: FilterRegion | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int | None = Query(None, ge=1, le=100),
) -> list[NewsStory]:
    return await list_stories_service(
        db=db,
        period=period,
        region=region,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )


@router.get("/news-feed", response_model=list[StoryCard])
async def get_story_feed(
    db: Session = Depends(get_db),
    period: FilterPeriod = FilterPeriod.today,
    region: FilterRegion | None = None,
    limit: int | None = Query(None, ge=1, le=100),
) -> list[StoryCard]:
    return await get_story_feed_service(
        db=db,
        period=period,
        region=region,
        limit=limit,
    )


@router.get("/{story_id}", response_model=NewsStory)
async def get_story(
    story_id: str,
    db: Session = Depends(get_db),
) -> NewsStory:
    story = await get_story_service(db=db, story_id=story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story
