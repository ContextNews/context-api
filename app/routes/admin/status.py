from fastapi import APIRouter

router = APIRouter(prefix="/status")


@router.get("/")
def status_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/badge")
def status_badge():
    return {
        "schemaVersion": 1,
        "label": "api",
        "message": "online",
        "color": "brightgreen"
    }
