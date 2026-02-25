from datetime import datetime
from typing import Any

from rds_postgres.models import Article, ArticleEntityResolved, KBEntity, KBLocation
from sqlalchemy import desc, func, literal_column
from sqlalchemy.orm import Session


def query_articles(
    db: Session,
    from_date: datetime,
    to_date: datetime,
    limit: int | None = None,
) -> list[Article]:
    query = (
        db.query(Article)
        .filter(Article.published_at >= from_date, Article.published_at < to_date)
        .order_by(desc(Article.published_at))
    )

    if limit:
        query = query.limit(limit)

    return query.all()  # type: ignore[no-any-return]


def query_article_by_id(db: Session, article_id: str) -> Article | None:
    return db.query(Article).filter(Article.id == article_id).first()


def query_article_locations(
    db: Session, article_ids: list[str]
) -> dict[str, list[Any]]:
    """
    Query locations for a list of articles.
    Returns a dict mapping article_id -> list of location data.
    """
    if not article_ids:
        return {}

    rows = (
        db.query(
            ArticleEntityResolved.article_id,
            KBEntity.qid.label("wikidata_qid"),
            KBEntity.name,
            KBLocation.location_type,
            KBLocation.country_code,
            func.ST_Y(literal_column("kb_locations.coordinates::geometry")).label(
                "latitude"
            ),
            func.ST_X(literal_column("kb_locations.coordinates::geometry")).label(
                "longitude"
            ),
        )
        .join(KBEntity, KBEntity.qid == ArticleEntityResolved.qid)
        .join(KBLocation, KBLocation.qid == KBEntity.qid)
        .filter(ArticleEntityResolved.article_id.in_(article_ids))
        .filter(KBEntity.entity_type == "location")
        .all()
    )

    locations_by_article: dict[str, list[Any]] = {}
    for row in rows:
        locations_by_article.setdefault(row.article_id, []).append(
            {
                "wikidata_qid": row.wikidata_qid,
                "name": row.name,
                "location_type": row.location_type,
                "country_code": row.country_code,
                "latitude": float(row.latitude),
                "longitude": float(row.longitude),
            }
        )

    return locations_by_article
