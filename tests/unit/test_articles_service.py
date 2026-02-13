from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.schemas.enums import FilterPeriod
from app.services.news.articles_service import get_article, list_articles


def _make_article(
    id="art1",
    source="BBC",
    title="Test Article",
    summary="A summary",
    url="https://bbc.co.uk/article/1",
    published_at=None,
    ingested_at=None,
):
    return SimpleNamespace(
        id=id,
        source=source,
        title=title,
        summary=summary,
        url=url,
        published_at=published_at or datetime(2025, 7, 15, 10, 0),
        ingested_at=ingested_at or datetime(2025, 7, 15, 10, 5),
    )


QUERIES = "app.services.news.articles_service"


class TestListArticles:
    @patch(f"{QUERIES}.query_article_locations", return_value={})
    @patch(f"{QUERIES}.query_articles", return_value=[])
    def test_returns_empty_list(self, *_):
        result = list_articles(MagicMock(), FilterPeriod.today)
        assert result == []

    @patch(f"{QUERIES}.query_article_locations")
    @patch(f"{QUERIES}.query_articles")
    def test_assembles_article_with_locations(self, mock_articles, mock_locations):
        mock_articles.return_value = [_make_article()]
        mock_locations.return_value = {
            "art1": [
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

        result = list_articles(MagicMock(), FilterPeriod.today)

        assert len(result) == 1
        assert result[0].id == "art1"
        assert len(result[0].locations) == 1
        assert result[0].locations[0].name == "London"

    @patch(f"{QUERIES}.query_article_locations", return_value={})
    @patch(f"{QUERIES}.query_articles")
    def test_article_without_locations(self, mock_articles, _):
        mock_articles.return_value = [_make_article()]

        result = list_articles(MagicMock(), FilterPeriod.today)

        assert len(result) == 1
        assert result[0].locations == []


class TestGetArticle:
    @patch(f"{QUERIES}.query_article_by_id", return_value=None)
    def test_returns_none_for_missing(self, _):
        result = get_article(MagicMock(), "nonexistent")
        assert result is None

    @patch(f"{QUERIES}.query_article_locations", return_value={})
    @patch(f"{QUERIES}.query_article_by_id")
    def test_returns_article(self, mock_by_id, _):
        mock_by_id.return_value = _make_article()

        result = get_article(MagicMock(), "art1")

        assert result is not None
        assert result.id == "art1"
        assert result.source == "BBC"
