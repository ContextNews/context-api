from fastapi import APIRouter

from . import top_stories

router = APIRouter(prefix="/landing", tags=["landing"])
router.include_router(top_stories.router)
