from fastapi import APIRouter

from app.schemas.news import NewsSource
from app.services.news.news_sources_service import get_news_sources

router = APIRouter(prefix="/sources")

@router.get("/")
def list_sources() -> list[NewsSource]:
    return get_news_sources()