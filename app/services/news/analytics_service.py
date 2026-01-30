from datetime import date

from sqlalchemy.orm import Session

from app.schemas.news import EntityCount, HistoricalEntityCount
from app.queries.news.analytics_queries import query_top_entities, query_top_entities_with_history
from app.schemas.enums import FilterPeriod, FilterRegion, Interval
from app.services.utils.date_utils import get_date_range


def get_top_locations(
    db: Session,
    period: FilterPeriod,
    region: FilterRegion | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int | None = None,
    interval: Interval | None = None,
) -> list[EntityCount] | list[HistoricalEntityCount]:
    from_date, to_date = get_date_range(period, from_date, to_date)

    if interval:
        return query_top_entities_with_history(
            db=db,
            entity_type="gpe",
            region=region,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            interval=interval,
        )

    return query_top_entities(
        db=db,
        entity_type="gpe",
        region=region,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )


def get_top_people(
    db: Session,
    period: FilterPeriod,
    region: FilterRegion | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int | None = None,
    interval: Interval | None = None,
) -> list[EntityCount] | list[HistoricalEntityCount]:
    from_date, to_date = get_date_range(period, from_date, to_date)

    if interval:
        return query_top_entities_with_history(
            db=db,
            entity_type="person",
            region=region,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            interval=interval,
        )

    return query_top_entities(
        db=db,
        entity_type="person",
        region=region,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )


def get_top_organizations(
    db: Session,
    period: FilterPeriod,
    region: FilterRegion | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int | None = None,
    interval: Interval | None = None,
) -> list[EntityCount] | list[HistoricalEntityCount]:
    from_date, to_date = get_date_range(period, from_date, to_date)

    if interval:
        return query_top_entities_with_history(
            db=db,
            entity_type="org",
            region=region,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            interval=interval,
        )

    return query_top_entities(
        db=db,
        entity_type="org",
        region=region,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )
