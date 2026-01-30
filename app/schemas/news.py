from pydantic import BaseModel
from datetime import datetime

class EntityCount(BaseModel):
    type: str
    name: str
    count: int

class NewsSource(BaseModel):
    source: str
    name: str
    url: str
    bias: str
    owner: str
    state_media: bool
    based: str

class StoryCard(BaseModel):
    story_id: str
    title: str
    primary_location: str | None
    article_count: int
    sources_count: int
    story_period: str
    updated_at: str
    image_url: str | None = None

class NewsStoryArticle(BaseModel):
    article_id: str
    headline: str
    source: str
    url: str
    image_url: str | None = None

class NewsStory(BaseModel):
    story_id: str
    title: str
    summary: str
    key_points: list[str]
    primary_location: str | None
    story_period: datetime
    generated_at: datetime
    updated_at: datetime
    articles: list[NewsStoryArticle]

class NewsArticle(BaseModel):
    id: str
    source: str
    title: str
    summary: str
    url: str
    published_at: datetime
    ingested_at: datetime

