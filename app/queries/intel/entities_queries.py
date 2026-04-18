from context_db.models import KBEntity, KBPerson
from sqlalchemy.orm import Session

REGISTRY_TYPES = ("person", "organization")


def query_entities(
    db: Session,
    entity_type: str | None = None,
) -> list[tuple]:
    q = db.query(KBEntity, KBPerson.nationalities).outerjoin(
        KBPerson, KBEntity.qid == KBPerson.qid
    )
    if entity_type:
        q = q.filter(KBEntity.entity_type == entity_type)
    else:
        q = q.filter(KBEntity.entity_type.in_(REGISTRY_TYPES))
    return q.order_by(KBEntity.name).all()  # type: ignore[no-any-return]


def query_entity(db: Session, qid: str) -> tuple | None:
    return (
        db.query(KBEntity, KBPerson.nationalities)
        .outerjoin(KBPerson, KBEntity.qid == KBPerson.qid)
        .filter(KBEntity.qid == qid)
        .first()
    )
