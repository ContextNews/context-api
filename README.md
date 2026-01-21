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

## Endpoints

- `GET /articles`
- `GET /articles/{article_id}`
- `GET /article-clusters`
- `GET /article-clusters?include_article_ids=true`
- `GET /stories`
- `GET /sources_data`
- `GET /health`

### Response shapes

`GET /articles` returns a list of articles:

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
    "text": "string or null"
  }
]
```

`GET /articles/{article_id}` returns a single article:

```json
{
  "id": "string",
  "source": "string",
  "title": "string",
  "summary": "string",
  "url": "string",
  "published_at": "2024-01-01T12:00:00Z",
  "ingested_at": "2024-01-01T12:05:00Z",
  "text": "string or null"
}
```

`GET /article-clusters` returns a list of clusters:

```json
[
  {
    "article_cluster_id": "string",
    "clustered_at": "2024-01-01T12:00:00Z"
  }
]
```

`GET /article-clusters?include_article_ids=true` returns clusters with article IDs:

```json
[
  {
    "article_cluster_id": "string",
    "clustered_at": "2024-01-01T12:00:00Z",
    "article_ids": ["string"]
  }
]
```

`GET /health`:

```json
{
  "status": "ok"
}
```

`GET /stories` returns a list of stories:

```json
[
  {
    "story_id": "47cb5ca6",
    "title": "Sparklers held near ceiling started Swiss ski resort fire, investigators believe",
    "summary": "A fire at a Swiss ski resort is believed to have been started by sparklers...",
    "key_points": [
      "Fire started by sparklers held near ceiling",
      "Multiple teenagers missing after the incident"
    ],
    "primary_location": "Switzerland",
    "generated_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T14:00:00Z",
    "articles": [
      {
        "article_id": "e6489b58bc3e7fb4",
        "headline": "'Living a nightmare': Families of teens missing after ski resort fire desperate for news",
        "source": "bbc"
      }
    ],
    "sub_stories": [
      {
        "story_id": "sub_123",
        "title": "Investigation into fire cause"
      }
    ]
  }
]
```

`GET /sources_data` returns a list of sources:

```json
[
  {
    "source": "BBC",
    "name": "BBC News",
    "url": "https://feeds.bbci.co.uk/news/rss.xml",
    "bias": "center",
    "owner": "BBC",
    "state_media": true,
    "based": "UK"
  }
]
```
