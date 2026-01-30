from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.schemas.news import EntityCount
from rds_postgres.models import Article, ArticleEntity
from app.schemas.enums import FilterRegion


def query_top_entities(
    db: Session,
    entity_type: str,
    region: FilterRegion | None, # Currently unused
    from_date: date | None,
    to_date: date | None,
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
        EntityCount(type=entity_type, name=row.name, count=row.count)
        for row in results
    ]

    return entities