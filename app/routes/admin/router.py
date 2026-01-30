from fastapi import APIRouter
from . import status

router = APIRouter(prefix="/admin", tags=["admin"])
router.include_router(status.router)
