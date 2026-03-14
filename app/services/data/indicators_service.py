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
            id=ind.id,
            name=ind.name,
            unit=ind.unit,
            frequency=ind.frequency,
            source=TSSourceSchema(id=src.id, name=src.name, url=src.url),
        )
        for ind, src in rows
    ]


def get_indicator(db: Session, indicator_id: str) -> TSIndicatorSchema | None:
    result = query_indicator(db, indicator_id)
    if not result:
        return None
    ind, src = result
    return TSIndicatorSchema(
        id=ind.id,
        name=ind.name,
        unit=ind.unit,
        frequency=ind.frequency,
        source=TSSourceSchema(id=src.id, name=src.name, url=src.url),
    )
