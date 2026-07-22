# Suot API

Suot API is a backend engineering project for building a fashion inventory and recommendation system.

The goal of this project is to deeply understand backend API development, including REST design, service-layer architecture, database persistence, automated testing, application configuration, authentication, and recommendation logic.

## Tech Stack

- Python
- FastAPI
- Pydantic
- pydantic-settings
- SQLAlchemy
- SQLite
- PostgreSQL
- Docker
- uv
- pytest
- ruff

## Current Features

- Health check endpoint
- Item CRUD endpoints
- SQLite persistence with SQLAlchemy
- Pydantic request and response schemas
- Service-layer architecture
- Environment-based database configuration
- Local `.env.example` configuration template
- Automated API tests with pytest
- Isolated test database
- FastAPI Swagger/OpenAPI documentation

## API Endpoints

### Health

```http
GET /health
```

### Items

```http
GET /items
POST /items
GET /items/{item_id}
PUT /items/{item_id}
DELETE /items/{item_id}
```

## Architecture

```txt
Client
  ↓
Router
  ↓
Schema validation
  ↓
Service layer
  ↓
SQLAlchemy Session
  ↓
Database
```

The application currently supports SQLite for local development and is being prepared for PostgreSQL.

The database connection is controlled through `DATABASE_URL`, which allows the app to use different databases in different environments without rewriting router or service logic.

```txt
Local development → SQLite
Testing           → test.db
PostgreSQL setup  → Docker + PostgreSQL
```

## Project Structure

```txt
app/
├── main.py
├── config.py
├── database.py
├── routers/
├── schemas/
├── services/
└── models/

tests/
└── test_items.py

.env.example
docker-compose.yml
pyproject.toml
README.md
DEVLOG.md
```

## Running Locally

Install dependencies:

```bash
uv sync
```

Create a local `.env` file:

```env
DATABASE_URL=sqlite:///./suot.db
```

Run the development server:

```bash
uv run uvicorn app.main:app --reload
```

Open the API docs:

```txt
http://127.0.0.1:8000/docs
```

Run tests:

```bash
uv run pytest
```

## Local PostgreSQL Setup

PostgreSQL is planned as the next database backend.

The app is being prepared so the database can be switched through configuration instead of changing application logic.

Future PostgreSQL connection format:

```env
DATABASE_URL=postgresql+psycopg://suot:suot@localhost:5432/suot
```

Docker will be used to run PostgreSQL locally.

```bash
docker compose up -d
docker compose ps
```

## Roadmap

- Phase 1: In-memory item CRUD — DONE
- Phase 2: SQLite persistence with SQLAlchemy — DONE
- Phase 3: Code review, cleanup, and item CRUD tests — DONE
- Phase 4A: Environment-based app configuration — DONE
- Phase 4B: Local PostgreSQL setup with Docker — WIP
- Phase 5: Alembic migrations
- Phase 6: Authentication
- Phase 7: User-owned inventory
- Phase 8: Recommendation logic
- Phase 9: Dockerize the application
- Phase 10: Deployment

## Learning Goals

This project is being built as a personal passion project and backend engineering learning system.

The goal is not only to ship features, but to understand every layer of the backend well enough to explain the architecture, design decisions, and implementation clearly to future employers.

Important concepts being practiced include:

```txt
HTTP requests
REST endpoints
Pydantic schemas
router/service separation
SQLAlchemy sessions
database persistence
test isolation
environment configuration
local infrastructure with Docker
```