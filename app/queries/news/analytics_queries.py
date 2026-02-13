from collections import defaultdict
from datetime import datetime

from rds_postgres.models import Article, ArticleEntity
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.schemas.enums import FilterRegion, Interval
from app.schemas.news import (
    EntityCount,
    HistoricalEntityCount,
    HistoricalEntityCountDataPoint,
)


def query_top_entities(
    db: Session,
    entity_type: str,
    region: FilterRegion | None,
    from_date: datetime | None,
    to_date: datetime | None,
    limit: int | None,
) -> list[EntityCount]:

    rows = (
        db.query(
            ArticleEntity.entity_name.label("name"),
            func.count(func.distinct(ArticleEntity.article_id)).label("count"),
        )
        .join(Article, Article.id == ArticleEntity.article_id)
        .filter(func.lower(ArticleEntity.entity_type) == entity_type)
        .filter(Article.published_at >= from_date, Article.published_at < to_date)
        .group_by(ArticleEntity.entity_name)
        .order_by(desc("count"), ArticleEntity.entity_name)
    )

    if limit:
        rows = rows.limit(limit)

    results = rows.all()

    entities = [
        EntityCount(type=entity_type, name=row.name, count=row.count) for row in results
    ]

    return entities


def query_top_entities_with_history(
    db: Session,
    entity_type: str,
    region: FilterRegion | None,
    from_date: datetime | None,
    to_date: datetime | None,
    limit: int | None,
    interval: Interval,
) -> list[HistoricalEntityCount]:
    top_entities = query_top_entities(
        db, entity_type, region, from_date, to_date, limit
    )

    entity_names = [e.name for e in top_entities]

    if not entity_names:
        return []

    if interval == Interval.hourly:
        time_bucket = func.date_trunc("hour", Article.published_at)
    else:
        time_bucket = func.date_trunc("day", Article.published_at)

    history_rows = (
        db.query(
            ArticleEntity.entity_name.label("name"),
            time_bucket.label("bucket"),
            func.count(func.distinct(ArticleEntity.article_id)).label("count"),
        )
        .join(Article, Article.id == ArticleEntity.article_id)
        .filter(func.lower(ArticleEntity.entity_type) == entity_type)
        .filter(ArticleEntity.entity_name.in_(entity_names))
        .filter(Article.published_at >= from_date, Article.published_at < to_date)
        .group_by(ArticleEntity.entity_name, time_bucket)
        .order_by(time_bucket)
        .all()
    )

    history_by_entity = defaultdict(list)
    for row in history_rows:
        history_by_entity[row.name].append(
            HistoricalEntityCountDataPoint(timestamp=row.bucket, count=row.count)
        )

    results = []
    for entity in top_entities:
        results.append(
            HistoricalEntityCount(
                type=entity.type,
                name=entity.name,
                count=entity.count,
                history=history_by_entity.get(entity.name, []),
            )
        )

    return results
