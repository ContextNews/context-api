from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArticleOut(BaseModel):
    id: str
    source: str
    title: str
    summary: str
    url: str
    published_at: datetime
    ingested_at: datetime
    text: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ArticleClusterOut(BaseModel):
    article_cluster_id: str
    clustered_at: datetime
    article_ids: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)


class StoryArticleOut(BaseModel):
    article_id: str
    headline: str
    source: str


class StorySubStoryOut(BaseModel):
    story_id: str
    title: str


class StoryOut(BaseModel):
    story_id: str
    title: str
    summary: str
    key_points: list[str]
    primary_location: str | None
    generated_at: datetime
    updated_at: datetime
    articles: list[StoryArticleOut]
    sub_stories: list[StorySubStoryOut]


class SourceOut(BaseModel):
    source: str
    name: str
    url: str
    bias: str
    owner: str
    state_media: bool
    based: str
