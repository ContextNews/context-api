from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.data import TSSeriesSchema
from app.schemas.enums import TSFilterPeriod
from app.services.data.datapoints_service import get_datapoints

router = APIRouter(prefix="/datapoints", tags=["data"])


@router.get("", response_model=list[TSSeriesSchema])
def get_datapoints_endpoint(
    indicator_id: list[str] = Query(..., min_length=1),
    entity_id: list[str] | None = Query(default=None),
    period: TSFilterPeriod = TSFilterPeriod.five_years,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
) -> list[TSSeriesSchema]:
    return get_datapoints(
        db,
        indicator_ids=indicator_id,
        entity_ids=entity_id,
        period=period,
        from_date=from_date,
        to_date=to_date,
    )
