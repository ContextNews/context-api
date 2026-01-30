from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router import router


app = FastAPI(
    title="Context API",
    root_path="/api",
    root_path_in_servers=False,
    redirect_slashes=False,
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

app.include_router(router)
