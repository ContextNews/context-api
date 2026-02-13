import asyncio
import re
import time

import httpx

_cache: dict[str, tuple[str | None, float]] = {}
_CACHE_TTL = 3600  # 1 hour


async def fetch_og_image(url: str, client: httpx.AsyncClient) -> str | None:
    """Fetch the og:image meta tag from a URL."""
    now = time.time()
    if url in _cache:
        cached_value, cached_at = _cache[url]
        if now - cached_at < _CACHE_TTL:
            return cached_value

    try:
        response = await client.get(url, timeout=5.0, follow_redirects=True)
        response.raise_for_status()
        html = response.text

        match = re.search(
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE,
        )
        if not match:
            match = re.search(
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
                html,
                re.IGNORECASE,
            )

        image_url = match.group(1) if match else None
        _cache[url] = (image_url, now)
        return image_url
    except Exception:
        _cache[url] = (None, now)
        return None


async def fetch_og_images(urls: list[str]) -> dict[str, str | None]:
    """Fetch og:image for multiple URLs in parallel."""
    async with httpx.AsyncClient() as client:
        tasks = [fetch_og_image(url, client) for url in urls]
        results = await asyncio.gather(*tasks)
    return dict(zip(urls, results, strict=False))
