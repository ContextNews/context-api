from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.schemas.enums import FilterPeriod, FilterRegion
from app.services.landing.top_stories_service import get_top_stories_by_region

QUERIES = "app.services.landing.top_stories_service"


def _make_story(id="story1", title="Test Story"):
    return SimpleNamespace(
        id=id,
        title=title,
        summary="A summary",
        key_points=["point1"],
        story_period=datetime(2025, 7, 15, 12, 0),
        generated_at=datetime(2025, 7, 15, 12, 0),
        updated_at=datetime(2025, 7, 15, 13, 0),
    )


class TestGetTopStoriesByRegion:
    @pytest.mark.asyncio
    @patch(f"{QUERIES}.query_story_locations", return_value={})
    @patch(f"{QUERIES}.query_stories", return_value=[])
    async def test_returns_all_regions_even_when_empty(self, *_):
        result = await get_top_stories_by_region(MagicMock(), FilterPeriod.today)
        # When all regions return no stories, result is empty
        assert result == []

    @pytest.mark.asyncio
    @patch(f"{QUERIES}.query_story_locations", return_value={})
    @patch(f"{QUERIES}.query_stories")
    async def test_returns_stories_grouped_by_region(self, mock_stories, _):
        story = _make_story()

        def side_effect(db, start, end, region=None, limit=None, parent_only=True):
            if region == FilterRegion.europe:
                return [story]
            return []

        mock_stories.side_effect = side_effect

        result = await get_top_stories_by_region(MagicMock(), FilterPeriod.today)

        region_names = [r.region for r in result]
        assert "europe" in region_names

        europe = next(r for r in result if r.region == "europe")
        assert len(europe.stories) == 1
        assert europe.stories[0].story_id == "story1"

    @pytest.mark.asyncio
    @patch(f"{QUERIES}.query_story_locations")
    @patch(f"{QUERIES}.query_stories")
    async def test_batch_fetches_locations(self, mock_stories, mock_locations):
        story = _make_story()
        mock_stories.side_effect = lambda *a, region=None, **kw: (
            [story] if region == FilterRegion.asia else []
        )
        mock_locations.return_value = {
            "story1": [
                {
                    "wikidata_qid": "Q1490",
                    "name": "Tokyo",
                    "location_type": "city",
                    "country_code": "JPN",
                    "latitude": 35.68,
                    "longitude": 139.69,
                }
            ]
        }

        result = await get_top_stories_by_region(MagicMock(), FilterPeriod.today)

        asia = next(r for r in result if r.region == "asia")
        assert len(asia.stories[0].locations) == 1
        assert asia.stories[0].locations[0].name == "Tokyo"

        # Locations queried in a single batch call
        mock_locations.assert_called_once()
