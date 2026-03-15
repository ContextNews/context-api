from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.data import TSSeriesSchema
from app.services.data.story_datapoints_service import get_story_datapoints

router = APIRouter()


@router.get("/stories/{story_id}/datapoints", response_model=list[TSSeriesSchema])
def get_story_datapoints_endpoint(
    story_id: str,
    db: Session = Depends(get_db),
) -> list[TSSeriesSchema]:
    return get_story_datapoints(db=db, story_id=story_id)
