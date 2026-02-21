import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.admin.admin import init_admin
from app.router import router

app = FastAPI(
    title="Context API",
    root_path="/api",
    root_path_in_servers=False,
    redirect_slashes=False,
)
# Innermost: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # local dev frontend
        "https://d1j7fhf5s3t3r4.cloudfront.net",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Session store required for SQLAdmin authentication
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("ADMIN_SECRET_KEY", ""),
)


# Corrects scope["scheme"] so SQLAdmin generates https:// URLs
@app.middleware("http")
async def fix_request_scheme(request: Request, call_next):  # type: ignore[no-untyped-def]
    proto = request.headers.get("x-forwarded-proto")
    if proto == "https" or "cloudfront.net" in str(request.base_url):
        request.scope["scheme"] = "https"
    return await call_next(request)


# Outermost: reads X-Forwarded-* headers from ALB first
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")


# TEMPORARY DIAGNOSTIC - remove after confirming headers
@app.middleware("http")
async def inspect_headers(request: Request, call_next):  # type: ignore[no-untyped-def]
    print(
        f"DEBUG: Host={request.headers.get('host')}, "
        f"Proto={request.headers.get('x-forwarded-proto')}",
        flush=True,
    )
    return await call_next(request)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/debug-path")
async def debug_path(request: Request) -> dict[str, str]:
    return {
        "path": request.scope["path"],
        "root_path": request.scope["root_path"],
    }


app.include_router(router)
init_admin(app)
