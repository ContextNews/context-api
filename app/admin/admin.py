import os
import secrets

from fastapi import FastAPI
from rds_postgres.models import Article, ArticleEntity, Entity, Story
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

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


class ArticleAdmin(ModelView, model=Article):
    column_list = [
        Article.id,
        Article.source,
        Article.title,
        Article.published_at,
        Article.ingested_at,
    ]
    can_create = False
    can_delete = False
    can_edit = False


class StoryAdmin(ModelView, model=Story):
    column_list = [
        Story.id,
        Story.title,
        Story.story_period,
        Story.generated_at,
        Story.updated_at,
    ]
    can_create = False
    can_delete = False
    can_edit = False


class EntityAdmin(ModelView, model=Entity):
    column_list = [Entity.type, Entity.name]
    can_create = False
    can_delete = False
    can_edit = False


class ArticleEntityAdmin(ModelView, model=ArticleEntity):
    column_list = [
        ArticleEntity.article_id,
        ArticleEntity.entity_type,
        ArticleEntity.entity_name,
        ArticleEntity.entity_count,
        ArticleEntity.entity_in_article_title,
    ]
    can_create = False
    can_delete = False
    can_edit = False


def init_admin(app: FastAPI) -> None:
    print("INIT ADMIN CALLED")
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

    print("ADMIN MOUNTING at /api/admin/db")

    auth = _AdminAuth(secret_key=secret_key, username=username, password=password)
    admin = Admin(app, engine, authentication_backend=auth, base_url="/api/admin/db")

    admin.add_view(ArticleAdmin)
    admin.add_view(StoryAdmin)
    admin.add_view(EntityAdmin)
    admin.add_view(ArticleEntityAdmin)

    for route in app.routes:
        print("ROUTE:", getattr(route, "path", route))
