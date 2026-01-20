from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import ArticleClusterOut
from rds_postgres.models import ArticleCluster, ArticleClusterArticle


router = APIRouter()


@router.get("/", response_model=list[ArticleClusterOut], response_model_exclude_none=True)
def list_article_clusters(
    include_article_ids: bool = Query(
        False, description="Include article IDs for each cluster"
    ),
    db: Session = Depends(get_db),
) -> list[ArticleClusterOut]:
    clusters = db.query(ArticleCluster).all()
    if not include_article_ids:
        return clusters

    cluster_ids = [cluster.article_cluster_id for cluster in clusters]
    if not cluster_ids:
        return []

    rows = (
        db.query(
            ArticleClusterArticle.article_cluster_id,
            ArticleClusterArticle.article_id,
        )
        .filter(ArticleClusterArticle.article_cluster_id.in_(cluster_ids))
        .all()
    )
    article_ids_by_cluster: dict[str, list[str]] = {}
    for cluster_id, article_id in rows:
        article_ids_by_cluster.setdefault(cluster_id, []).append(article_id)

    return [
        ArticleClusterOut(
            article_cluster_id=cluster.article_cluster_id,
            clustered_at=cluster.clustered_at,
            article_ids=article_ids_by_cluster.get(cluster.article_cluster_id, []),
        )
        for cluster in clusters
    ]
