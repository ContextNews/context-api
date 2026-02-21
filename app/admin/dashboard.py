from datetime import UTC, datetime, timedelta

from rds_postgres.models import (
    Article,
    ArticleEmbedding,
    ArticleEntity,
    ArticleLocation,
    ArticlePerson,
    ArticleStory,
    ArticleTopic,
    Story,
    StoryLocation,
)
from sqladmin import BaseView, expose
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.db import engine


class DashboardView(BaseView):
    name = "Dashboard"
    icon = "fa-solid fa-chart-line"

    @expose("/admin/db/dashboard", methods=["GET"])
    async def dashboard(self, request: Request):  # type: ignore[no-untyped-def]
        with Session(engine) as db:
            data = _collect_all_metrics(db)

        return await self.templates.TemplateResponse(
            "admin/dashboard.html",  # type: ignore[arg-type]
            {"request": request, **data},  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def _collect_all_metrics(db: Session) -> dict:  # type: ignore[type-arg]
    apd_labels, apd_values = _articles_per_day(db)
    aps_labels, aps_values = _articles_per_source(db)
    topic_labels, topic_values = _topic_distribution(db)
    gpe = _entity_resolution(db, entity_type="gpe")
    person = _entity_resolution(db, entity_type="person")
    clustering = _clustering_health(db)
    location = _location_health(db)
    embedding = _embedding_coverage(db)

    return {
        "articles_per_day_labels": apd_labels,
        "articles_per_day_values": apd_values,
        "articles_per_source_labels": aps_labels,
        "articles_per_source_values": aps_values,
        "topic_labels": topic_labels,
        "topic_values": topic_values,
        "gpe_resolution_pct": gpe["resolution_pct"],
        "unresolved_gpe": gpe["unresolved"],
        "person_resolution_pct": person["resolution_pct"],
        "unresolved_person": person["unresolved"],
        **clustering,
        **location,
        **embedding,
    }


# ---------------------------------------------------------------------------
# A. Ingestion Health
# ---------------------------------------------------------------------------


def _articles_per_day(db: Session) -> tuple[list[str], list[int]]:
    thirty_days_ago = datetime.now(tz=UTC) - timedelta(days=30)
    rows = (
        db.query(
            func.date_trunc("day", Article.published_at).label("day"),
            func.count(Article.id).label("count"),
        )
        .filter(Article.published_at >= thirty_days_ago)
        .group_by("day")
        .order_by("day")
        .all()
    )
    labels = [r.day.strftime("%b %d") for r in rows]
    values = [r.count for r in rows]
    return labels, values


def _articles_per_source(db: Session) -> tuple[list[str], list[int]]:
    rows = (
        db.query(Article.source, func.count(Article.id).label("count"))
        .group_by(Article.source)
        .order_by(desc("count"))
        .all()
    )
    return [r.source for r in rows], [r.count for r in rows]


# ---------------------------------------------------------------------------
# B. Topic Distribution
# ---------------------------------------------------------------------------


def _topic_distribution(db: Session, limit: int = 25) -> tuple[list[str], list[int]]:
    rows = (
        db.query(
            ArticleTopic.topic,
            func.count(ArticleTopic.article_id).label("count"),
        )
        .group_by(ArticleTopic.topic)
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )
    return [r.topic for r in rows], [r.count for r in rows]


# ---------------------------------------------------------------------------
# C. Entity Resolution
# ---------------------------------------------------------------------------


def _entity_resolution(db: Session, entity_type: str) -> dict:  # type: ignore[type-arg]
    """
    Compute resolution rate for GPE or PERSON entities.

    For GPE:   resolved via ArticleLocation (article_id + name match)
    For PERSON: resolved via ArticlePerson  (article_id + name match)
    """
    resolved_model = ArticleLocation if entity_type == "gpe" else ArticlePerson
    resolved_fk = resolved_model.article_id
    resolved_name = resolved_model.name

    total: int = (
        db.query(func.count())
        .select_from(ArticleEntity)
        .filter(func.lower(ArticleEntity.entity_type) == entity_type)
        .scalar()
    ) or 0

    resolved: int = (
        db.query(func.count())
        .select_from(ArticleEntity)
        .join(
            resolved_model,
            and_(
                resolved_fk == ArticleEntity.article_id,
                resolved_name == ArticleEntity.entity_name,
            ),
        )
        .filter(func.lower(ArticleEntity.entity_type) == entity_type)
        .scalar()
    ) or 0

    resolution_pct = round(resolved / total * 100, 1) if total else 0.0

    unresolved_rows = (
        db.query(
            ArticleEntity.entity_name.label("name"),
            func.count().label("count"),
        )
        .outerjoin(
            resolved_model,
            and_(
                resolved_fk == ArticleEntity.article_id,
                resolved_name == ArticleEntity.entity_name,
            ),
        )
        .filter(func.lower(ArticleEntity.entity_type) == entity_type)
        .filter(resolved_fk.is_(None))
        .group_by(ArticleEntity.entity_name)
        .order_by(desc("count"))
        .limit(20)
        .all()
    )

    return {
        "resolution_pct": resolution_pct,
        "unresolved": [{"name": r.name, "count": r.count} for r in unresolved_rows],
    }


# ---------------------------------------------------------------------------
# D. Clustering Health
# ---------------------------------------------------------------------------


def _clustering_health(db: Session) -> dict:  # type: ignore[type-arg]
    total_articles: int = db.query(func.count(Article.id)).scalar() or 0
    assigned: int = (
        db.query(func.count(func.distinct(ArticleStory.article_id))).scalar() or 0
    )
    unclustered_pct = (
        round((total_articles - assigned) / total_articles * 100, 1)
        if total_articles
        else 0.0
    )

    size_rows = (
        db.query(
            ArticleStory.story_id,
            func.count(ArticleStory.article_id).label("size"),
        )
        .group_by(ArticleStory.story_id)
        .all()
    )

    buckets: dict[str, int] = {
        "1": 0,
        "2": 0,
        "3-5": 0,
        "6-10": 0,
        "11-20": 0,
        "21+": 0,
    }
    for row in size_rows:
        s = row.size
        if s == 1:
            buckets["1"] += 1
        elif s == 2:
            buckets["2"] += 1
        elif s <= 5:
            buckets["3-5"] += 1
        elif s <= 10:
            buckets["6-10"] += 1
        elif s <= 20:
            buckets["11-20"] += 1
        else:
            buckets["21+"] += 1

    return {
        "unclustered_pct": unclustered_pct,
        "cluster_size_bucket_labels": list(buckets.keys()),
        "cluster_size_bucket_values": list(buckets.values()),
    }


# ---------------------------------------------------------------------------
# E. Location Health
# ---------------------------------------------------------------------------


def _location_health(db: Session) -> dict:  # type: ignore[type-arg]
    stories_no_location: int = (
        db.query(func.count(Story.id))
        .outerjoin(StoryLocation, StoryLocation.story_id == Story.id)
        .filter(StoryLocation.story_id.is_(None))
        .scalar()
    ) or 0

    subq = (
        db.query(
            StoryLocation.story_id,
            func.count(StoryLocation.wikidata_qid).label("loc_count"),
        )
        .group_by(StoryLocation.story_id)
        .subquery()
    )
    avg_locations_per_story = (
        db.query(func.round(func.avg(subq.c.loc_count), 1)).scalar() or 0
    )

    return {
        "stories_no_location": stories_no_location,
        "avg_locations_per_story": avg_locations_per_story,
    }


# ---------------------------------------------------------------------------
# F. Embedding Coverage
# ---------------------------------------------------------------------------


def _embedding_coverage(db: Session) -> dict:  # type: ignore[type-arg]
    total_articles: int = db.query(func.count(Article.id)).scalar() or 0
    total_embedded: int = (
        db.query(func.count(func.distinct(ArticleEmbedding.article_id))).scalar() or 0
    )
    coverage_pct = (
        round(total_embedded / total_articles * 100, 1) if total_articles else 0.0
    )

    model_rows = (
        db.query(
            ArticleEmbedding.embedding_model,
            func.count(ArticleEmbedding.article_id).label("count"),
        )
        .group_by(ArticleEmbedding.embedding_model)
        .order_by(desc("count"))
        .all()
    )

    return {
        "embedding_coverage_pct": coverage_pct,
        "embedding_model_labels": [r.embedding_model for r in model_rows],
        "embedding_model_values": [r.count for r in model_rows],
    }
