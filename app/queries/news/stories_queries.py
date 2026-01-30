from datetime import datetime

from sqlalchemy.orm import Session

from rds_postgres.models import Article, ArticleStory, Story


def query_stories(
    db: Session,
    from_date: datetime,
    to_date: datetime,
    limit: int | None = None,
    parent_only: bool = True,
) -> list[Story]:
    query = db.query(Story).filter(
        Story.story_period >= from_date,
        Story.story_period < to_date,
    )

    if parent_only:
        query = query.filter(Story.parent_story_id.is_(None))

    query = query.order_by(Story.story_period.desc())

    if limit:
        query = query.limit(limit)

    return query.all()


def query_story_by_id(db: Session, story_id: str) -> Story | None:
    return db.query(Story).filter(Story.id == story_id).first()


def query_sub_stories(db: Session, parent_story_ids: list[str]) -> list[Story]:
    if not parent_story_ids:
        return []
    return (
        db.query(Story)
        .filter(Story.parent_story_id.in_(parent_story_ids))
        .all()
    )


def query_story_articles(
    db: Session,
    story_ids: list[str],
) -> list[tuple[str, str, str, str, str]]:
    if not story_ids:
        return []
    return (
        db.query(
            ArticleStory.story_id,
            Article.id,
            Article.title,
            Article.source,
            Article.url,
        )
        .join(Article, Article.id == ArticleStory.article_id)
        .filter(ArticleStory.story_id.in_(story_ids))
        .all()
    )
