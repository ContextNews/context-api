from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.queries.intel.entities_queries import (
    query_entities,
    query_entity,
    query_entity_coverage_stats,
    query_entity_heatmap,
)
from app.schemas.intel import (
    EntityCoverageStatsResponse,
    EntityHeatmapResponse,
    EntityLocationStat,
    EntityMentionDay,
    EntityPeriodCounts,
    EntitySourceStat,
    EntityTopicStat,
    KBEntitySchema,
)


def list_entities(
    db: Session,
    entity_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[KBEntitySchema]:
    rows = query_entities(db, entity_type=entity_type, limit=limit, offset=offset)
    return [_to_schema(entity, nationalities) for entity, nationalities in rows]


def get_entity(db: Session, qid: str) -> KBEntitySchema | None:
    row = query_entity(db, qid)
    if not row:
        return None
    entity, nationalities = row
    return _to_schema(entity, nationalities)


def get_entity_heatmap(db: Session, qid: str, days: int = 365) -> EntityHeatmapResponse:
    counts = query_entity_heatmap(db, qid, days)
    today = date.today()
    result = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        result.append(EntityMentionDay(date=d, count=counts.get(d, 0)))
    return EntityHeatmapResponse(data=result)


def get_entity_coverage_stats(db: Session, qid: str) -> EntityCoverageStatsResponse:
    raw = query_entity_coverage_stats(db, qid)
    return EntityCoverageStatsResponse(
        period_counts=EntityPeriodCounts(**raw["period_counts"]),
        top_locations=[
            EntityLocationStat(
                name=row.name,
                country_code=row.country_code,
                story_count=row.story_count,
            )
            for row in raw["location_rows"]
        ],
        topics=[
            EntityTopicStat(topic=row.topic, story_count=row.story_count)
            for row in raw["topic_rows"]
        ],
        sources=[
            EntitySourceStat(source=row.source, article_count=row.article_count)
            for row in raw["source_rows"]
        ],
    )


def _to_schema(entity: object, nationalities: list[str] | None) -> KBEntitySchema:
    return KBEntitySchema(
        qid=entity.qid,  # type: ignore[attr-defined]
        entity_type=entity.entity_type,  # type: ignore[attr-defined]
        name=entity.name,  # type: ignore[attr-defined]
        description=entity.description,  # type: ignore[attr-defined]
        image_url=entity.image_url,  # type: ignore[attr-defined]
        nationalities=nationalities,
    )
