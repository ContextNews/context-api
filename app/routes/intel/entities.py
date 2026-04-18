from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.intel import KBEntitySchema
from app.services.intel.entities_service import get_entity, list_entities

router = APIRouter(prefix="/entities", tags=["intel"])


@router.get("", response_model=list[KBEntitySchema])
def get_entities(
    entity_type: str | None = None,
    db: Session = Depends(get_db),
) -> list[KBEntitySchema]:
    return list_entities(db, entity_type=entity_type)


@router.get("/{qid}", response_model=KBEntitySchema)
def get_entity_by_qid(
    qid: str,
    db: Session = Depends(get_db),
) -> KBEntitySchema:
    entity = get_entity(db, qid)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity
