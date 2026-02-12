from fastapi import APIRouter

from app.routes.admin.router import router as admin_router
from app.routes.landing.router import router as landing_router
from app.routes.news.router import router as news_router

router = APIRouter()
router.include_router(admin_router)
router.include_router(landing_router)
router.include_router(news_router)
