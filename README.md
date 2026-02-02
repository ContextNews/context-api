# Context API

FastAPI service for accessing Context News RDS data.

## Setup

1. Install dependencies with Poetry:

```bash
poetry install
```

2. Set `DATABASE_URL` to your RDS connection string (use `.env` or export).

Example:

```bash
export DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/dbname"
```

## Run

```bash
poetry run uvicorn app.main:app --reload
```

## Docker

Build the image:

```bash
docker build -t context-api .
```

Run the container (pass your database URL as an env var):

```bash
docker run --rm -p 8000:8000 -e DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/dbname" context-api
```

## API Structure

The API is organized into two main sections:

- `/admin` - Administrative endpoints (status checks)
- `/news` - News data endpoints (stories, articles, analytics, sources)

### Common Query Parameters

Most `/news` endpoints support these filtering parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | enum | `today` | Time period filter: `today`, `week`, `month` |
| `region` | enum | none | Region filter: `north_america`, `south_america`, `europe`, `africa`, `middle_east`, `asia`, `oceania` |
| `from_date` | date | none | Custom start date (YYYY-MM-DD) |
| `to_date` | date | none | Custom end date (YYYY-MM-DD) |
| `limit` | int | none | Max results (1-100) |

## Endpoints

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/status/` | Health check |
| GET | `/admin/status/badge` | Status badge for shields.io |

### News - Stories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/news/stories/` | List stories with full details |
| GET | `/news/stories/news-feed` | Story cards for news feed UI |
| GET | `/news/stories/{story_id}` | Get a single story by ID |

### News - Articles

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/news/articles/` | List articles |
| GET | `/news/articles/{article_id}` | Get a single article by ID |

### News - Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/news/analytics/top-locations` | Top mentioned locations |
| GET | `/news/analytics/top-people` | Top mentioned people |
| GET | `/news/analytics/top-organizations` | Top mentioned organizations |

Analytics endpoints support an additional `interval` parameter:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `interval` | enum | none | Historical breakdown: `hourly`, `daily` |

When `interval` is provided, the response includes a `history` array with counts per time bucket.

### News - Sources

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/news/sources/` | List all news sources |

## Response Shapes

### `GET /admin/status/`

```json
{
  "status": "ok"
}
```

### `GET /admin/status/badge`

```json
{
  "schemaVersion": 1,
  "label": "api",
  "message": "healthy",
  "color": "brightgreen"
}
```

### `GET /news/articles/`

```json
[
  {
    "id": "string",
    "source": "string",
    "title": "string",
    "summary": "string",
    "url": "string",
    "published_at": "2024-01-01T12:00:00Z",
    "ingested_at": "2024-01-01T12:05:00Z",
    "locations": [
      {
        "wikidata_qid": "Q39",
        "name": "Switzerland",
        "location_type": "country",
        "country_code": "CHE",
        "latitude": 46.8182,
        "longitude": 8.2275
      }
    ]
  }
]
```

### `GET /news/stories/`

```json
[
  {
    "story_id": "47cb5ca6",
    "title": "Example story title",
    "summary": "A summary of the story...",
    "key_points": [
      "First key point",
      "Second key point"
    ],
    "locations": [
      {
        "wikidata_qid": "Q39",
        "name": "Switzerland",
        "location_type": "country",
        "country_code": "CHE",
        "latitude": 46.8182,
        "longitude": 8.2275
      }
    ],
    "story_period": "2024-01-01T00:00:00Z",
    "generated_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T14:00:00Z",
    "articles": [
      {
        "article_id": "e6489b58bc3e7fb4",
        "headline": "Article headline",
        "source": "bbc",
        "url": "https://www.bbc.com/news/articles/example",
        "image_url": "https://example.com/image.jpg"
      }
    ]
  }
]
```

### `GET /news/stories/news-feed`

```json
[
  {
    "story_id": "47cb5ca6",
    "title": "Example story title",
    "locations": [
      {
        "wikidata_qid": "Q39",
        "name": "Switzerland",
        "location_type": "country",
        "country_code": "CHE",
        "latitude": 46.8182,
        "longitude": 8.2275
      }
    ],
    "article_count": 5,
    "sources_count": 3,
    "story_period": "2024-01-01",
    "updated_at": "2024-01-01T14:00:00Z",
    "image_url": "https://example.com/image.jpg"
  }
]
```

### `GET /news/analytics/top-locations` (and other analytics endpoints)

Without `interval` parameter:

```json
[
  {
    "type": "gpe",
    "name": "United States",
    "count": 542
  }
]
```

With `interval=daily` parameter:

```json
[
  {
    "type": "gpe",
    "name": "United States",
    "count": 542,
    "history": [
      {"timestamp": "2024-01-01T00:00:00Z", "count": 72},
      {"timestamp": "2024-01-02T00:00:00Z", "count": 85},
      {"timestamp": "2024-01-03T00:00:00Z", "count": 68}
    ]
  }
]
```

### `GET /news/sources/`

```json
[
  {
    "source": "bbc",
    "name": "BBC News",
    "url": "https://feeds.bbci.co.uk/news/rss.xml",
    "bias": "center",
    "owner": "BBC",
    "state_media": true,
    "based": "UK"
  }
]
```
