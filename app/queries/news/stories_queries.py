from datetime import datetime
from typing import Any

from rds_postgres.models import (
    Article,
    ArticleStory,
    KBEntity,
    KBLocation,
    KBPerson,
    Story,
    StoryEntity,
    StoryTopic,
)
from sqlalchemy import func, literal_column, text
from sqlalchemy.orm import Session

from app.schemas.enums import FilterRegion, FilterTopic

# Mapping of ISO 3166-1 alpha-3 country codes to regions
REGION_COUNTRY_CODES: dict[FilterRegion, set[str]] = {
    FilterRegion.north_america: {
        "USA",
        "CAN",
        "MEX",
        "GTM",
        "BLZ",
        "HND",
        "SLV",
        "NIC",
        "CRI",
        "PAN",
        "CUB",
        "JAM",
        "HTI",
        "DOM",
        "PRI",
        "TTO",
        "BHS",
        "BRB",
        "ATG",
        "DMA",
        "GRD",
        "KNA",
        "LCA",
        "VCT",
        "ABW",
        "CUW",
        "SXM",
        "BES",
        "AIA",
        "VGB",
        "VIR",
        "CYM",
        "TCA",
        "BMU",
        "GRL",
        "SPM",
        "MTQ",
        "GLP",
        "MAF",
        "BLM",
    },
    FilterRegion.south_america: {
        "BRA",
        "ARG",
        "COL",
        "PER",
        "VEN",
        "CHL",
        "ECU",
        "BOL",
        "PRY",
        "URY",
        "GUY",
        "SUR",
        "GUF",
        "FLK",
    },
    FilterRegion.europe: {
        "GBR",
        "DEU",
        "FRA",
        "ITA",
        "ESP",
        "PRT",
        "NLD",
        "BEL",
        "AUT",
        "CHE",
        "SWE",
        "NOR",
        "DNK",
        "FIN",
        "IRL",
        "POL",
        "CZE",
        "HUN",
        "ROU",
        "BGR",
        "GRC",
        "HRV",
        "SVK",
        "SVN",
        "EST",
        "LVA",
        "LTU",
        "CYP",
        "MLT",
        "LUX",
        "ISL",
        "AND",
        "MCO",
        "SMR",
        "VAT",
        "LIE",
        "ALB",
        "BIH",
        "MNE",
        "MKD",
        "SRB",
        "XKX",
        "UKR",
        "BLR",
        "MDA",
        "RUS",
        "GEO",
        "ARM",
        "AZE",
    },
    FilterRegion.africa: {
        "ZAF",
        "NGA",
        "EGY",
        "KEN",
        "ETH",
        "GHA",
        "TZA",
        "UGA",
        "DZA",
        "MAR",
        "TUN",
        "LBY",
        "SDN",
        "SSD",
        "AGO",
        "MOZ",
        "ZWE",
        "ZMB",
        "BWA",
        "NAM",
        "SEN",
        "CIV",
        "CMR",
        "COD",
        "COG",
        "GAB",
        "GNQ",
        "CAF",
        "TCD",
        "NER",
        "MLI",
        "BFA",
        "BEN",
        "TGO",
        "GIN",
        "SLE",
        "LBR",
        "GMB",
        "GNB",
        "CPV",
        "MRT",
        "ERI",
        "DJI",
        "SOM",
        "RWA",
        "BDI",
        "MWI",
        "LSO",
        "SWZ",
        "MDG",
        "MUS",
        "SYC",
        "COM",
        "REU",
        "MYT",
        "STP",
    },
    FilterRegion.middle_east: {
        "SAU",
        "ARE",
        "QAT",
        "KWT",
        "BHR",
        "OMN",
        "YEM",
        "IRQ",
        "IRN",
        "SYR",
        "JOR",
        "LBN",
        "ISR",
        "PSE",
        "TUR",
    },
    FilterRegion.asia: {
        "CHN",
        "JPN",
        "KOR",
        "PRK",
        "IND",
        "PAK",
        "BGD",
        "LKA",
        "NPL",
        "BTN",
        "MMR",
        "THA",
        "VNM",
        "LAO",
        "KHM",
        "MYS",
        "SGP",
        "IDN",
        "PHL",
        "BRN",
        "TLS",
        "MNG",
        "KAZ",
        "UZB",
        "TKM",
        "KGZ",
        "TJK",
        "AFG",
        "MDV",
        "HKG",
        "MAC",
        "TWN",
    },
    FilterRegion.oceania: {
        "AUS",
        "NZL",
        "PNG",
        "FJI",
        "SLB",
        "VUT",
        "NCL",
        "PYF",
        "WSM",
        "TON",
        "FSM",
        "MHL",
        "PLW",
        "KIR",
        "NRU",
        "TUV",
        "COK",
        "NIU",
        "TKL",
        "ASM",
        "GUM",
        "MNP",
        "WLF",
    },
}


