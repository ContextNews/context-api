from datetime import date, datetime, time, timedelta
from functools import lru_cache

from fastapi import APIRouter, Depends
import pycountry
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import LocationDailyCountOut
from rds_postgres.models import Article, ArticleEntity


router = APIRouter()


@lru_cache(maxsize=1024)
def resolve_iso3(location: str) -> str | None:
    if not location:
        return None
    try:
        country = pycountry.countries.lookup(location.strip())
    except LookupError:
        return None
    return getattr(country, "alpha_3", None)


@router.get("/", response_model=list[LocationDailyCountOut])
def list_top_locations(db: Session = Depends(get_db)) -> list[LocationDailyCountOut]:
    today = date.today()
    start_day = today - timedelta(days=6)
    start = datetime.combine(start_day, time.min)
    end = datetime.combine(today + timedelta(days=1), time.min)

    rows = (
        db.query(
            func.date(Article.published_at).label("day"),
            ArticleEntity.entity_name.label("location"),
            func.count(func.distinct(ArticleEntity.article_id)).label("article_count"),
        )
        .join(Article, Article.id == ArticleEntity.article_id)
        .filter(func.lower(ArticleEntity.entity_type) == "gpe")
        .filter(Article.published_at >= start, Article.published_at < end)
        .group_by("day", ArticleEntity.entity_name)
        .order_by(desc("day"), desc("article_count"), ArticleEntity.entity_name)
        .all()
    )

    return [
        LocationDailyCountOut(
            date=row.day,
            location=row.location,
            article_count=row.article_count,
            iso3=resolve_iso3(row.location),
        )
        for row in rows
    ]
