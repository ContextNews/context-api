from datetime import date
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.news import EntityCount
from app.services.news.analytics_service import (
    get_top_locations,
    get_top_people,
    get_top_organizations,
    FilterPeriod,
    FilterRegion,
)

router = APIRouter(prefix="/analytics")

@router.get("/top-locations")
def top_locations(
    db: Session = Depends(get_db),
    period: FilterPeriod = FilterPeriod.today,
    region: FilterRegion | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int | None = Query(None, ge=1, le=100)
) -> list[EntityCount]:
    return get_top_locations(
        db=db,
        period=period,
        region=region,
        from_date=from_date,
        to_date=to_date,
        limit=limit
    )

@router.get("/top-people")
def top_locations(
    db: Session = Depends(get_db),
    period: FilterPeriod = FilterPeriod.today,
    region: FilterRegion | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int | None = Query(None, ge=1, le=100)
) -> list[EntityCount]:
    return get_top_people(
        db=db,
        period=period,
        region=region,
        from_date=from_date,
        to_date=to_date,
        limit=limit
    )

@router.get("/top-organizations")
def top_locations(
    db: Session = Depends(get_db),
    period: FilterPeriod = FilterPeriod.today,
    region: FilterRegion | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int | None = Query(None, ge=1, le=100)
) -> list[EntityCount]:
    return get_top_organizations(
        db=db,
        period=period,
        region=region,
        from_date=from_date,
        to_date=to_date,
        limit=limit
    )