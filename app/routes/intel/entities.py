from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.intel import (
    EntityCoverageStatsResponse,
    EntityHeatmapResponse,
    KBEntitySchema,
)
from app.schemas.news import PaginatedStoryCards
from app.services.intel.entities_service import (
    get_entity,
    get_entity_coverage_stats,
    get_entity_heatmap,
    list_entities,
)
from app.services.news.stories_service import get_stories_by_entity

router = APIRouter(prefix="/entities", tags=["intel"])


@router.get("", response_model=list[KBEntitySchema])
def get_entities(
    entity_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[KBEntitySchema]:
    return list_entities(db, entity_type=entity_type, limit=limit, offset=offset)


@router.get("/{qid}/stories", response_model=PaginatedStoryCards)
async def get_entity_stories(
    qid: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> PaginatedStoryCards:
    return await get_stories_by_entity(db, qid, limit=limit, offset=offset)


@router.get("/{qid}/heatmap", response_model=EntityHeatmapResponse)
def get_entity_heatmap_endpoint(
    qid: str,
    days: int = 365,
    db: Session = Depends(get_db),
) -> EntityHeatmapResponse:
    return get_entity_heatmap(db, qid, days)


@router.get("/{qid}/coverage-stats", response_model=EntityCoverageStatsResponse)
def get_entity_coverage_stats_endpoint(
    qid: str,
    db: Session = Depends(get_db),
) -> EntityCoverageStatsResponse:
    return get_entity_coverage_stats(db, qid)


@router.get("/{qid}", response_model=KBEntitySchema)
def get_entity_by_qid(
    qid: str,
    db: Session = Depends(get_db),
) -> KBEntitySchema:
    entity = get_entity(db, qid)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity
