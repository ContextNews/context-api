from datetime import date

from sqlalchemy.orm import Session

from app.queries.news.articles_queries import (
    query_article_by_id,
    query_article_locations,
    query_articles,
)
from app.schemas.enums import FilterPeriod, FilterRegion
from app.schemas.news import ArticleLocationSchema, NewsArticle
from app.services.utils.date_utils import get_date_range


def list_articles(
    db: Session,
    period: FilterPeriod,
    region: FilterRegion | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int | None = None,
) -> list[NewsArticle]:
    start, end = get_date_range(period, from_date, to_date)

    articles_db = query_articles(db, start, end, limit=limit)

    article_ids = [article.id for article in articles_db]
    locations_by_article = query_article_locations(db, article_ids)

    return [
        NewsArticle(
            id=article.id,
            source=article.source,
            title=article.title,
            summary=article.summary,
            url=article.url,
            published_at=article.published_at,
            ingested_at=article.ingested_at,
            locations=[
                ArticleLocationSchema(**loc)
                for loc in locations_by_article.get(article.id, [])
            ],
        )
        for article in articles_db
    ]


def get_article(db: Session, article_id: str) -> NewsArticle | None:
    article = query_article_by_id(db, article_id)
    if not article:
        return None

    locations_by_article = query_article_locations(db, [article_id])

    return NewsArticle(
        id=article.id,
        source=article.source,
        title=article.title,
        summary=article.summary,
        url=article.url,
        published_at=article.published_at,
        ingested_at=article.ingested_at,
        locations=[
            ArticleLocationSchema(**loc)
            for loc in locations_by_article.get(article_id, [])
        ],
    )
