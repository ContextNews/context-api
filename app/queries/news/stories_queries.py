from datetime import datetime

from sqlalchemy import func, literal_column, or_, text
from sqlalchemy.orm import Session

from app.schemas.enums import FilterRegion, FilterTopic
from rds_postgres.models import (
    Article,
    ArticleStory,
    Location,
    Person,
    Story,
    StoryLocation,
    StoryPerson,
    StoryStory,
    StoryTopic,
)

# Mapping of ISO 3166-1 alpha-3 country codes to regions
REGION_COUNTRY_CODES: dict[FilterRegion, set[str]] = {
    FilterRegion.north_america: {
        "USA", "CAN", "MEX", "GTM", "BLZ", "HND", "SLV", "NIC", "CRI", "PAN",
        "CUB", "JAM", "HTI", "DOM", "PRI", "TTO", "BHS", "BRB", "ATG", "DMA",
        "GRD", "KNA", "LCA", "VCT", "ABW", "CUW", "SXM", "BES", "AIA", "VGB",
        "VIR", "CYM", "TCA", "BMU", "GRL", "SPM", "MTQ", "GLP", "MAF", "BLM",
    },
    FilterRegion.south_america: {
        "BRA", "ARG", "COL", "PER", "VEN", "CHL", "ECU", "BOL", "PRY", "URY",
        "GUY", "SUR", "GUF", "FLK",
    },
    FilterRegion.europe: {
        "GBR", "DEU", "FRA", "ITA", "ESP", "PRT", "NLD", "BEL", "AUT", "CHE",
        "SWE", "NOR", "DNK", "FIN", "IRL", "POL", "CZE", "HUN", "ROU", "BGR",
        "GRC", "HRV", "SVK", "SVN", "EST", "LVA", "LTU", "CYP", "MLT", "LUX",
        "ISL", "AND", "MCO", "SMR", "VAT", "LIE", "ALB", "BIH", "MNE", "MKD",
        "SRB", "XKX", "UKR", "BLR", "MDA", "RUS", "GEO", "ARM", "AZE",
    },
    FilterRegion.africa: {
        "ZAF", "NGA", "EGY", "KEN", "ETH", "GHA", "TZA", "UGA", "DZA", "MAR",
        "TUN", "LBY", "SDN", "SSD", "AGO", "MOZ", "ZWE", "ZMB", "BWA", "NAM",
        "SEN", "CIV", "CMR", "COD", "COG", "GAB", "GNQ", "CAF", "TCD", "NER",
        "MLI", "BFA", "BEN", "TGO", "GIN", "SLE", "LBR", "GMB", "GNB", "CPV",
        "MRT", "ERI", "DJI", "SOM", "RWA", "BDI", "MWI", "LSO", "SWZ", "MDG",
        "MUS", "SYC", "COM", "REU", "MYT", "STP",
    },
    FilterRegion.middle_east: {
        "SAU", "ARE", "QAT", "KWT", "BHR", "OMN", "YEM", "IRQ", "IRN", "SYR",
        "JOR", "LBN", "ISR", "PSE", "TUR",
    },
    FilterRegion.asia: {
        "CHN", "JPN", "KOR", "PRK", "IND", "PAK", "BGD", "LKA", "NPL", "BTN",
        "MMR", "THA", "VNM", "LAO", "KHM", "MYS", "SGP", "IDN", "PHL", "BRN",
        "TLS", "MNG", "KAZ", "UZB", "TKM", "KGZ", "TJK", "AFG", "MDV", "HKG",
        "MAC", "TWN",
    },
    FilterRegion.oceania: {
        "AUS", "NZL", "PNG", "FJI", "SLB", "VUT", "NCL", "PYF", "WSM", "TON",
        "FSM", "MHL", "PLW", "KIR", "NRU", "TUV", "COK", "NIU", "TKL", "ASM",
        "GUM", "MNP", "WLF",
    },
}


def query_stories(
    db: Session,
    from_date: datetime,
    to_date: datetime,
    region: FilterRegion | None = None,
    topic: FilterTopic | None = None,
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

    if topic:
        query = (
            query.join(StoryTopic, StoryTopic.story_id == Story.id)
            .filter(StoryTopic.topic == topic.value)
            .distinct()
        )

    query = query.order_by(Story.story_period.desc())

    if limit:
        query = query.limit(limit)

    return query.all()


def query_story_by_id(db: Session, story_id: str) -> Story | None:
    return db.query(Story).filter(Story.id == story_id).first()


def query_related_stories(db: Session, story_id: str) -> list[Story]:
    """
    Traverse the full story_stories graph using a recursive CTE
    to find all transitively connected stories, not just direct neighbors.
    """
    related_ids = [
        row[0]
        for row in db.execute(
            text("""
                WITH RECURSIVE related AS (
                    SELECT CAST(:story_id AS varchar) AS id, 0 AS depth
                    UNION
                    SELECT CASE
                        WHEN ss.story_id_1 = related.id THEN ss.story_id_2
                        ELSE ss.story_id_1
                    END,
                    related.depth + 1
                    FROM story_stories ss
                    JOIN related ON (ss.story_id_1 = related.id OR ss.story_id_2 = related.id)
                        AND related.depth < 10
                )
                SELECT id FROM related WHERE id != :story_id
            """),
            {"story_id": story_id},
        ).fetchall()
    ]

    if not related_ids:
        return []

    return (
        db.query(Story)
        .filter(Story.id.in_(related_ids))
        .order_by(Story.story_period.desc())
        .all()
    )


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


def query_story_persons(db: Session, story_ids: list[str]) -> dict[str, list]:
    """
    Query persons for a list of stories.
    Returns a dict mapping story_id -> list of person data.
    """
    if not story_ids:
        return {}

    rows = (
        db.query(
            StoryPerson.story_id,
            Person.wikidata_qid,
            Person.name,
            Person.description,
            Person.nationalities,
            Person.image_url,
        )
        .join(Person, Person.wikidata_qid == StoryPerson.wikidata_qid)
        .filter(StoryPerson.story_id.in_(story_ids))
        .all()
    )

    persons_by_story: dict[str, list] = {}
    for row in rows:
        persons_by_story.setdefault(row.story_id, []).append(
            {
                "wikidata_qid": row.wikidata_qid,
                "name": row.name,
                "description": row.description,
                "nationalities": row.nationalities,
                "image_url": row.image_url,
            }
        )

    return persons_by_story
