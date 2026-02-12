from sqlalchemy.orm import Session

from app.queries.news.stories_queries import (
    query_stories,
    query_story_locations,
)
from app.schemas.enums import FilterPeriod, FilterRegion
from app.schemas.landing import LandingStory, RegionTopStories
from app.schemas.news import ArticleLocationSchema
from app.services.utils.date_utils import get_date_range


async def get_top_stories_by_region(
    db: Session,
    period: FilterPeriod,
) -> list[RegionTopStories]:
    start, end = get_date_range(period, None, None)

    # Query top 3 stories per region
    stories_by_region: dict[FilterRegion, list] = {}
    all_story_ids: list[str] = []

    for region in FilterRegion:
        stories = query_stories(db, start, end, region=region, limit=3, parent_only=True)
        stories_by_region[region] = stories
        all_story_ids.extend(story.id for story in stories)

    if not all_story_ids:
        return []

    # Batch fetch locations for all stories at once
    locations_by_story = query_story_locations(db, all_story_ids)

    # Assemble response grouped by region
    result: list[RegionTopStories] = []
    for region in FilterRegion:
        stories: list[LandingStory] = []
        for story in stories_by_region[region]:
            stories.append(
                LandingStory(
                    story_id=story.id,
                    title=story.title,
                    locations=[
                        ArticleLocationSchema(**loc)
                        for loc in locations_by_story.get(story.id, [])
                    ],
                )
            )
        result.append(RegionTopStories(region=region.value, stories=stories))

    return result
