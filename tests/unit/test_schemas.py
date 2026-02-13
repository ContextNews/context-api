from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.enums import FilterPeriod, FilterRegion, FilterTopic, Interval
from app.schemas.landing import LandingStory, RegionTopStories
from app.schemas.news import (
    ArticleLocationSchema,
    NewsStory,
    NewsStoryArticle,
    NewsStoryWithRelated,
    RelatedStorySchema,
    StoryCard,
    StoryPersonSchema,
)


class TestFilterEnums:
    def test_filter_period_values(self):
        assert FilterPeriod.today.value == "today"
        assert FilterPeriod.week.value == "week"
        assert FilterPeriod.month.value == "month"

    def test_filter_region_values(self):
        assert len(FilterRegion) == 7
        assert FilterRegion.europe.value == "europe"

    def test_filter_topic_values(self):
        assert FilterTopic.politics.value == "Politics"
        assert FilterTopic.conflict_and_security.value == "Conflict & Security"

    def test_interval_values(self):
        assert Interval.hourly.value == "hourly"
        assert Interval.daily.value == "daily"


class TestArticleLocationSchema:
    def test_valid_location(self):
        loc = ArticleLocationSchema(
            wikidata_qid="Q84",
            name="London",
            location_type="city",
            country_code="GBR",
            latitude=51.5,
            longitude=-0.12,
        )
        assert loc.name == "London"

    def test_country_code_optional(self):
        loc = ArticleLocationSchema(
            wikidata_qid="Q2",
            name="Earth",
            location_type="planet",
            latitude=0.0,
            longitude=0.0,
        )
        assert loc.country_code is None


class TestStoryPersonSchema:
    def test_minimal_person(self):
        person = StoryPersonSchema(wikidata_qid="Q1", name="Test Person")
        assert person.description is None
        assert person.nationalities is None
        assert person.image_url is None

    def test_full_person(self):
        person = StoryPersonSchema(
            wikidata_qid="Q1",
            name="Test Person",
            description="A person",
            nationalities=["British", "American"],
            image_url="https://img.com/person.jpg",
        )
        assert len(person.nationalities) == 2


class TestNewsStoryArticle:
    def test_image_url_optional(self):
        article = NewsStoryArticle(
            article_id="a1",
            headline="Test",
            source="BBC",
            url="https://bbc.co.uk/1",
        )
        assert article.image_url is None


class TestNewsStory:
    def test_valid_story(self):
        story = NewsStory(
            story_id="s1",
            title="Title",
            summary="Summary",
            key_points=["p1"],
            story_period=datetime(2025, 1, 1),
            generated_at=datetime(2025, 1, 1),
            updated_at=datetime(2025, 1, 1),
            articles=[],
        )
        assert story.topics == []
        assert story.locations == []
        assert story.persons == []

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            NewsStory(
                story_id="s1",
                title="Title",
                # missing summary
                key_points=[],
                story_period=datetime(2025, 1, 1),
                generated_at=datetime(2025, 1, 1),
                updated_at=datetime(2025, 1, 1),
                articles=[],
            )


class TestNewsStoryWithRelated:
    def test_inherits_from_news_story(self):
        story = NewsStoryWithRelated(
            story_id="s1",
            title="Title",
            summary="Summary",
            key_points=[],
            story_period=datetime(2025, 1, 1),
            generated_at=datetime(2025, 1, 1),
            updated_at=datetime(2025, 1, 1),
            articles=[],
        )
        assert story.related_stories == []

    def test_with_related_stories(self):
        related = RelatedStorySchema(
            story_id="r1",
            title="Related",
            summary="Summary",
            story_period=datetime(2025, 1, 1),
            updated_at=datetime(2025, 1, 1),
        )
        story = NewsStoryWithRelated(
            story_id="s1",
            title="Title",
            summary="Summary",
            key_points=[],
            story_period=datetime(2025, 1, 1),
            generated_at=datetime(2025, 1, 1),
            updated_at=datetime(2025, 1, 1),
            articles=[],
            related_stories=[related],
        )
        assert len(story.related_stories) == 1


class TestStoryCard:
    def test_valid_card(self):
        card = StoryCard(
            story_id="s1",
            title="Title",
            article_count=5,
            sources_count=3,
            story_period="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )
        assert card.image_url is None
        assert card.topics == []


class TestLandingSchemas:
    def test_landing_story(self):
        story = LandingStory(story_id="s1", title="Title")
        assert story.locations == []

    def test_region_top_stories(self):
        region = RegionTopStories(region="europe", stories=[])
        assert region.stories == []
