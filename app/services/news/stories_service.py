from datetime import date

from sqlalchemy.orm import Session

from app.queries.news.stories_queries import (
    query_stories,
    query_story_by_id,
    query_story_articles,
    query_story_locations,
    query_story_topics,
)
from app.schemas.enums import FilterPeriod, FilterRegion, FilterTopic
from app.schemas.news import ArticleLocationSchema, NewsStory, NewsStoryArticle, StoryCard
from app.services.utils.date_utils import get_date_range
from app.services.utils.image_fetcher import fetch_og_images


async def list_stories(
    db: Session,
    period: FilterPeriod,
    region: FilterRegion | None = None,
    topic: FilterTopic | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int | None = None,
) -> list[NewsStory]:
    start, end = get_date_range(period, from_date, to_date)

    stories_db = query_stories(db, start, end, region=region, topic=topic, limit=limit, parent_only=True)
    if not stories_db:
        return []

    story_ids = [story.id for story in stories_db]

    article_rows = query_story_articles(db, story_ids)
    locations_by_story = query_story_locations(db, story_ids)
    topics_by_story = query_story_topics(db, story_ids)

    article_urls = list({row[4] for row in article_rows})
    url_to_image = await fetch_og_images(article_urls)

    articles_by_story: dict[str, list[NewsStoryArticle]] = {}
    for story_id, article_id, title, source, url in article_rows:
        articles_by_story.setdefault(story_id, []).append(
            NewsStoryArticle(
                article_id=article_id,
                headline=title,
                source=source,
                url=url,
                image_url=url_to_image.get(url),
            )
        )

    stories: list[NewsStory] = []
    for story in stories_db:
        stories.append(
            NewsStory(
                story_id=story.id,
                title=story.title,
                summary=story.summary,
                key_points=story.key_points or [],
                topics=topics_by_story.get(story.id, []),
                locations=[
                    ArticleLocationSchema(**loc)
                    for loc in locations_by_story.get(story.id, [])
                ],
                story_period=story.story_period,
                generated_at=story.generated_at,
                updated_at=story.updated_at,
                articles=articles_by_story.get(story.id, []),
            )
        )

    return stories


async def get_story(db: Session, story_id: str) -> NewsStory | None:
    story = query_story_by_id(db, story_id)
    if not story:
        return None

    article_rows = query_story_articles(db, [story_id])
    locations_by_story = query_story_locations(db, [story_id])
    topics_by_story = query_story_topics(db, [story_id])

    article_urls = list({row[4] for row in article_rows})
    url_to_image = await fetch_og_images(article_urls)

    articles = [
        NewsStoryArticle(
            article_id=article_id,
            headline=title,
            source=source,
            url=url,
            image_url=url_to_image.get(url),
        )
        for _, article_id, title, source, url in article_rows
    ]

    return NewsStory(
        story_id=story.id,
        title=story.title,
        summary=story.summary,
        key_points=story.key_points or [],
        topics=topics_by_story.get(story_id, []),
        locations=[
            ArticleLocationSchema(**loc)
            for loc in locations_by_story.get(story_id, [])
        ],
        story_period=story.story_period,
        generated_at=story.generated_at,
        updated_at=story.updated_at,
        articles=articles,
    )


async def get_story_feed(
    db: Session,
    period: FilterPeriod,
    region: FilterRegion | None = None,
    topic: FilterTopic | None = None,
    limit: int | None = None,
) -> list[StoryCard]:
    start, end = get_date_range(period, None, None)

    stories_db = query_stories(db, start, end, region=region, topic=topic, limit=limit, parent_only=True)
    if not stories_db:
        return []

    story_ids = [story.id for story in stories_db]

    article_rows = query_story_articles(db, story_ids)
    locations_by_story = query_story_locations(db, story_ids)
    topics_by_story = query_story_topics(db, story_ids)

    # Get first image URL per story for the card
    article_urls = list({row[4] for row in article_rows})
    url_to_image = await fetch_og_images(article_urls)

    # Calculate counts and get first image per story
    article_counts: dict[str, int] = {}
    sources_by_story: dict[str, set[str]] = {}
    image_by_story: dict[str, str | None] = {}

    for story_id, _, _, source, url in article_rows:
        article_counts[story_id] = article_counts.get(story_id, 0) + 1
        sources_by_story.setdefault(story_id, set()).add(source)
        if story_id not in image_by_story:
            image_by_story[story_id] = url_to_image.get(url)

    cards: list[StoryCard] = []
    for story in stories_db:
        cards.append(
            StoryCard(
                story_id=story.id,
                title=story.title,
                topics=topics_by_story.get(story.id, []),
                locations=[
                    ArticleLocationSchema(**loc)
                    for loc in locations_by_story.get(story.id, [])
                ],
                article_count=article_counts.get(story.id, 0),
                sources_count=len(sources_by_story.get(story.id, set())),
                story_period=story.story_period.isoformat(),
                updated_at=story.updated_at.isoformat(),
                image_url=image_by_story.get(story.id),
            )
        )

    return cards
