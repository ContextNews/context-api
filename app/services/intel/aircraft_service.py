import os
from typing import Any

import httpx

from app.schemas.intel import MilitaryAircraftSchema

ADSB_MIL_URL = "https://adsbexchange-com1.p.rapidapi.com/v2/mil/"
RAPIDAPI_HOST = "adsbexchange-com1.p.rapidapi.com"


def _parse_aircraft(ac: dict[str, Any]) -> MilitaryAircraftSchema | None:
    lat = ac.get("lat")
    lon = ac.get("lon")
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return None

    alt_baro = ac.get("alt_baro")
    on_ground = alt_baro == "ground"
    altitude_ft = int(alt_baro) if isinstance(alt_baro, (int, float)) else None

    gs = ac.get("gs")
    speed_kts = int(gs) if isinstance(gs, (int, float)) else None

    track = ac.get("track")
    heading_deg = int(track) if isinstance(track, (int, float)) else None

    callsign = str(ac.get("flight", "")).strip() or None
    aircraft_type = str(ac.get("t", "")).strip() or None
    registration = str(ac.get("r", "")).strip() or None

    return MilitaryAircraftSchema(
        hex=str(ac.get("hex", "")),
        callsign=callsign,
        lat=float(lat),
        lon=float(lon),
        altitude_ft=altitude_ft,
        on_ground=on_ground,
        speed_kts=speed_kts,
        heading_deg=heading_deg,
        aircraft_type=aircraft_type,
        registration=registration,
    )


async def fetch_military_aircraft() -> list[MilitaryAircraftSchema]:
    api_key = os.environ.get("RAPIDAPI_KEY", "")
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            ADSB_MIL_URL,
            headers={
                "x-rapidapi-key": api_key,
                "x-rapidapi-host": RAPIDAPI_HOST,
            },
        )
        response.raise_for_status()
        data = response.json()

    return [
        parsed
        for ac in data.get("ac", [])
        if (parsed := _parse_aircraft(ac)) is not None
    ]
