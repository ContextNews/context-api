from datetime import datetime

from sqlalchemy import func, literal_column
from sqlalchemy.orm import Session

from app.schemas.enums import FilterRegion
from rds_postgres.models import Article, ArticleStory, Location, Story, StoryLocation, StoryTopic

# Mapping of country codes to regions
REGION_COUNTRY_CODES: dict[FilterRegion, set[str]] = {
    FilterRegion.north_america: {
        "US", "CA", "MX", "GT", "BZ", "HN", "SV", "NI", "CR", "PA",
        "CU", "JM", "HT", "DO", "PR", "TT", "BS", "BB", "AG", "DM",
        "GD", "KN", "LC", "VC", "AW", "CW", "SX", "BQ", "AI", "VG",
        "VI", "KY", "TC", "BM", "GL", "PM", "MQ", "GP", "MF", "BL",
    },
    FilterRegion.south_america: {
        "BR", "AR", "CO", "PE", "VE", "CL", "EC", "BO", "PY", "UY",
        "GY", "SR", "GF", "FK",
    },
    FilterRegion.europe: {
        "GB", "DE", "FR", "IT", "ES", "PT", "NL", "BE", "AT", "CH",
        "SE", "NO", "DK", "FI", "IE", "PL", "CZ", "HU", "RO", "BG",
        "GR", "HR", "SK", "SI", "EE", "LV", "LT", "CY", "MT", "LU",
        "IS", "AD", "MC", "SM", "VA", "LI", "AL", "BA", "ME", "MK",
        "RS", "XK", "UA", "BY", "MD", "RU", "GE", "AM", "AZ",
    },
    FilterRegion.africa: {
        "ZA", "NG", "EG", "KE", "ET", "GH", "TZ", "UG", "DZ", "MA",
        "TN", "LY", "SD", "SS", "AO", "MZ", "ZW", "ZM", "BW", "NA",
        "SN", "CI", "CM", "CD", "CG", "GA", "GQ", "CF", "TD", "NE",
        "ML", "BF", "BJ", "TG", "GN", "SL", "LR", "GM", "GW", "CV",
        "MR", "ER", "DJ", "SO", "RW", "BI", "MW", "LS", "SZ", "MG",
        "MU", "SC", "KM", "RE", "YT", "ST",
    },
    FilterRegion.middle_east: {
        "SA", "AE", "QA", "KW", "BH", "OM", "YE", "IQ", "IR", "SY",
        "JO", "LB", "IL", "PS", "TR",
    },
    FilterRegion.asia: {
        "CN", "JP", "KR", "KP", "IN", "PK", "BD", "LK", "NP", "BT",
        "MM", "TH", "VN", "LA", "KH", "MY", "SG", "ID", "PH", "BN",
        "TL", "MN", "KZ", "UZ", "TM", "KG", "TJ", "AF", "MV", "HK",
        "MO", "TW",
    },
    FilterRegion.oceania: {
        "AU", "NZ", "PG", "FJ", "SB", "VU", "NC", "PF", "WS", "TO",
        "FM", "MH", "PW", "KI", "NR", "TV", "CK", "NU", "TK", "AS",
        "GU", "MP", "WF",
    },
}


def query_stories(
    db: Session,
    from_date: datetime,
    to_date: datetime,
    region: FilterRegion | None = None,
    limit: int | None = None,
    parent_only: bool = True,
) -> list[Story]:
    query = db.query(Story).filter(
        Story.story_period >= from_date,
        Story.story_period < to_date,
    )

    if parent_only:
        query = query.filter(Story.parent_story_id.is_(None))

    if region:
        country_codes = REGION_COUNTRY_CODES.get(region, set())
        query = (
            query.join(StoryLocation, StoryLocation.story_id == Story.id)
            .join(Location, Location.wikidata_qid == StoryLocation.wikidata_qid)
            .filter(Location.country_code.in_(country_codes))
            .distinct()
        )

    query = query.order_by(Story.story_period.desc())

    if limit:
        query = query.limit(limit)

    return query.all()


def query_story_by_id(db: Session, story_id: str) -> Story | None:
    return db.query(Story).filter(Story.id == story_id).first()


def query_sub_stories(db: Session, parent_story_ids: list[str]) -> list[Story]:
    if not parent_story_ids:
        return []
    return (
        db.query(Story)
        .filter(Story.parent_story_id.in_(parent_story_ids))
        .all()
    )


def query_story_articles(
    db: Session,
    story_ids: list[str],
) -> list[tuple[str, str, str, str, str]]:
    if not story_ids:
        return []
    return (
        db.query(
            ArticleStory.story_id,
            Article.id,
            Article.title,
            Article.source,
            Article.url,
        )
        .join(Article, Article.id == ArticleStory.article_id)
        .filter(ArticleStory.story_id.in_(story_ids))
        .all()
    )


def query_story_locations(db: Session, story_ids: list[str]) -> dict[str, list]:
    """
    Query locations for a list of stories.
    Returns a dict mapping story_id -> list of location data.
    """
    if not story_ids:
        return {}

    rows = (
        db.query(
            StoryLocation.story_id,
            Location.wikidata_qid,
            Location.name,
            Location.location_type,
            Location.country_code,
            func.ST_Y(literal_column("locations.coordinates::geometry")).label("latitude"),
            func.ST_X(literal_column("locations.coordinates::geometry")).label("longitude"),
        )
        .join(Location, Location.wikidata_qid == StoryLocation.wikidata_qid)
        .filter(StoryLocation.story_id.in_(story_ids))
        .all()
    )

    locations_by_story: dict[str, list] = {}
    for row in rows:
        locations_by_story.setdefault(row.story_id, []).append({
            "wikidata_qid": row.wikidata_qid,
            "name": row.name,
            "location_type": row.location_type,
            "country_code": row.country_code,
            "latitude": row.latitude,
            "longitude": row.longitude,
        })

    return locations_by_story


def query_story_topics(db: Session, story_ids: list[str]) -> dict[str, list[str]]:
    """
    Query topics for a list of stories.
    Returns a dict mapping story_id -> list of topic strings.
    """
    if not story_ids:
        return {}

    rows = (
        db.query(StoryTopic.story_id, StoryTopic.topic)
        .filter(StoryTopic.story_id.in_(story_ids))
        .all()
    )

    topics_by_story: dict[str, list[str]] = {}
    for row in rows:
        topics_by_story.setdefault(row.story_id, []).append(row.topic)

    return topics_by_story
