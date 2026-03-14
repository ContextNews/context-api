from context_db.models import TSEntity
from sqlalchemy.orm import Session


def query_entities(
    db: Session,
    entity_type: str | None = None,
) -> list[TSEntity]:
    q = db.query(TSEntity)
    if entity_type:
        q = q.filter(TSEntity.entity_type == entity_type)
    return q.order_by(TSEntity.name).all()  # type: ignore[no-any-return]


def query_entity(db: Session, entity_id: str) -> TSEntity | None:
    return db.query(TSEntity).filter(TSEntity.id == entity_id).first()


def query_entities_by_ids(db: Session, entity_ids: list[str]) -> dict[str, TSEntity]:
    if not entity_ids:
        return {}
    rows = db.query(TSEntity).filter(TSEntity.id.in_(entity_ids)).all()
    return {e.id: e for e in rows}
