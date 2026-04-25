from datetime import date, datetime

from pydantic import BaseModel


class KBEntitySchema(BaseModel):
    qid: str
    entity_type: str
    name: str
    description: str | None = None
    image_url: str | None = None
    nationalities: list[str] | None = None


class EntityMentionDay(BaseModel):
    date: date
    count: int


class EntityHeatmapResponse(BaseModel):
    data: list[EntityMentionDay]


class EntityPeriodCounts(BaseModel):
    today: int
    this_month: int
    this_year: int


class EntityLocationStat(BaseModel):
    name: str
    country_code: str | None = None
    story_count: int


class EntityTopicStat(BaseModel):
    topic: str
    story_count: int


class EntitySourceStat(BaseModel):
    source: str
    article_count: int


class EntityCoverageStatsResponse(BaseModel):
    period_counts: EntityPeriodCounts
    top_locations: list[EntityLocationStat]
    topics: list[EntityTopicStat]
    sources: list[EntitySourceStat]


class MilitaryAircraftSchema(BaseModel):
    hex: str
    callsign: str | None = None
    lat: float
    lon: float
    altitude_ft: int | None = None
    on_ground: bool = False
    speed_kts: int | None = None
    heading_deg: int | None = None
    aircraft_type: str | None = None
    registration: str | None = None


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


class TgStructuredPostSchema(BaseModel):
    post_id: int
    channel_id: int
    message_id: int
    text: str | None = None
    date: datetime | None = None
    label: str
    priority: int
    latitude: float | None = None
    longitude: float | None = None
    location_name: str | None = None
    story_id: str | None = None


class TgStructuredPostListSchema(BaseModel):
    items: list[TgStructuredPostSchema]
    has_more: bool
