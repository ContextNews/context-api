from fastapi import FastAPI

from app.routes import article_clusters, articles, sources, stories


app = FastAPI(title="Context API")

app.include_router(articles.router, prefix="/articles", tags=["articles"])
app.include_router(
    article_clusters.router, prefix="/article-clusters", tags=["article-clusters"]
)
app.include_router(stories.router, prefix="/stories", tags=["stories"])
app.include_router(sources.router, tags=["sources"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
