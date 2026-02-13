from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.enums import FilterPeriod, FilterRegion
from app.schemas.news import NewsArticle
from app.services.news.articles_service import (
    get_article as get_article_service,
)
from app.services.news.articles_service import (
    list_articles as list_articles_service,
)

router = APIRouter(prefix="/articles")


@router.get("", response_model=list[NewsArticle])
def list_articles(
    db: Session = Depends(get_db),
    period: FilterPeriod = FilterPeriod.today,
    region: FilterRegion | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int | None = Query(None, ge=1, le=100),
) -> list[NewsArticle]:
    return list_articles_service(
        db=db,
        period=period,
        region=region,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )


@router.get("/{article_id}", response_model=NewsArticle)
def get_article(
    article_id: str,
    db: Session = Depends(get_db),
) -> NewsArticle:
    article = get_article_service(db=db, article_id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
