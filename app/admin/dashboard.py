from datetime import UTC, datetime, timedelta

from rds_postgres.models import (
    Article,
    ArticleEmbedding,
    ArticleEntityMention,
    ArticleEntityResolved,
    ArticleStory,
    ArticleTopic,
    KBEntity,
    KBEntityAlias,
    Story,
    StoryEntity,
)
from sqladmin import BaseView, expose
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.db import engine


class DashboardView(BaseView):
    name = "Dashboard"
    icon = "fa-solid fa-chart-line"

    @expose("/dashboard", methods=["GET"])
    async def dashboard(self, request: Request):  # type: ignore[no-untyped-def]
        with Session(engine) as db:
            data = _collect_all_metrics(db)

        return await self.templates.TemplateResponse(
            request,
            "admin/dashboard.html",
            context=data,
        )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def _collect_all_metrics(db: Session) -> dict:  # type: ignore[type-arg]
    apd_labels, apd_values = _articles_per_day(db)
    aps_labels, aps_values = _articles_per_source(db)
    topic_labels, topic_values = _topic_distribution(db)
    gpe = _entity_resolution(db, entity_type="GPE")
    person = _entity_resolution(db, entity_type="PERSON")
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
    Compute resolution rate for GPE or PERSON entities, and list mention texts
    that have no matching alias in the knowledge base (i.e. entities genuinely
    missing from the KB, not just articles where the pipeline didn't run).

    entity_type: uppercase NER type — 'GPE' or 'PERSON'.
    kb_entity_type: matching KBEntity.entity_type — 'location' or 'person'.
    """
    kb_entity_type = "location" if entity_type == "GPE" else "person"

    # Articles that have at least one NER mention of this type
    total: int = (
        db.query(func.count(func.distinct(ArticleEntityMention.article_id)))
        .filter(ArticleEntityMention.ner_type == entity_type)
        .scalar()
    ) or 0

    # Articles that have at least one resolved KB entity of the matching type
    resolved: int = (
        db.query(func.count(func.distinct(ArticleEntityResolved.article_id)))
        .join(KBEntity, KBEntity.qid == ArticleEntityResolved.qid)
        .filter(KBEntity.entity_type == kb_entity_type)
        .scalar()
    ) or 0

    resolution_pct = round(resolved / total * 100, 1) if total else 0.0

    # Top mention texts with no matching alias in the KB for this entity type.
    # Uses UPPER() on both sides for case-insensitive comparison.
    # alias is a primary key (NOT NULL) so NOT IN is safe from the NULL gotcha.
    kb_aliases_upper = (
        db.query(func.upper(KBEntityAlias.alias))
        .join(KBEntity, KBEntity.qid == KBEntityAlias.qid)
        .filter(KBEntity.entity_type == kb_entity_type)
    )

    unresolved_rows = (
        db.query(
            ArticleEntityMention.mention_text.label("name"),
            func.count(func.distinct(ArticleEntityMention.article_id)).label("count"),
        )
        .filter(ArticleEntityMention.ner_type == entity_type)
        .filter(func.upper(ArticleEntityMention.mention_text).not_in(kb_aliases_upper))
        .group_by(ArticleEntityMention.mention_text)
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
    stories_with_location = (
        db.query(StoryEntity.story_id)
        .join(KBEntity, KBEntity.qid == StoryEntity.qid)
        .filter(KBEntity.entity_type == "location")
        .distinct()
        .subquery()
    )

    stories_no_location: int = (
        db.query(func.count(Story.id))
        .outerjoin(
            stories_with_location,
            stories_with_location.c.story_id == Story.id,
        )
        .filter(stories_with_location.c.story_id.is_(None))
        .scalar()
    ) or 0

    loc_count_subq = (
        db.query(
            StoryEntity.story_id,
            func.count(StoryEntity.qid).label("loc_count"),
        )
        .join(KBEntity, KBEntity.qid == StoryEntity.qid)
        .filter(KBEntity.entity_type == "location")
        .group_by(StoryEntity.story_id)
        .subquery()
    )
    avg_locations_per_story = (
        db.query(func.round(func.avg(loc_count_subq.c.loc_count), 1)).scalar() or 0
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
