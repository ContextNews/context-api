from fastapi import APIRouter

from app.routes.data import datapoints, entities
from app.routes.data.indicators import indicators_router, sources_router

router = APIRouter(prefix="/data", tags=["data"])
router.include_router(entities.router)
router.include_router(sources_router)
router.include_router(indicators_router)
router.include_router(datapoints.router)
