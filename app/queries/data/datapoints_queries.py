from datetime import date

from context_db.models import TSDatapoint
from sqlalchemy.orm import Session


def query_datapoints(
    db: Session,
    indicator_ids: list[str],
    entity_ids: list[str] | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[TSDatapoint]:
    if not indicator_ids:
        return []

    q = db.query(TSDatapoint).filter(TSDatapoint.indicator_id.in_(indicator_ids))

    if entity_ids:
        q = q.filter(TSDatapoint.entity_id.in_(entity_ids))
    if from_date:
        q = q.filter(TSDatapoint.date >= from_date)
    if to_date:
        q = q.filter(TSDatapoint.date <= to_date)

    return q.order_by(  # type: ignore[no-any-return]
        TSDatapoint.indicator_id,
        TSDatapoint.entity_id,
        TSDatapoint.date,
    ).all()
