from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.data import TSEntitySchema
from app.services.data.entities_service import get_entity, list_entities

router = APIRouter(prefix="/entities", tags=["data"])


@router.get("", response_model=list[TSEntitySchema])
def get_entities(
    entity_type: str | None = None,
    db: Session = Depends(get_db),
) -> list[TSEntitySchema]:
    return list_entities(db, entity_type=entity_type)


@router.get("/{entity_id}", response_model=TSEntitySchema)
def get_entity_by_id(
    entity_id: str,
    db: Session = Depends(get_db),
) -> TSEntitySchema:
    entity = get_entity(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity
