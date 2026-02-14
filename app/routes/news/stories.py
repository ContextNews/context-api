from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.enums import FilterPeriod, FilterRegion, FilterTopic
from app.schemas.news import (
    NewsStory,
    NewsStoryWithRelated,
    PaginatedStoryCards,
)
from app.services.news.stories_service import (
    get_story as get_story_service,
)
from app.services.news.stories_service import (
    get_story_feed as get_story_feed_service,
)
from app.services.news.stories_service import (
    list_stories as list_stories_service,
)

router = APIRouter(prefix="/stories")


@router.get("", response_model=list[NewsStory])
async def list_stories(
    db: Session = Depends(get_db),
    period: FilterPeriod = FilterPeriod.today,
    region: FilterRegion | None = None,
    topic: FilterTopic | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int | None = Query(None, ge=1, le=100),
) -> list[NewsStory]:
    return await list_stories_service(
        db=db,
        period=period,
        region=region,
        topic=topic,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )


@router.get("/news-feed", response_model=PaginatedStoryCards)
async def get_story_feed(
    db: Session = Depends(get_db),
    period: FilterPeriod = FilterPeriod.today,
    region: FilterRegion | None = None,
    topic: FilterTopic | None = None,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginatedStoryCards:
    return await get_story_feed_service(
        db=db,
        period=period,
        region=region,
        topic=topic,
        limit=limit,
        offset=offset,
    )


@router.get("/{story_id}", response_model=NewsStoryWithRelated)
async def get_story(
    story_id: str,
    db: Session = Depends(get_db),
) -> NewsStoryWithRelated:
    story = await get_story_service(db=db, story_id=story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story
