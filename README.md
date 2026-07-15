# Suot API

Suot API is a backend engineering project for building a fashion inventory and recommendation system.

The goal of this project is to deeply understand backend API development, including REST design, service-layer architecture, database persistence, authentication, and recommendation logic.

## Tech Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- uv
- pytest
- ruff

## Current Features

- Health check endpoint
- Item CRUD endpoints
- SQLite persistence with SQLAlchemy
- Pydantic request and response schemas
- Service-layer architecture
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
SQLite database
```

## Project Structure

```txt
app/
├── main.py
├── database.py
├── routers/
├── schemas/
├── services/
└── models/
```

## Running Locally

Install dependencies:

```bash
uv sync
```

Run the development server:

```bash
uv run uvicorn app.main:app --reload
```

Open the API docs:

```txt
http://127.0.0.1:8000/docs
```

## Roadmap

- Phase 1: In-memory item CRUD - DONE
- Phase 2: SQLite persistence with SQLAlchemy - DONE
- Phase 3: Code review, cleanup, and tests - WIP
- Phase 4: PostgreSQL - WIP
- Phase 5: Alembic migrations
- Phase 6: Authentication
- Phase 7: User-owned inventory
- Phase 8: Recommendation logic
- Phase 9: Docker
- Phase 10: Deployment

## Learning Goals

This project is being built as a personal passion project and backend engineering learning system. The goal is not only to ship features, but to understand every layer of the backend well enough to explain the architecture, design decisions, and implementation clearly to future employers.