from sqlalchemy.orm import Session

from app.queries.intel.entities_queries import query_entities, query_entity
from app.schemas.intel import KBEntitySchema


def list_entities(
    db: Session,
    entity_type: str | None = None,
) -> list[KBEntitySchema]:
    rows = query_entities(db, entity_type=entity_type)
    return [_to_schema(entity, nationalities) for entity, nationalities in rows]


def get_entity(db: Session, qid: str) -> KBEntitySchema | None:
    row = query_entity(db, qid)
    if not row:
        return None
    entity, nationalities = row
    return _to_schema(entity, nationalities)


def _to_schema(entity: object, nationalities: list[str] | None) -> KBEntitySchema:
    return KBEntitySchema(
        qid=entity.qid,  # type: ignore[attr-defined]
        entity_type=entity.entity_type,  # type: ignore[attr-defined]
        name=entity.name,  # type: ignore[attr-defined]
        description=entity.description,  # type: ignore[attr-defined]
        image_url=entity.image_url,  # type: ignore[attr-defined]
        nationalities=nationalities,
    )
