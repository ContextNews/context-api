from pydantic import BaseModel

from app.schemas.news import ArticleLocationSchema


class LandingStory(BaseModel):
    story_id: str
    title: str
    locations: list[ArticleLocationSchema] = []


class RegionTopStories(BaseModel):
    region: str
    stories: list[LandingStory]
