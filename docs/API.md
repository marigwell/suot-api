# Suot API

## Overview

Suot API is the backend for Suot, a personal wardrobe inventory app. It handles account registration, login, and managing each user's private collection of clothing items.

Built with FastAPI, SQLAlchemy, and PostgreSQL, it supports item filtering, sorting, pagination, and closet statistics. The project is a solo learning project for practicing backend development. A separate Next.js frontend communicates with the API over HTTP.

Jump to: [Local setup](#running-locally) · [Using the API](#using-the-api) · [Testing](#testing) · [Limitations](#current-limitations). For a request walkthrough, see [architecture and data flow](ARCHITECTURE.md).

## Running locally

You need Git, Python **3.14**, **uv**, and a running Docker engine with **Compose v2**. Run the commands below from the API repository.

### 1. Install dependencies

```shell
git clone https://github.com/marigwell/suot-api.git
cd suot-api
uv sync --locked
```

If you already have the repository, start with `uv sync --locked`.

### 2. Configure the environment

Generate a signing secret. The API uses this private value to sign and verify login tokens:

```shell
uv run python -c "import secrets; print(secrets.token_hex(32))"
```

Create or update `.env` in the repository root with these values, replacing the secret placeholder with the generated value:

```dotenv
DATABASE_URL=postgresql+psycopg://suot:suot@localhost:5432/suot
SECRET_KEY=replace-with-your-generated-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Also create `.env.docker` with the same values, changing the database hostname from `localhost` to `db`. Compose references this file even when starting only PostgreSQL. Keep both files out of Git.

The existing `.env.example` defaults to SQLite. Use the PostgreSQL URL above because the current database migrations (versioned table changes) do not fully support SQLite.

### 3. Start the database and API

```shell
docker compose up -d db
docker compose exec db pg_isready -U suot -d suot
```

Wait until `pg_isready` reports that PostgreSQL is accepting connections. Then apply the migrations to create the tables and start the API:

```shell
uv run python -m alembic upgrade head
uv run python -m uvicorn app.main:app --reload
```

Open [Swagger UI](http://localhost:8000/docs), the interactive API page, to try requests. [Health](http://localhost:8000/health) should return `{"status":"healthy","service":"Suot API","version":"0.1.0"}`. Health does not check the database; [registering an account](#authentication) verifies database access.

This setup runs Python on your computer and PostgreSQL in Docker. API startup does not run migrations automatically. Stop the API with Ctrl+C and containers with `docker compose down`; the database volume is retained.

## How it works

```text
Client → FastAPI router → service → SQLAlchemy → PostgreSQL
```

| Location | Purpose |
| --- | --- |
| [`app/routers/`](../app/routers/) | Receive requests, identify the signed-in user, and return responses or errors |
| [`app/schemas/`](../app/schemas/) | Define and validate request and response fields |
| [`app/services/`](../app/services/) | Query items, check ownership, save changes, and calculate statistics |
| [`app/models/`](../app/models/) | Define database tables and their rules |
| [`app/database.py`](../app/database.py) | Provide a session to manage each request's database work |
| [`app/security.py`](../app/security.py) | Hash passwords and create or verify signed login tokens (JWTs) |
| [`alembic/`](../alembic/) | Track and apply changes to database tables |

The database has `users` and `items` tables. Each item belongs to a user through `items.user_id`. The API takes ownership from the verified token and filters item queries by that user. Missing items and another user's items both return 404.

Prices use `Decimal` and `Numeric(10, 2)` storage and are returned as JSON strings.

For a request walkthrough and ownership details, see [API architecture and data flow](ARCHITECTURE.md).

## Using the API

Base URL: `http://localhost:8000`. Full request and response fields are available in [Swagger UI](http://localhost:8000/docs) and the machine-readable [OpenAPI JSON](http://localhost:8000/openapi.json).

### Authentication

**Register** with `POST /auth/register` and a JSON body:

```json
{
  "email": "demo@example.com",
  "username": "demo",
  "password": "local-demo-password"
}
```

Usernames must be 3–50 characters and passwords 8–128 characters. Passwords are hashed with Argon2; responses exclude password hashes.

**Log in** using `POST /auth/login` with form data (`application/x-www-form-urlencoded`). Send the **email address in the field named `username`**, plus `password`. The response contains `access_token` and `token_type`. The access token is your proof of login for protected requests.

**Try protected requests** in Swagger: click **Authorize**, enter the email and password, and leave the client fields blank. Swagger will attach the token to requests. When using another client, include this header:

```http
Authorization: Bearer <access_token>
```

Tokens expire after 30 minutes by default. Register your own local account; none are seeded.

### Endpoints

| Method | Path | Purpose | Success |
| --- | --- | --- | --- |
| GET | `/health` | Service status | 200 |
| POST | `/auth/register` | Create an account | 201, user |
| POST | `/auth/login` | Sign in | 200, token |
| GET | `/auth/me` | Current user; requires authentication | 200, user |
| GET | `/items` | List owned items | 200, page |
| POST | `/items` | Create an item | 200, item |
| GET | `/items/stats` | Closet statistics | 200, statistics |
| GET | `/items/{item_id}` | Read an item | 200, item |
| PUT | `/items/{item_id}` | Replace item fields | 200, item |
| DELETE | `/items/{item_id}` | Delete an item | 200, `true` |

All item endpoints require authentication. Common errors are 401 for authentication failures, 404 for inaccessible items, 409 for duplicate registration details, and 422 for invalid requests.

### Create or replace an item

Example JSON body for `POST /items`:

```json
{
  "name": "Everyday shirt",
  "category": "Shirt",
  "color": "White",
  "size": "M",
  "brand": "UNIQLO",
  "price": "29.90"
}
```

Name, category, color, and size are required. Brand, price, purchase date (`YYYY-MM-DD`), condition, and notes are optional. The response adds `id` and `user_id`; ownership is assigned by the server.

`PUT` uses the same body shape. Include all values you want to keep: omitted optional fields become null. This branch has no `PATCH` endpoint.

### Filter, sort, and page through items

Add these query parameters to `GET /items`:

| Query parameters | Behavior |
| --- | --- |
| `category`, `brand`, `condition` | Exact matches; items must meet every supplied filter |
| `min_price`, `max_price` | Minimum and maximum price, including the boundary values |
| `sort_by`, `sort_order` | Sort by `name`, `price`, or `purchase_date`; order is `asc` or `desc` |
| `limit`, `offset` | `limit`: page size 1–100 (default 20). `offset`: number of matching items to skip, at least 0 (default 0) |

For example, get the first ten shirts, cheapest first:

```http
GET /items?category=Shirt&sort_by=price&sort_order=asc&limit=10&offset=0
```

Lists return a page object. An empty response with default pagination looks like:

```json
{
  "items": [],
  "total": 0,
  "limit": 20,
  "offset": 0,
  "has_more": false
}
```

`total` counts all matching items, including those outside the current page. `has_more` tells you whether more matching items remain. For the next page, increase `offset` by `limit`.

### Closet statistics

`GET /items/stats` returns item count, total value, category/brand counts, and the most expensive item. It always uses the user's whole closet, regardless of list filters or pagination.

## Testing

Run these from the repository root after installing dependencies. The first command runs the tests; the other two check code quality and formatting:

```shell
uv run python -m pytest
uv run ruff check .
uv run ruff format --check .
```

Tests cover registration/login, item operations, ownership isolation, filtering, sorting, pagination, and statistics. They recreate tables in a separate `test.db` SQLite file before each test. Run them serially because the test modules share that file.

The suite does not test PostgreSQL migrations or the browser interface. PostgreSQL need not be running for these tests, but application imports still load the driver configured by `DATABASE_URL`.

## Current limitations

- No refresh tokens, logout/revocation endpoint, password reset or email verification. The stored `is_active` flag is not enforced.
- Item validation needs stricter length, non-empty, and price rules. Error handling and rate limiting need further work before public hosting.
- Lists have no default ordering or tie-breaker. Statistics load the user's items into memory.
- The ownership migration has no backfill for existing ownerless items. The setup above assumes a fresh database.
- The Dockerfile starts from Python 3.12 while the project requires 3.14, and it omits migration files. The documented setup therefore runs the API on the host.
- PostgreSQL integration tests and wardrobe recommendations are not implemented.
