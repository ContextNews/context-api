from context_db.models import TSIndicator, TSSource
from sqlalchemy.orm import Session


def query_sources(db: Session) -> list[TSSource]:
    return db.query(TSSource).order_by(TSSource.name).all()  # type: ignore[no-any-return]


def query_indicators(
    db: Session,
    source_id: int | None = None,
    frequency: str | None = None,
) -> list[tuple[TSIndicator, TSSource]]:
    q = db.query(TSIndicator, TSSource).join(
        TSSource, TSSource.id == TSIndicator.source_id
    )
    if source_id is not None:
        q = q.filter(TSIndicator.source_id == source_id)
    if frequency:
        q = q.filter(TSIndicator.frequency == frequency)
    return q.order_by(TSIndicator.name).all()  # type: ignore[no-any-return]


def query_indicator(
    db: Session, indicator_id: str
) -> tuple[TSIndicator, TSSource] | None:
    return (  # type: ignore[no-any-return]
        db.query(TSIndicator, TSSource)
        .join(TSSource, TSSource.id == TSIndicator.source_id)
        .filter(TSIndicator.id == indicator_id)
        .first()
    )


def query_indicators_by_ids(
    db: Session, indicator_ids: list[str]
) -> dict[str, tuple[TSIndicator, TSSource]]:
    if not indicator_ids:
        return {}
    rows = (
        db.query(TSIndicator, TSSource)
        .join(TSSource, TSSource.id == TSIndicator.source_id)
        .filter(TSIndicator.id.in_(indicator_ids))
        .all()
    )
    return {ind.id: (ind, src) for ind, src in rows}
