from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.data import TSIndicatorSchema, TSSourceSchema
from app.services.data.indicators_service import (
    get_indicator,
    list_indicators,
    list_sources,
)

router = APIRouter(tags=["data"])

sources_router = APIRouter(prefix="/sources")
indicators_router = APIRouter(prefix="/indicators")


@sources_router.get("", response_model=list[TSSourceSchema])
def get_sources(db: Session = Depends(get_db)) -> list[TSSourceSchema]:
    return list_sources(db)


@indicators_router.get("", response_model=list[TSIndicatorSchema])
def get_indicators(
    source_id: int | None = None,
    frequency: str | None = None,
    db: Session = Depends(get_db),
) -> list[TSIndicatorSchema]:
    return list_indicators(db, source_id=source_id, frequency=frequency)


@indicators_router.get("/{indicator_id}", response_model=TSIndicatorSchema)
def get_indicator_by_id(
    indicator_id: str,
    db: Session = Depends(get_db),
) -> TSIndicatorSchema:
    indicator = get_indicator(db, indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return indicator
