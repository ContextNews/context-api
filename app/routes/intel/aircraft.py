import httpx
from fastapi import APIRouter, HTTPException

from app.schemas.intel import MilitaryAircraftSchema
from app.services.intel.aircraft_service import fetch_military_aircraft

router = APIRouter(prefix="/military-aircraft", tags=["intel"])


@router.get("", response_model=list[MilitaryAircraftSchema])
async def get_military_aircraft() -> list[MilitaryAircraftSchema]:
    try:
        return await fetch_military_aircraft()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"ADS-B Exchange error: {e.response.status_code}",
        ) from e
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502, detail="Failed to reach ADS-B Exchange"
        ) from e
