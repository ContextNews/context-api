import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Set dummy DATABASE_URL before importing app — the connection is never used
# because we override get_db, but rds_postgres.connection reads it at import time.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")

from app.db import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.schemas.news import PaginatedStoryCards

FEED_PATH = "/news/stories/news-feed"
SERVICE = "app.routes.news.stories.get_story_feed_service"


def _override_get_db():
    yield MagicMock()


app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


def _empty_paginated(**overrides):
    defaults = {"stories": [], "offset": 0, "limit": 25, "has_more": False}
    defaults.update(overrides)
    return PaginatedStoryCards(**defaults)


class TestNewsFeedRoute:
    @patch(SERVICE, new_callable=AsyncMock)
    def test_default_params_returns_paginated_shape(self, mock_service):
        mock_service.return_value = _empty_paginated()

        response = client.get(FEED_PATH)

        assert response.status_code == 200
        body = response.json()
        assert "stories" in body
        assert "offset" in body
        assert "limit" in body
        assert "has_more" in body
        assert isinstance(body["stories"], list)

    @patch(SERVICE, new_callable=AsyncMock)
    def test_custom_pagination_params(self, mock_service):
        mock_service.return_value = _empty_paginated(offset=20, limit=10)

        response = client.get(f"{FEED_PATH}?limit=10&offset=20")

        assert response.status_code == 200
        mock_service.assert_called_once()
        call_kwargs = mock_service.call_args.kwargs
        assert call_kwargs["limit"] == 10
        assert call_kwargs["offset"] == 20

    def test_negative_offset_returns_422(self):
        response = client.get(f"{FEED_PATH}?offset=-1")
        assert response.status_code == 422

    @pytest.mark.parametrize("limit", [0, 101])
    def test_invalid_limit_returns_422(self, limit):
        response = client.get(f"{FEED_PATH}?limit={limit}")
        assert response.status_code == 422
