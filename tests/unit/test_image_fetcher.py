import time
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.utils.image_fetcher import (
    _cache,
    fetch_og_image,
    fetch_og_images,
)


@pytest.fixture(autouse=True)
def clear_cache():
    _cache.clear()
    yield
    _cache.clear()


class TestFetchOgImage:
    @pytest.mark.asyncio
    async def test_extracts_og_image_property_first(self):
        html = '<html><head><meta property="og:image" content="https://img.com/photo.jpg"></head></html>'
        client = AsyncMock(spec=httpx.AsyncClient)
        response = MagicMock()
        response.text = html
        response.raise_for_status = MagicMock()
        client.get.return_value = response

        result = await fetch_og_image("https://example.com/article", client)
        assert result == "https://img.com/photo.jpg"

    @pytest.mark.asyncio
    async def test_extracts_og_image_content_first_order(self):
        html = '<html><head><meta content="https://img.com/alt.jpg" property="og:image"></head></html>'
        client = AsyncMock(spec=httpx.AsyncClient)
        response = MagicMock()
        response.text = html
        response.raise_for_status = MagicMock()
        client.get.return_value = response

        result = await fetch_og_image("https://example.com/article", client)
        assert result == "https://img.com/alt.jpg"

    @pytest.mark.asyncio
    async def test_returns_none_when_no_og_image(self):
        html = "<html><head><title>No image</title></head></html>"
        client = AsyncMock(spec=httpx.AsyncClient)
        response = MagicMock()
        response.text = html
        response.raise_for_status = MagicMock()
        client.get.return_value = response

        result = await fetch_og_image("https://example.com/article", client)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_http_error(self):
        client = AsyncMock(spec=httpx.AsyncClient)
        client.get.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=MagicMock()
        )

        result = await fetch_og_image("https://example.com/missing", client)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_connection_error(self):
        client = AsyncMock(spec=httpx.AsyncClient)
        client.get.side_effect = httpx.ConnectError("connection refused")

        result = await fetch_og_image("https://example.com/down", client)
        assert result is None

    @pytest.mark.asyncio
    async def test_uses_cache_on_second_call(self):
        html = '<meta property="og:image" content="https://img.com/cached.jpg">'
        client = AsyncMock(spec=httpx.AsyncClient)
        response = MagicMock()
        response.text = html
        response.raise_for_status = MagicMock()
        client.get.return_value = response

        url = "https://example.com/cached"
        await fetch_og_image(url, client)
        assert client.get.call_count == 1

        result = await fetch_og_image(url, client)
        assert result == "https://img.com/cached.jpg"
        assert client.get.call_count == 1  # not called again

    @pytest.mark.asyncio
    async def test_cache_expires_after_ttl(self):
        html = '<meta property="og:image" content="https://img.com/old.jpg">'
        client = AsyncMock(spec=httpx.AsyncClient)
        response = MagicMock()
        response.text = html
        response.raise_for_status = MagicMock()
        client.get.return_value = response

        url = "https://example.com/expiry"
        await fetch_og_image(url, client)

        # Expire the cache entry
        _cache[url] = (_cache[url][0], time.time() - 3601)

        await fetch_og_image(url, client)
        assert client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_caches_none_on_error(self):
        client = AsyncMock(spec=httpx.AsyncClient)
        client.get.side_effect = Exception("boom")

        url = "https://example.com/error"
        await fetch_og_image(url, client)
        assert url in _cache
        assert _cache[url][0] is None


class TestFetchOgImages:
    @pytest.mark.asyncio
    async def test_fetches_multiple_urls(self):
        html_a = '<meta property="og:image" content="https://img.com/a.jpg">'
        html_b = '<meta property="og:image" content="https://img.com/b.jpg">'

        responses = {
            "https://a.com": html_a,
            "https://b.com": html_b,
        }

        async def mock_get(url, **kwargs):
            resp = MagicMock()
            resp.text = responses[url]
            resp.raise_for_status = MagicMock()
            return resp

        with patch("app.services.utils.image_fetcher.httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_client.get = mock_get
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await fetch_og_images(["https://a.com", "https://b.com"])

        assert result == {
            "https://a.com": "https://img.com/a.jpg",
            "https://b.com": "https://img.com/b.jpg",
        }

    @pytest.mark.asyncio
    async def test_empty_urls_returns_empty_dict(self):
        result = await fetch_og_images([])
        assert result == {}
