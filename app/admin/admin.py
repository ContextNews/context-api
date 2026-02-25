import os
import secrets

from fastapi import FastAPI
from rds_postgres.models import (
    Article,
    ArticleCluster,
    ArticleClusterArticle,
    ArticleEmbedding,
    ArticleEntityMention,
    ArticleEntityResolved,
    ArticleStory,
    ArticleTopic,
    KBEntity,
    KBEntityAlias,
    KBLocation,
    KBPerson,
    Story,
    StoryEdge,
    StoryEntity,
    StoryTopic,
    Topic,
)
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.admin.dashboard import DashboardView
from app.db import engine


class _AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str, username: str, password: str) -> None:
        super().__init__(secret_key=secret_key)
        self._username = username
        self._password = password

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = str(form.get("username", ""))
        password = str(form.get("password", ""))
        if secrets.compare_digest(username, self._username) and secrets.compare_digest(
            password, self._password
        ):
            request.session.update({"authenticated": True})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("authenticated"))


class _ReadOnlyModelView(ModelView):
    can_create = False
    can_delete = False
    can_edit = False


class ArticleAdmin(_ReadOnlyModelView, model=Article):
    column_list = [
        Article.id,
        Article.source,
        Article.title,
        Article.published_at,
        Article.ingested_at,
    ]


class ArticleEmbeddingAdmin(_ReadOnlyModelView, model=ArticleEmbedding):
    column_list = [
        ArticleEmbedding.article_id,
        ArticleEmbedding.embedding_model,
        ArticleEmbedding.embedded_text,
    ]


class ArticleClusterAdmin(_ReadOnlyModelView, model=ArticleCluster):
    column_list = [ArticleCluster.article_cluster_id, ArticleCluster.cluster_period]


class ArticleClusterArticleAdmin(_ReadOnlyModelView, model=ArticleClusterArticle):
    column_list = [
        ArticleClusterArticle.article_cluster_id,
        ArticleClusterArticle.article_id,
    ]


class ArticleTopicAdmin(_ReadOnlyModelView, model=ArticleTopic):
    column_list = [ArticleTopic.article_id, ArticleTopic.topic]


class ArticleStoryAdmin(_ReadOnlyModelView, model=ArticleStory):
    column_list = [ArticleStory.article_id, ArticleStory.story_id]


class ArticleEntityResolvedAdmin(_ReadOnlyModelView, model=ArticleEntityResolved):
    column_list = [
        ArticleEntityResolved.article_id,
        ArticleEntityResolved.qid,
        ArticleEntityResolved.score,
    ]


class ArticleEntityMentionAdmin(_ReadOnlyModelView, model=ArticleEntityMention):
    column_list = [
        ArticleEntityMention.article_id,
        ArticleEntityMention.ner_type,
        ArticleEntityMention.mention_text,
        ArticleEntityMention.mention_count,
        ArticleEntityMention.in_title,
    ]


class StoryAdmin(_ReadOnlyModelView, model=Story):
    column_list = [
        Story.id,
        Story.title,
        Story.story_period,
        Story.created_at,
        Story.updated_at,
    ]


class StoryTopicAdmin(_ReadOnlyModelView, model=StoryTopic):
    column_list = [StoryTopic.story_id, StoryTopic.topic]


class StoryEntityAdmin(_ReadOnlyModelView, model=StoryEntity):
    column_list = [StoryEntity.story_id, StoryEntity.qid]


class StoryEdgeAdmin(_ReadOnlyModelView, model=StoryEdge):
    column_list = [
        StoryEdge.from_story_id,
        StoryEdge.to_story_id,
        StoryEdge.relation_type,
        StoryEdge.score,
    ]


class TopicAdmin(_ReadOnlyModelView, model=Topic):
    column_list = [Topic.topic]


class KBEntityAdmin(_ReadOnlyModelView, model=KBEntity):
    column_list = [
        KBEntity.qid,
        KBEntity.entity_type,
        KBEntity.name,
        KBEntity.description,
    ]


class KBEntityAliasAdmin(_ReadOnlyModelView, model=KBEntityAlias):
    column_list = [KBEntityAlias.alias, KBEntityAlias.qid]


class KBLocationAdmin(_ReadOnlyModelView, model=KBLocation):
    column_list = [
        KBLocation.qid,
        KBLocation.location_type,
        KBLocation.country_code,
    ]


class KBPersonAdmin(_ReadOnlyModelView, model=KBPerson):
    column_list = [KBPerson.qid, KBPerson.nationalities]


def init_admin(app: FastAPI) -> None:
    username = os.environ.get("ADMIN_USERNAME")
    password = os.environ.get("ADMIN_PASSWORD")
    secret_key = os.environ.get("ADMIN_SECRET_KEY")

    if not username or not password or not secret_key:
        print(
            f"ADMIN NOT MOUNTED - missing vars: "
            f"username={bool(username)} "
            f"password={bool(password)} "
            f"secret_key={bool(secret_key)}"
        )
        return

    auth = _AdminAuth(secret_key=secret_key, username=username, password=password)
    admin = Admin(
        app,
        engine,
        authentication_backend=auth,
        base_url="/admin/db",
        templates_dir="app/templates",
    )

    admin.add_view(ArticleAdmin)
    admin.add_view(ArticleEmbeddingAdmin)
    admin.add_view(ArticleClusterAdmin)
    admin.add_view(ArticleClusterArticleAdmin)
    admin.add_view(ArticleTopicAdmin)
    admin.add_view(ArticleStoryAdmin)
    admin.add_view(ArticleEntityResolvedAdmin)
    admin.add_view(ArticleEntityMentionAdmin)
    admin.add_view(StoryAdmin)
    admin.add_view(StoryTopicAdmin)
    admin.add_view(StoryEntityAdmin)
    admin.add_view(StoryEdgeAdmin)
    admin.add_view(TopicAdmin)
    admin.add_view(KBEntityAdmin)
    admin.add_view(KBEntityAliasAdmin)
    admin.add_view(KBLocationAdmin)
    admin.add_view(KBPersonAdmin)
    admin.add_base_view(DashboardView)
