from datetime import datetime

from pydantic import BaseModel


class EntityCount(BaseModel):
    type: str
    name: str
    count: int


class HistoricalEntityCountDataPoint(BaseModel):
    timestamp: datetime
    count: int


class HistoricalEntityCount(BaseModel):
    type: str
    name: str
    count: int
    history: list[HistoricalEntityCountDataPoint]


class NewsSource(BaseModel):
    source: str
    name: str
    url: str
    bias: str
    owner: str
    state_media: bool
    based: str


class ArticleLocationSchema(BaseModel):
    wikidata_qid: str
    name: str
    location_type: str
    country_code: str | None = None
    latitude: float
    longitude: float


class StoryPersonSchema(BaseModel):
    wikidata_qid: str
    name: str
    description: str | None = None
    nationalities: list[str] | None = None
    image_url: str | None = None


class StoryCard(BaseModel):
    story_id: str
    title: str
    topics: list[str] = []
    locations: list[ArticleLocationSchema] = []
    persons: list[StoryPersonSchema] = []
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
    topics: list[str] = []
    locations: list[ArticleLocationSchema] = []
    persons: list[StoryPersonSchema] = []
    story_period: datetime
    generated_at: datetime
    updated_at: datetime
    articles: list[NewsStoryArticle]


class RelatedStorySchema(BaseModel):
    story_id: str
    title: str
    summary: str
    story_period: datetime
    updated_at: datetime


class NewsStoryWithRelated(NewsStory):
    related_stories: list[RelatedStorySchema] = []


class NewsArticle(BaseModel):
    id: str
    source: str
    title: str
    summary: str
    url: str
    published_at: datetime
    ingested_at: datetime
    locations: list[ArticleLocationSchema] = []
