from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.schemas.enums import FilterPeriod
from app.services.news.stories_service import get_story, get_story_feed, list_stories


_SENTINEL = object()


def _make_story(
    id="story1",
    title="Test Story",
    summary="A summary",
    key_points=_SENTINEL,
    story_period=None,
    generated_at=None,
    updated_at=None,
    parent_story_id=None,
):
    return SimpleNamespace(
        id=id,
        title=title,
        summary=summary,
        key_points=["point1"] if key_points is _SENTINEL else key_points,
        story_period=story_period or datetime(2025, 7, 15, 12, 0),
        generated_at=generated_at or datetime(2025, 7, 15, 12, 0),
        updated_at=updated_at or datetime(2025, 7, 15, 13, 0),
        parent_story_id=parent_story_id,
    )


def _make_article_row(story_id="story1", article_id="art1", title="Headline", source="BBC", url="https://bbc.co.uk/1"):
    return (story_id, article_id, title, source, url)


QUERIES = "app.services.news.stories_service"


class TestListStories:
    @pytest.mark.asyncio
    @patch(f"{QUERIES}.fetch_og_images", return_value={})
    @patch(f"{QUERIES}.query_story_topics", return_value={})
    @patch(f"{QUERIES}.query_story_persons", return_value={})
    @patch(f"{QUERIES}.query_story_locations", return_value={})
    @patch(f"{QUERIES}.query_story_articles", return_value=[])
    @patch(f"{QUERIES}.query_stories", return_value=[])
    async def test_returns_empty_list_when_no_stories(self, mock_stories, *_):
        result = await list_stories(MagicMock(), FilterPeriod.today)
        assert result == []

    @pytest.mark.asyncio
    @patch(f"{QUERIES}.fetch_og_images", return_value={"https://bbc.co.uk/1": "https://img.com/1.jpg"})
    @patch(f"{QUERIES}.query_story_topics", return_value={"story1": ["Politics"]})
    @patch(f"{QUERIES}.query_story_persons", return_value={})
    @patch(f"{QUERIES}.query_story_locations", return_value={})
    @patch(f"{QUERIES}.query_story_articles")
    @patch(f"{QUERIES}.query_stories")
    async def test_assembles_story_with_articles(self, mock_stories, mock_articles, *_):
        mock_stories.return_value = [_make_story()]
        mock_articles.return_value = [_make_article_row()]

        result = await list_stories(MagicMock(), FilterPeriod.today)

        assert len(result) == 1
        assert result[0].story_id == "story1"
        assert result[0].title == "Test Story"
        assert result[0].topics == ["Politics"]
        assert len(result[0].articles) == 1
        assert result[0].articles[0].image_url == "https://img.com/1.jpg"

    @pytest.mark.asyncio
    @patch(f"{QUERIES}.fetch_og_images", return_value={})
    @patch(f"{QUERIES}.query_story_topics", return_value={})
    @patch(f"{QUERIES}.query_story_persons", return_value={})
    @patch(f"{QUERIES}.query_story_locations", return_value={})
    @patch(f"{QUERIES}.query_story_articles", return_value=[])
    @patch(f"{QUERIES}.query_stories")
    async def test_null_key_points_becomes_empty_list(self, mock_stories, *_):
        mock_stories.return_value = [_make_story(key_points=None)]

        result = await list_stories(MagicMock(), FilterPeriod.today)
        assert result[0].key_points == []

    @pytest.mark.asyncio
    @patch(f"{QUERIES}.fetch_og_images", return_value={})
    @patch(f"{QUERIES}.query_story_topics", return_value={})
    @patch(f"{QUERIES}.query_story_persons", return_value={})
    @patch(f"{QUERIES}.query_story_locations")
    @patch(f"{QUERIES}.query_story_articles", return_value=[])
    @patch(f"{QUERIES}.query_stories")
    async def test_story_with_locations(self, mock_stories, mock_articles, mock_locations, *_):
        mock_stories.return_value = [_make_story()]
        mock_locations.return_value = {
            "story1": [
                {
                    "wikidata_qid": "Q84",
                    "name": "London",
                    "location_type": "city",
                    "country_code": "GBR",
                    "latitude": 51.5,
                    "longitude": -0.12,
                }
            ]
        }

        result = await list_stories(MagicMock(), FilterPeriod.today)
        assert len(result[0].locations) == 1
        assert result[0].locations[0].name == "London"


