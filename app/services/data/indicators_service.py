from sqlalchemy.orm import Session

from app.queries.data.indicators_queries import (
    query_indicator,
    query_indicators,
    query_sources,
)
from app.schemas.data import TSIndicatorSchema, TSSourceSchema


def list_sources(db: Session) -> list[TSSourceSchema]:
    rows = query_sources(db)
    return [TSSourceSchema(id=s.id, name=s.name, url=s.url) for s in rows]


def list_indicators(
    db: Session,
    source_id: int | None = None,
    frequency: str | None = None,
) -> list[TSIndicatorSchema]:
    rows = query_indicators(db, source_id=source_id, frequency=frequency)
    return [
        TSIndicatorSchema(
            id=i.id,
            name=i.name,
            unit=i.unit,
            frequency=i.frequency,
            source=TSSourceSchema(id=i.source.id, name=i.source.name, url=i.source.url),
        )
        for i in rows
    ]


def get_indicator(db: Session, indicator_id: str) -> TSIndicatorSchema | None:
    row = query_indicator(db, indicator_id)
    if not row:
        return None
    return TSIndicatorSchema(
        id=row.id,
        name=row.name,
        unit=row.unit,
        frequency=row.frequency,
        source=TSSourceSchema(
            id=row.source.id, name=row.source.name, url=row.source.url
        ),
    )
