from fastapi import APIRouter

router = APIRouter(prefix="/status")


@router.api_route("", methods=["GET", "HEAD"])
def status_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/badge")
def status_badge() -> dict[str, str | int]:
    return {
        "schemaVersion": 1,
        "label": "api",
        "message": "online",
        "color": "brightgreen",
    }
