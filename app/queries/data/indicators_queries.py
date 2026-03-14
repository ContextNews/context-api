from context_db.models import TSIndicator, TSSource
from sqlalchemy.orm import Session, joinedload


def query_sources(db: Session) -> list[TSSource]:
    return db.query(TSSource).order_by(TSSource.name).all()  # type: ignore[no-any-return]


def query_indicators(
    db: Session,
    source_id: int | None = None,
    frequency: str | None = None,
) -> list[TSIndicator]:
    q = db.query(TSIndicator).options(joinedload(TSIndicator.source))
    if source_id is not None:
        q = q.filter(TSIndicator.source_id == source_id)
    if frequency:
        q = q.filter(TSIndicator.frequency == frequency)
    return q.order_by(TSIndicator.name).all()  # type: ignore[no-any-return]


def query_indicator(db: Session, indicator_id: str) -> TSIndicator | None:
    return (
        db.query(TSIndicator)
        .options(joinedload(TSIndicator.source))
        .filter(TSIndicator.id == indicator_id)
        .first()
    )


def query_indicators_by_ids(
    db: Session, indicator_ids: list[str]
) -> dict[str, TSIndicator]:
    if not indicator_ids:
        return {}
    rows = (
        db.query(TSIndicator)
        .options(joinedload(TSIndicator.source))
        .filter(TSIndicator.id.in_(indicator_ids))
        .all()
    )
    return {i.id: i for i in rows}
