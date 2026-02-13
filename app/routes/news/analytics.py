from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.enums import FilterPeriod, FilterRegion, Interval
from app.schemas.news import EntityCount, HistoricalEntityCount
from app.services.news.analytics_service import (
    get_top_locations,
    get_top_organizations,
    get_top_people,
)

router = APIRouter(prefix="/analytics")


@router.get("/top-locations")
def top_locations(
    db: Session = Depends(get_db),
    period: FilterPeriod = FilterPeriod.today,
    region: FilterRegion | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int | None = Query(None, ge=1, le=100),
    interval: Interval | None = None,
) -> list[EntityCount] | list[HistoricalEntityCount]:
    return get_top_locations(
        db=db,
        period=period,
        region=region,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        interval=interval,
    )


@router.get("/top-people")
def top_people(
    db: Session = Depends(get_db),
    period: FilterPeriod = FilterPeriod.today,
    region: FilterRegion | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int | None = Query(None, ge=1, le=100),
    interval: Interval | None = None,
) -> list[EntityCount] | list[HistoricalEntityCount]:
    return get_top_people(
        db=db,
        period=period,
        region=region,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        interval=interval,
    )


@router.get("/top-organizations")
def top_organizations(
    db: Session = Depends(get_db),
    period: FilterPeriod = FilterPeriod.today,
    region: FilterRegion | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int | None = Query(None, ge=1, le=100),
    interval: Interval | None = None,
) -> list[EntityCount] | list[HistoricalEntityCount]:
    return get_top_organizations(
        db=db,
        period=period,
        region=region,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        interval=interval,
    )
