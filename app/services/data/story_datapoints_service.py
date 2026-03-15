from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.queries.data.stories_queries import (
    query_indicator_ids_for_story,
    query_story_exists,
)
from app.schemas.data import TSSeriesSchema
from app.schemas.enums import TSFilterPeriod
from app.services.data.datapoints_service import get_datapoints

DEFAULT_ENTITY_IDS = ["CHN", "USA", "GBR", "RUS", "FRA"]
DEFAULT_PERIOD = TSFilterPeriod.ten_years


def get_story_datapoints(db: Session, story_id: str) -> list[TSSeriesSchema]:
    if not query_story_exists(db, story_id):
        raise HTTPException(status_code=404, detail="Story not found")

    indicator_ids = query_indicator_ids_for_story(db, story_id)
    if not indicator_ids:
        return []

    return get_datapoints(
        db=db,
        indicator_ids=indicator_ids,
        entity_ids=DEFAULT_ENTITY_IDS,
        period=DEFAULT_PERIOD,
        from_date=None,
        to_date=None,
    )
