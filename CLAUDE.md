# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI REST API for accessing Context News data from a PostgreSQL/PostGIS database. Serves a news aggregation frontend with stories, articles, analytics, and source metadata.

## Commands

```bash
poetry install                                # Install dependencies
poetry run uvicorn app.main:app --reload      # Run dev server (port 8000)
docker build -t context-api .                 # Build Docker image
```

No test suite or linter is configured.

## Architecture

**Layered pattern:** Routes → Services → Queries, with Pydantic schemas for validation.

- `app/routes/` — FastAPI endpoint handlers. Grouped under `/admin` and `/news` prefixes.
- `app/services/` — Business logic. Orchestrates queries, assembles response objects, handles async OG image fetching.
- `app/queries/` — Raw SQLAlchemy database queries. Each function returns DB rows or dicts keyed by entity ID.
- `app/schemas/` — Pydantic response models and filter enums (`FilterPeriod`, `FilterRegion`, `FilterTopic`).

**Database models** come from an external package: `context-data-schema` (installed from `github.com/ContextNews/context-data-schemas`). Models are imported as `from rds_postgres.models import Story, Article, ...` and the session factory is `rds_postgres.connection.get_session()`.

**Database session** is provided via FastAPI dependency injection through `app/db.py:get_db()`, which loads `.env` via dotenv before importing the session factory.

## Key Patterns

- **Batch fetching:** Services query related data (articles, locations, persons, topics) in bulk using `IN` clauses on story/article IDs, then assemble into per-entity dicts. Follow this pattern for new endpoints.
- **Async image fetching:** `app/services/utils/image_fetcher.py` uses httpx to fetch OG images concurrently with a 1-hour in-memory cache.
- **Regional filtering:** `app/queries/news/stories_queries.py` contains `REGION_COUNTRY_CODES`, a hardcoded mapping of ISO 3166-1 alpha-3 codes to regions, used for geographic query filtering via PostGIS joins.
- **Related stories:** Uses a recursive CTE on the `story_stories` table to traverse the full graph of connected stories.
- **Date ranges:** `app/services/utils/date_utils.py` converts `FilterPeriod` enums (today/week/month) or explicit from/to dates into datetime ranges.

## API Structure

All routes are mounted under `root_path="/api"`. Two top-level groups:

- `/admin/status/` — Health checks and status badges
- `/news/stories/`, `/news/articles/`, `/news/analytics/`, `/news/sources/` — News data

Common query params across news endpoints: `period`, `region`, `topic`, `from_date`, `to_date`, `limit`. Analytics endpoints also support `interval` (hourly/daily).

## Deployment

GitHub Actions (`.github/workflows/ecs-deploy.yml`) builds a Docker image and deploys to AWS ECS in `eu-west-2` on push to `main`.
