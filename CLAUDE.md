# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI REST API for accessing Context News data from a PostgreSQL/PostGIS database. Serves a news aggregation frontend with stories, articles, analytics, and source metadata.

## Commands

```bash
poetry install                                # Install dependencies
poetry run uvicorn app.main:app --reload      # Run dev server (port 8000)
docker build -t context-api .                 # Build Docker image
poetry run ruff check .                       # Lint
poetry run ruff format .                      # Format
poetry run mypy app                           # Type check
poetry run pytest tests/unit -v               # Run unit tests
poetry run pre-commit install                 # Install pre-commit hooks (once)
```

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

## CI/CD

- **Pre-commit hooks:** Ruff check (with auto-fix) and Ruff format run on every commit via `.pre-commit-config.yaml`.
- **GitHub Actions CI** (`.github/workflows/ci.yml`): Runs ruff check, ruff format, mypy, and pytest on every push and PR. Merging to `main` is blocked unless CI passes.
- **ECS Deploy** (`.github/workflows/ecs-deploy.yml`): Builds a Docker image and deploys to AWS ECS in `eu-west-2` on push to `main`.

## SQLAdmin Routing — Confirmed Findings

`/api/admin/db` is the SQLAdmin interface in production. SQLAdmin is mounted at `base_url="/admin/db"` (without `/api/`).

**How root_path works:** `FastAPI(root_path="/api")` causes Starlette to strip `/api` from incoming paths before route matching, but does NOT modify `scope["path"]` — so `scope["path"]` still reports the full raw path including `/api/`. This is confirmed by the route dump: all routes appear without `/api/` prefix (`/admin/status`, `/news/stories`, etc.) yet they work in production at `/api/admin/status`, `/api/news/stories` etc.

**Consequence:** SQLAdmin must be at `base_url="/admin/db"`. Using `base_url="/api/admin/db"` would cause it to expect paths of `/api/api/admin/db` → 404.

**Do not change `base_url` to `/api/admin/db`.** This was tried and confirmed broken. The `scope["path"] = "/api/debug-path"` debug result was initially misread as evidence for keeping `/api/` in the mount path — it actually shows the raw unstripped path that `scope["path"]` always reports, while Starlette strips `root_path` internally for matching only.

**If SQLAdmin 404s after deploy, check:**
- ECS logs for `ADMIN NOT MOUNTED` — means `ADMIN_USERNAME`, `ADMIN_PASSWORD`, or `ADMIN_SECRET_KEY` are missing from the ECS task definition.
- CloudFront custom error responses intercepting non-200 origin responses and serving the SPA instead.
