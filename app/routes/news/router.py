from fastapi import APIRouter
from . import stories, articles, analytics, sources

router = APIRouter(prefix="/news", tags=["news"])
router.include_router(stories.router)
router.include_router(articles.router)
router.include_router(analytics.router)
router.include_router(sources.router)