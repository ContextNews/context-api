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
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("ADMIN_SECRET_KEY", ""),
)
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
