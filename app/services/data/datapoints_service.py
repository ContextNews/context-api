from datetime import date

from sqlalchemy.orm import Session

from app.queries.data.datapoints_queries import query_datapoints
from app.queries.data.entities_queries import query_entities_by_ids
from app.queries.data.indicators_queries import query_indicators_by_ids
from app.schemas.data import (
    TSDatapointSchema,
    TSEntitySchema,
    TSIndicatorSchema,
    TSSeriesSchema,
    TSSourceSchema,
)
from app.schemas.enums import TSFilterPeriod
from app.services.utils.ts_date_utils import get_ts_date_range


def get_datapoints(
    db: Session,
    indicator_ids: list[str],
    entity_ids: list[str] | None = None,
    period: TSFilterPeriod = TSFilterPeriod.five_years,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[TSSeriesSchema]:
    start, end = get_ts_date_range(period, from_date, to_date)

    rows = query_datapoints(
        db,
        indicator_ids=indicator_ids,
        entity_ids=entity_ids,
        from_date=start,
        to_date=end,
    )
    if not rows:
        return []

    seen_entity_ids = list({r.entity_id for r in rows})
    indicators_by_id = query_indicators_by_ids(db, indicator_ids)
    entities_by_id = query_entities_by_ids(db, seen_entity_ids)

    # Group datapoints by (indicator_id, entity_id)
    series: dict[tuple[str, str], list[TSDatapointSchema]] = {}
    for row in rows:
        key = (row.indicator_id, row.entity_id)
        series.setdefault(key, []).append(
            TSDatapointSchema(date=row.date, value=row.value)
        )

    result: list[TSSeriesSchema] = []
    for (indicator_id, entity_id), datapoints in series.items():
        ind = indicators_by_id.get(indicator_id)
        ent = entities_by_id.get(entity_id)
        if not ind or not ent:
            continue
        result.append(
            TSSeriesSchema(
                indicator=TSIndicatorSchema(
                    id=ind.id,
                    name=ind.name,
                    unit=ind.unit,
                    frequency=ind.frequency,
                    source=TSSourceSchema(
                        id=ind.source.id,
                        name=ind.source.name,
                        url=ind.source.url,
                    ),
                ),
                entity=TSEntitySchema(
                    id=ent.id,
                    name=ent.name,
                    entity_type=ent.entity_type,
                ),
                datapoints=datapoints,
            )
        )

    return result
