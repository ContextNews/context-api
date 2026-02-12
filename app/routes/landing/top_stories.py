from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.enums import FilterPeriod
from app.schemas.landing import RegionTopStories
from app.services.landing.top_stories_service import (
    get_top_stories_by_region as get_top_stories_by_region_service,
)

router = APIRouter(prefix="/top-stories")


@router.get("", response_model=list[RegionTopStories])
async def top_stories(
    db: Session = Depends(get_db),
    period: FilterPeriod = FilterPeriod.today,
) -> list[RegionTopStories]:
    return await get_top_stories_by_region_service(db=db, period=period)
