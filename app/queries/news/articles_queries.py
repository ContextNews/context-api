from datetime import datetime

from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_X, ST_Y
from sqlalchemy import cast, desc
from sqlalchemy.orm import Session

from rds_postgres.models import Article, ArticleLocation, Location


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

    return query.all()


def query_article_by_id(db: Session, article_id: str) -> Article | None:
    return db.query(Article).filter(Article.id == article_id).first()


def query_article_locations(db: Session, article_ids: list[str]) -> dict[str, list]:
    """
    Query locations for a list of articles.
    Returns a dict mapping article_id -> list of location data.
    """
    if not article_ids:
        return {}

    rows = (
        db.query(
            ArticleLocation.article_id,
            Location.wikidata_qid,
            Location.name,
            Location.location_type,
            Location.country_code,
            ST_Y(cast(Location.coordinates, Geometry)).label("latitude"),
            ST_X(cast(Location.coordinates, Geometry)).label("longitude"),
        )
        .join(Location, Location.wikidata_qid == ArticleLocation.wikidata_qid)
        .filter(ArticleLocation.article_id.in_(article_ids))
        .all()
    )

    locations_by_article: dict[str, list] = {}
    for row in rows:
        locations_by_article.setdefault(row.article_id, []).append({
            "wikidata_qid": row.wikidata_qid,
            "name": row.name,
            "location_type": row.location_type,
            "country_code": row.country_code,
            "latitude": row.latitude,
            "longitude": row.longitude,
        })

    return locations_by_article
