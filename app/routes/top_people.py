from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import PersonDailyCountOut
from rds_postgres.models import Article, ArticleEntity


router = APIRouter()


@router.get("/", response_model=list[PersonDailyCountOut])
def list_top_people(db: Session = Depends(get_db)) -> list[PersonDailyCountOut]:
    today = date.today()
    start_day = today - timedelta(days=6)
    start = datetime.combine(start_day, time.min)
    end = datetime.combine(today + timedelta(days=1), time.min)

    rows = (
        db.query(
            func.date(Article.published_at).label("day"),
            ArticleEntity.entity_name.label("person"),
            func.count(func.distinct(ArticleEntity.article_id)).label("article_count"),
        )
        .join(Article, Article.id == ArticleEntity.article_id)
        .filter(func.lower(ArticleEntity.entity_type) == "person")
        .filter(Article.published_at >= start, Article.published_at < end)
        .group_by("day", ArticleEntity.entity_name)
        .order_by(desc("day"), desc("article_count"), ArticleEntity.entity_name)
        .all()
    )

    return [
        PersonDailyCountOut(
            date=row.day,
            person=row.person,
            article_count=row.article_count,
        )
        for row in rows
    ]
