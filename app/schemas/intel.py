from datetime import datetime

from pydantic import BaseModel


class KBEntitySchema(BaseModel):
    qid: str
    entity_type: str
    name: str
    description: str | None = None
    image_url: str | None = None
    nationalities: list[str] | None = None


class TgChannelSchema(BaseModel):
    id: int
    username: str
    channel_id: int | None = None
    title: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime


class TgPostSchema(BaseModel):
    id: int
    channel_id: int
    message_id: int
    text: str | None = None
    date: datetime | None = None
    edit_date: datetime | None = None
    has_media: bool
    media_type: str | None = None
    collected_at: datetime


class TgPostListSchema(BaseModel):
    items: list[TgPostSchema]
    has_more: bool
