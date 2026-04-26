from collections import defaultdict
from datetime import datetime

from context_db.models import Article, ArticleEntityResolved, KBEntity
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
            KBEntity.qid.label("qid"),
            KBEntity.name.label("name"),
            func.count(func.distinct(ArticleEntityResolved.article_id)).label("count"),
        )
        .join(ArticleEntityResolved, ArticleEntityResolved.qid == KBEntity.qid)
        .join(Article, Article.id == ArticleEntityResolved.article_id)
        .filter(KBEntity.entity_type == entity_type)
        .filter(Article.published_at >= from_date, Article.published_at < to_date)
        .group_by(KBEntity.qid, KBEntity.name)
        .order_by(desc("count"), KBEntity.name)
    )

    if limit:
        rows = rows.limit(limit)

    results = rows.all()

    return [
        EntityCount(type=entity_type, qid=row.qid, name=row.name, count=row.count)
        for row in results
    ]


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

    top_qids = [e.qid for e in top_entities]

    if not top_qids:
        return []

    if interval == Interval.hourly:
        time_bucket = func.date_trunc("hour", Article.published_at)
    else:
        time_bucket = func.date_trunc("day", Article.published_at)

    history_rows = (
        db.query(
            KBEntity.qid.label("qid"),
            time_bucket.label("bucket"),
            func.count(func.distinct(ArticleEntityResolved.article_id)).label("count"),
        )
        .join(ArticleEntityResolved, ArticleEntityResolved.qid == KBEntity.qid)
        .join(Article, Article.id == ArticleEntityResolved.article_id)
        .filter(KBEntity.qid.in_(top_qids))
        .filter(Article.published_at >= from_date, Article.published_at < to_date)
        .group_by(KBEntity.qid, time_bucket)
        .order_by(time_bucket)
        .all()
    )

    history_by_qid = defaultdict(list)
    for row in history_rows:
        history_by_qid[row.qid].append(
            HistoricalEntityCountDataPoint(timestamp=row.bucket, count=row.count)
        )

    return [
        HistoricalEntityCount(
            type=entity.type,
            qid=entity.qid,
            name=entity.name,
            count=entity.count,
            history=history_by_qid.get(entity.qid, []),
        )
        for entity in top_entities
    ]
