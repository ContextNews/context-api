from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import ArticleOut
from rds_postgres.models import Article


router = APIRouter()


@router.get("/", response_model=list[ArticleOut])
def list_articles(db: Session = Depends(get_db)) -> list[Article]:
    return db.query(Article).all()


@router.get("/{article_id}", response_model=ArticleOut)
def get_article(article_id: str, db: Session = Depends(get_db)) -> Article:
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
