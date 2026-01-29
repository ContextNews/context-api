from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import (
    article_clusters,
    articles,
    sources,
    stories,
    top_locations,
    top_people,
)


app = FastAPI(
    title="Context API",
    root_path="/api",
    root_path_in_servers=False,
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

app.include_router(articles.router, prefix="/articles", tags=["articles"])
app.include_router(
    article_clusters.router, prefix="/article-clusters", tags=["article-clusters"]
)
app.include_router(stories.router, prefix="/stories", tags=["stories"])
app.include_router(sources.router, tags=["sources"])
app.include_router(top_locations.router, prefix="/top-locations", tags=["locations"])
app.include_router(top_people.router, prefix="/top-people", tags=["people"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/health/badge")
def health_badge():
    return {
        "schemaVersion": 1,
        "label": "api",
        "message": "healthy",
        "color": "brightgreen"
    }
