from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.image_fetcher import fetch_og_images
from app.schemas import StoryArticleOut, StoryOut, StorySubStoryOut
from rds_postgres.models import Article, ArticleStory, Story


router = APIRouter()


@router.get("/", response_model=list[StoryOut])
async def list_stories(
    story_date: date | None = Query(
        default=None,
        description="Filter by story period date (YYYY-MM-DD). Defaults to today.",
    ),
    db: Session = Depends(get_db),
) -> list[StoryOut]:
    target_date = story_date or date.today()
    start = datetime.combine(target_date, time.min)
    end = start + timedelta(days=1)
    stories_db = (
        db.query(Story)
        .filter(Story.parent_story_id.is_(None))
        .filter(Story.story_period >= start, Story.story_period < end)
        .all()
    )
    if not stories_db:
        return []

    story_ids = [story.id for story in stories_db]

    article_rows = (
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

    article_urls = list({row[4] for row in article_rows})
    url_to_image = await fetch_og_images(article_urls)

    articles_by_story: dict[str, list[StoryArticleOut]] = {}
    for story_id, article_id, title, source, url in article_rows:
        articles_by_story.setdefault(story_id, []).append(
            StoryArticleOut(
                article_id=article_id,
                headline=title,
                source=source,
                url=url,
                image_url=url_to_image.get(url),
            )
        )

    sub_stories_db = (
        db.query(Story)
        .filter(Story.parent_story_id.in_(story_ids))
        .all()
    )

    sub_stories_by_parent: dict[str, list[StorySubStoryOut]] = {}
    for sub_story in sub_stories_db:
        sub_stories_by_parent.setdefault(sub_story.parent_story_id, []).append(
            StorySubStoryOut(story_id=sub_story.id, title=sub_story.title)
        )

    stories: list[StoryOut] = []
    for story in stories_db:
        stories.append(
            StoryOut(
                story_id=story.id,
                title=story.title,
                summary=story.summary,
                key_points=story.key_points or [],
                primary_location=story.primary_location,
                story_period=story.story_period,
                generated_at=story.generated_at,
                updated_at=story.updated_at,
                articles=articles_by_story.get(story.id, []),
                sub_stories=sub_stories_by_parent.get(story.id, []),
            )
        )

    return stories