def query_stories(
    db: Session,
    from_date: datetime,
    to_date: datetime,
    region: FilterRegion | None = None,
    topic: FilterTopic | None = None,
    limit: int | None = None,
    offset: int | None = None,
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
            query.join(StoryEntity, StoryEntity.story_id == Story.id)
            .join(KBEntity, KBEntity.qid == StoryEntity.qid)
            .join(KBLocation, KBLocation.qid == KBEntity.qid)
            .filter(KBEntity.entity_type == "location")
            .filter(KBLocation.country_code.in_(country_codes))
            .distinct()
        )

    if topic:
        query = (
            query.join(StoryTopic, StoryTopic.story_id == Story.id)
            .filter(StoryTopic.topic == topic.value)
            .distinct()
        )

    query = query.order_by(Story.story_period.desc(), Story.id.desc())

    if offset:
        query = query.offset(offset)

    if limit:
        query = query.limit(limit)

    return query.all()  # type: ignore[no-any-return]


def query_story_by_id(db: Session, story_id: str) -> Story | None:
    return db.query(Story).filter(Story.id == story_id).first()


def query_related_stories(db: Session, story_id: str) -> list[Story]:
    """
    Traverse the story_edges graph using a recursive CTE
    to find all transitively connected stories, not just direct neighbors.
    story_edges is directional, so we seed from both directions.
    """
    related_ids = [
        row[0]
        for row in db.execute(
            text("""
                WITH RECURSIVE related(id, depth) AS (
                    SELECT to_story_id AS id, 1
                    FROM story_edges
                    WHERE from_story_id = :story_id
                    UNION
                    SELECT from_story_id AS id, 1
                    FROM story_edges
                    WHERE to_story_id = :story_id
                    UNION ALL
                    SELECT se.to_story_id, r.depth + 1
                    FROM story_edges se
                    JOIN related r ON se.from_story_id = r.id
                    WHERE r.depth < 10
                )
                SELECT DISTINCT id FROM related WHERE id != :story_id
            """),
            {"story_id": story_id},
        ).fetchall()
    ]

    if not related_ids:
        return []

    return (  # type: ignore[no-any-return]
        db.query(Story)
        .filter(Story.id.in_(related_ids))
        .order_by(Story.story_period.desc())
        .all()
    )


def query_sub_stories(db: Session, parent_story_ids: list[str]) -> list[Story]:
    if not parent_story_ids:
        return []
    return db.query(Story).filter(Story.parent_story_id.in_(parent_story_ids)).all()  # type: ignore[no-any-return]


def query_story_articles(
    db: Session,
    story_ids: list[str],
) -> list[tuple[str, str, str, str, str]]:
    if not story_ids:
        return []
    return (  # type: ignore[no-any-return]
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


def query_story_locations(db: Session, story_ids: list[str]) -> dict[str, list[Any]]:
    """
    Query locations for a list of stories.
    Returns a dict mapping story_id -> list of location data.
    """
    if not story_ids:
        return {}

    rows = (
        db.query(
            StoryEntity.story_id,
            KBEntity.qid.label("wikidata_qid"),
            KBEntity.name,
            KBLocation.location_type,
            KBLocation.country_code,
            func.ST_Y(literal_column("kb_locations.coordinates::geometry")).label(
                "latitude"
            ),
            func.ST_X(literal_column("kb_locations.coordinates::geometry")).label(
                "longitude"
            ),
        )
        .join(KBEntity, KBEntity.qid == StoryEntity.qid)
        .join(KBLocation, KBLocation.qid == KBEntity.qid)
        .filter(StoryEntity.story_id.in_(story_ids))
        .filter(KBEntity.entity_type == "location")
        .all()
    )

    locations_by_story: dict[str, list[Any]] = {}
    for row in rows:
        locations_by_story.setdefault(row.story_id, []).append(
            {
                "wikidata_qid": row.wikidata_qid,
                "name": row.name,
                "location_type": row.location_type,
                "country_code": row.country_code,
                "latitude": float(row.latitude),
                "longitude": float(row.longitude),
            }
        )

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


def query_story_persons(db: Session, story_ids: list[str]) -> dict[str, list[Any]]:
    """
    Query persons for a list of stories.
    Returns a dict mapping story_id -> list of person data.
    """
    if not story_ids:
        return {}

    rows = (
        db.query(
            StoryEntity.story_id,
            KBEntity.qid.label("wikidata_qid"),
            KBEntity.name,
            KBEntity.description,
            KBEntity.image_url,
            KBPerson.nationalities,
        )
        .join(KBEntity, KBEntity.qid == StoryEntity.qid)
        .join(KBPerson, KBPerson.qid == KBEntity.qid)
        .filter(StoryEntity.story_id.in_(story_ids))
        .filter(KBEntity.entity_type == "person")
        .all()
    )

    persons_by_story: dict[str, list[Any]] = {}
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
