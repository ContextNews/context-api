from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.intel import KBEntitySchema
from app.schemas.news import StoryCard
from app.services.intel.entities_service import get_entity, list_entities
from app.services.news.stories_service import get_stories_by_entity

router = APIRouter(prefix="/entities", tags=["intel"])


@router.get("", response_model=list[KBEntitySchema])
def get_entities(
    entity_type: str | None = None,
    db: Session = Depends(get_db),
) -> list[KBEntitySchema]:
    return list_entities(db, entity_type=entity_type)


@router.get("/{qid}/stories", response_model=list[StoryCard])
async def get_entity_stories(
    qid: str,
    db: Session = Depends(get_db),
) -> list[StoryCard]:
    return await get_stories_by_entity(db, qid)


@router.get("/{qid}", response_model=KBEntitySchema)
def get_entity_by_qid(
    qid: str,
    db: Session = Depends(get_db),
) -> KBEntitySchema:
    entity = get_entity(db, qid)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity
