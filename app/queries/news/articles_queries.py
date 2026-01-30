from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.orm import Session

from rds_postgres.models import Article


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
