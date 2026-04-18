from fastapi import APIRouter

from app.routes.intel import channels, posts

router = APIRouter(prefix="/intel", tags=["intel"])
router.include_router(channels.router)
router.include_router(posts.router)
