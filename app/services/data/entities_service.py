from sqlalchemy.orm import Session

from app.queries.data.entities_queries import query_entities, query_entity
from app.schemas.data import TSEntitySchema


def list_entities(
    db: Session,
    entity_type: str | None = None,
) -> list[TSEntitySchema]:
    rows = query_entities(db, entity_type=entity_type)
    return [
        TSEntitySchema(id=e.id, name=e.name, entity_type=e.entity_type) for e in rows
    ]


def get_entity(db: Session, entity_id: str) -> TSEntitySchema | None:
    row = query_entity(db, entity_id)
    if not row:
        return None
    return TSEntitySchema(id=row.id, name=row.name, entity_type=row.entity_type)
