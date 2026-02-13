from unittest.mock import MagicMock, patch

import pytest

from app.schemas.enums import FilterPeriod, FilterRegion, Interval
from app.services.news.analytics_service import (
    get_top_locations,
    get_top_organizations,
    get_top_people,
)

QUERIES = "app.services.news.analytics_service"


class TestGetTopLocations:
    @patch(f"{QUERIES}.query_top_entities", return_value=[])
    def test_calls_query_without_interval(self, mock_query):
        result = get_top_locations(MagicMock(), FilterPeriod.today)
        assert result == []
        mock_query.assert_called_once()
        assert mock_query.call_args.kwargs["entity_type"] == "gpe"

    @patch(f"{QUERIES}.query_top_entities_with_history", return_value=[])
    def test_calls_history_query_with_interval(self, mock_query):
        result = get_top_locations(MagicMock(), FilterPeriod.today, interval=Interval.hourly)
        assert result == []
        mock_query.assert_called_once()
        assert mock_query.call_args.kwargs["entity_type"] == "gpe"
        assert mock_query.call_args.kwargs["interval"] == Interval.hourly


class TestGetTopPeople:
    @patch(f"{QUERIES}.query_top_entities", return_value=[])
    def test_uses_person_entity_type(self, mock_query):
        get_top_people(MagicMock(), FilterPeriod.today)
        assert mock_query.call_args.kwargs["entity_type"] == "person"

    @patch(f"{QUERIES}.query_top_entities_with_history", return_value=[])
    def test_uses_person_entity_type_with_interval(self, mock_query):
        get_top_people(MagicMock(), FilterPeriod.week, interval=Interval.daily)
        assert mock_query.call_args.kwargs["entity_type"] == "person"


class TestGetTopOrganizations:
    @patch(f"{QUERIES}.query_top_entities", return_value=[])
    def test_uses_org_entity_type(self, mock_query):
        get_top_organizations(MagicMock(), FilterPeriod.today)
        assert mock_query.call_args.kwargs["entity_type"] == "org"

    @patch(f"{QUERIES}.query_top_entities", return_value=[])
    def test_passes_region_filter(self, mock_query):
        get_top_organizations(MagicMock(), FilterPeriod.today, region=FilterRegion.europe)
        assert mock_query.call_args.kwargs["region"] == FilterRegion.europe
