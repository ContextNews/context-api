from fastapi import APIRouter

from app.routes.intel import aircraft, channels, entities, posts, structured_posts

router = APIRouter(prefix="/intel", tags=["intel"])
router.include_router(channels.router)
router.include_router(posts.router)
router.include_router(structured_posts.router)
router.include_router(entities.router)
router.include_router(aircraft.router)