class TestGetStory:
    @pytest.mark.asyncio
    @patch(f"{QUERIES}.query_story_by_id", return_value=None)
    async def test_returns_none_for_missing_story(self, _):
        result = await get_story(MagicMock(), "nonexistent")
        assert result is None

    @pytest.mark.asyncio
    @patch(f"{QUERIES}.fetch_og_images", return_value={})
    @patch(f"{QUERIES}.query_related_stories", return_value=[])
    @patch(f"{QUERIES}.query_story_topics", return_value={"story1": ["Politics"]})
    @patch(f"{QUERIES}.query_story_persons", return_value={})
    @patch(f"{QUERIES}.query_story_locations", return_value={})
    @patch(f"{QUERIES}.query_story_articles")
    @patch(f"{QUERIES}.query_story_by_id")
    async def test_returns_story_with_related(self, mock_by_id, mock_articles, *_):
        mock_by_id.return_value = _make_story()
        mock_articles.return_value = [_make_article_row()]

        result = await get_story(MagicMock(), "story1")

        assert result is not None
        assert result.story_id == "story1"
        assert result.related_stories == []

    @pytest.mark.asyncio
    @patch(f"{QUERIES}.fetch_og_images", return_value={})
    @patch(f"{QUERIES}.query_related_stories")
    @patch(f"{QUERIES}.query_story_topics", return_value={})
    @patch(f"{QUERIES}.query_story_persons", return_value={})
    @patch(f"{QUERIES}.query_story_locations", return_value={})
    @patch(f"{QUERIES}.query_story_articles", return_value=[])
    @patch(f"{QUERIES}.query_story_by_id")
    async def test_related_stories_populated(self, mock_by_id, mock_articles, mock_locations, mock_persons, mock_topics, mock_related, *_):
        mock_by_id.return_value = _make_story()
        mock_related.return_value = [
            _make_story(id="related1", title="Related Story"),
        ]

        result = await get_story(MagicMock(), "story1")

        assert len(result.related_stories) == 1
        assert result.related_stories[0].story_id == "related1"

    @pytest.mark.asyncio
    @patch(f"{QUERIES}.fetch_og_images", return_value={})
    @patch(f"{QUERIES}.query_related_stories", side_effect=Exception("DB error"))
    @patch(f"{QUERIES}.query_story_topics", return_value={})
    @patch(f"{QUERIES}.query_story_persons", return_value={})
    @patch(f"{QUERIES}.query_story_locations", return_value={})
    @patch(f"{QUERIES}.query_story_articles", return_value=[])
    @patch(f"{QUERIES}.query_story_by_id")
    async def test_related_stories_error_returns_empty(self, mock_by_id, *_):
        mock_by_id.return_value = _make_story()

        result = await get_story(MagicMock(), "story1")

        assert result is not None
        assert result.related_stories == []


class TestGetStoryFeed:
    @pytest.mark.asyncio
    @patch(f"{QUERIES}.fetch_og_images", return_value={})
    @patch(f"{QUERIES}.query_story_topics", return_value={})
    @patch(f"{QUERIES}.query_story_persons", return_value={})
    @patch(f"{QUERIES}.query_story_locations", return_value={})
    @patch(f"{QUERIES}.query_story_articles", return_value=[])
    @patch(f"{QUERIES}.query_stories", return_value=[])
    async def test_returns_empty_when_no_stories(self, *_):
        result = await get_story_feed(MagicMock(), FilterPeriod.today)
        assert result == []

    @pytest.mark.asyncio
    @patch(f"{QUERIES}.fetch_og_images", return_value={"https://bbc.co.uk/1": "https://img.com/1.jpg", "https://cnn.com/1": None})
    @patch(f"{QUERIES}.query_story_topics", return_value={"story1": ["Politics"]})
    @patch(f"{QUERIES}.query_story_persons", return_value={})
    @patch(f"{QUERIES}.query_story_locations", return_value={})
    @patch(f"{QUERIES}.query_story_articles")
    @patch(f"{QUERIES}.query_stories")
    async def test_card_counts_articles_and_sources(self, mock_stories, mock_articles, *_):
        mock_stories.return_value = [_make_story()]
        mock_articles.return_value = [
            _make_article_row(source="BBC", url="https://bbc.co.uk/1"),
            _make_article_row(article_id="art2", source="CNN", url="https://cnn.com/1"),
        ]

        result = await get_story_feed(MagicMock(), FilterPeriod.today)

        assert len(result) == 1
        assert result[0].article_count == 2
        assert result[0].sources_count == 2
        assert result[0].image_url == "https://img.com/1.jpg"
