from datetime import UTC, date, datetime, timedelta

from context_db.models import (
    Article,
    ArticleStory,
    KBEntity,
    KBLocation,
    KBPerson,
    Story,
    StoryEntity,
    StoryTopic,
)
from sqlalchemy import alias, and_, case, desc, func
from sqlalchemy.orm import Session

REGISTRY_TYPES = ("person", "organization")
ENTITY_PAGE_SIZE = 50


def query_entities(
    db: Session,
    entity_type: str | None = None,
    limit: int = ENTITY_PAGE_SIZE,
    offset: int = 0,
) -> list[tuple]:
    now = datetime.now(tz=UTC)
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = now - timedelta(days=7)

    # Subquery: story mention counts per entity across three windows
    mention_counts = (
        db.query(
            StoryEntity.qid.label("qid"),
            func.count(
                func.distinct(case((Story.story_period >= start_of_today, Story.id)))
            ).label("today_count"),
            func.count(
                func.distinct(case((Story.story_period >= start_of_week, Story.id)))
            ).label("week_count"),
            func.count(func.distinct(Story.id)).label("alltime_count"),
        )
        .outerjoin(
            Story,
            and_(Story.id == StoryEntity.story_id, Story.parent_story_id.is_(None)),
        )
        .group_by(StoryEntity.qid)
        .subquery()
    )

    q = (
        db.query(KBEntity, KBPerson.nationalities)
        .outerjoin(KBPerson, KBEntity.qid == KBPerson.qid)
        .outerjoin(mention_counts, mention_counts.c.qid == KBEntity.qid)
    )

    if entity_type:
        q = q.filter(KBEntity.entity_type == entity_type)
    else:
        q = q.filter(KBEntity.entity_type.in_(REGISTRY_TYPES))

    q = q.order_by(
        desc(func.coalesce(mention_counts.c.today_count, 0)),
        desc(func.coalesce(mention_counts.c.week_count, 0)),
        desc(func.coalesce(mention_counts.c.alltime_count, 0)),
        KBEntity.name,
    )

    return q.limit(limit).offset(offset).all()  # type: ignore[no-any-return]


def query_entity(db: Session, qid: str) -> tuple | None:
    return (
        db.query(KBEntity, KBPerson.nationalities)
        .outerjoin(KBPerson, KBEntity.qid == KBPerson.qid)
        .filter(KBEntity.qid == qid)
        .first()
    )


def query_entity_heatmap(db: Session, qid: str, days: int = 365) -> dict[date, int]:
    cutoff = datetime.now(tz=UTC) - timedelta(days=days)
    rows = (
        db.query(
            func.date_trunc("day", Story.story_period).label("day"),
            func.count(func.distinct(Story.id)).label("count"),
        )
        .join(StoryEntity, StoryEntity.story_id == Story.id)
        .filter(StoryEntity.qid == qid)
        .filter(Story.parent_story_id.is_(None))
        .filter(Story.story_period >= cutoff)
        .group_by(func.date_trunc("day", Story.story_period))
        .all()
    )
    return {row.day.date(): row.count for row in rows}


def query_entity_coverage_stats(db: Session, qid: str) -> dict:
    now = datetime.now(tz=UTC)
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_month = start_of_today.replace(day=1)
    start_of_year = start_of_today.replace(month=1, day=1)

    def _story_count_since(since: datetime) -> int:
        return (
            db.query(func.count(func.distinct(Story.id)))
            .join(StoryEntity, StoryEntity.story_id == Story.id)
            .filter(StoryEntity.qid == qid)
            .filter(Story.parent_story_id.is_(None))
            .filter(Story.story_period >= since)
            .scalar()
        ) or 0

    period_counts = {
        "today": _story_count_since(start_of_today),
        "this_month": _story_count_since(start_of_month),
        "this_year": _story_count_since(start_of_year),
    }

    # Top locations: locations co-occurring in the entity's stories
    loc_se = alias(StoryEntity)
    location_rows = (
        db.query(
            KBEntity.name.label("name"),
            KBLocation.country_code.label("country_code"),
            func.count(func.distinct(Story.id)).label("story_count"),
        )
        .join(StoryEntity, StoryEntity.story_id == Story.id)
        .filter(StoryEntity.qid == qid)
        .filter(Story.parent_story_id.is_(None))
        .join(loc_se, loc_se.c.story_id == Story.id)
        .join(KBEntity, KBEntity.qid == loc_se.c.qid)
        .join(KBLocation, KBLocation.qid == KBEntity.qid)
        .filter(KBEntity.entity_type == "location")
        .group_by(KBEntity.name, KBLocation.country_code)
        .order_by(desc("story_count"))
        .limit(5)
        .all()
    )

    # Topic breakdown
    topic_rows = (
        db.query(
            StoryTopic.topic.label("topic"),
            func.count(func.distinct(Story.id)).label("story_count"),
        )
        .join(StoryEntity, StoryEntity.story_id == Story.id)
        .filter(StoryEntity.qid == qid)
        .filter(Story.parent_story_id.is_(None))
        .join(StoryTopic, StoryTopic.story_id == Story.id)
        .group_by(StoryTopic.topic)
        .order_by(desc("story_count"))
        .limit(5)
        .all()
    )

    # Source breakdown
    source_rows = (
        db.query(
            Article.source.label("source"),
            func.count(func.distinct(Article.id)).label("article_count"),
        )
        .join(ArticleStory, ArticleStory.article_id == Article.id)
        .join(Story, Story.id == ArticleStory.story_id)
        .join(StoryEntity, StoryEntity.story_id == Story.id)
        .filter(StoryEntity.qid == qid)
        .filter(Story.parent_story_id.is_(None))
        .group_by(Article.source)
        .order_by(desc("article_count"))
        .limit(5)
        .all()
    )

    return {
        "period_counts": period_counts,
        "location_rows": location_rows,
        "topic_rows": topic_rows,
        "source_rows": source_rows,
    }
