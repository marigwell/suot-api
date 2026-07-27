# Suot API

Suot API is a backend engineering project for building a fashion inventory and recommendation system.

The goal of this project is to deeply understand backend API development, including REST design, service-layer architecture, database persistence, automated testing, application configuration, Docker, PostgreSQL, authentication, and recommendation logic.

## Tech Stack

- Python
- FastAPI
- Pydantic
- pydantic-settings
- SQLAlchemy
- SQLite
- PostgreSQL
- Docker
- Docker Compose
- uv
- pytest
- ruff
- Git

## Current Features

- Health check endpoint
- Item CRUD endpoints
- SQLite persistence with SQLAlchemy
- PostgreSQL support
- Dockerized FastAPI API service
- Dockerized PostgreSQL database service
- Docker Compose setup for running API and database together
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
FastAPI API
  ↓
Router
  ↓
Schema validation
  ↓
Service layer
  ↓
SQLAlchemy Session
  ↓
PostgreSQL database
```

## Docker Architecture

The application can now run with Docker Compose.

```txt
Docker Compose
├── api
│   └── FastAPI app
│       └── runs on container port 8000
│
└── db
    └── PostgreSQL database
        └── stores item data
```

The API and database run as separate services.

```txt
Browser / Swagger
  ↓
localhost:8000
  ↓
api container
  ↓
db container
  ↓
PostgreSQL
```

This means Suot can now run locally as a containerized backend system.

## Database Configuration

The database connection is controlled through `DATABASE_URL`.

Local SQLite example:

```env
DATABASE_URL=sqlite:///./suot.db
```

Local FastAPI app connecting to Dockerized PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://suot:suot@localhost:5432/suot
```

Dockerized API connecting to Dockerized PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://suot:suot@db:5432/suot
```

Important distinction:

```txt
localhost → used when the API runs on the laptop
db        → used when the API runs inside Docker Compose
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

Dockerfile
.dockerignore
docker-compose.yml
.env.example
pyproject.toml
README.md
DEVLOG.md
```

## Running Locally Without Docker

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

## Running with Docker Compose

Start the API and PostgreSQL database:

```bash
docker compose up --build
```

Open the API docs:

```txt
http://localhost:8000/docs
```

Check running containers:

```bash
docker compose ps
```

Stop the containers:

```bash
docker compose down
```

## Testing

Local automated tests are run with:

```bash
uv run pytest
```

Current tests run locally and use an isolated test database.

```txt
pytest locally
  → tests CRUD behavior and route/service logic

Docker Compose manually
  → tests the containerized API and PostgreSQL runtime
```

The current automated test suite covers:

```txt
POST   /items
GET    /items
GET    /items/{item_id}
GET    /items/999
PUT    /items/{item_id}
PUT    /items/999
DELETE /items/{item_id}
DELETE /items/999
```

## Git Workflow

`main` should represent the stable working version of the project.

Feature branches should be used for meaningful backend, database, Docker, authentication, or infrastructure changes.

### Basic Workflow

```txt
branch → build → test → commit → merge → push
```

### Branch Sequence

Start from `main`:

```bash
git switch main
git pull
```

Create a feature branch:

```bash
git switch -c feature/example-name
```

Do the work on the feature branch.

Check the project:

```bash
git status
uv run pytest
docker compose ps
```

Commit the work:

```bash
git add .
git commit -m "clear human-readable message"
```

Push the branch:

```bash
git push -u origin feature/example-name
```

Merge after the feature works:

```bash
git switch main
git pull
git merge feature/example-name
git push
```

### Branch Naming

```txt
feature/postgres-setup
feature/dockerize-api
feature/auth
feature/user-inventory
feature/recommendations
fix/item-not-found
docs/update-devlog
test/item-service-tests
```

### Git Rules

```txt
Use main for stable checkpoints.
Use feature branches for meaningful changes.
Do not commit .env files.
Do not commit local database files.
Run tests before committing.
Test Docker changes with docker compose ps and Swagger.
Merge only after the feature works.
```

## Roadmap

- Phase 1: In-memory item CRUD — DONE
- Phase 2: SQLite persistence with SQLAlchemy — DONE
- Phase 3: Code review, cleanup, and item CRUD tests — DONE
- Phase 4A: Environment-based app configuration — DONE
- Phase 4B: Local PostgreSQL setup with Docker — DONE
- Phase 5: Dockerize the FastAPI API — DONE
- Phase 6: Alembic migrations
- Phase 7: Authentication
- Phase 8: User-owned inventory
- Phase 9: Recommendation logic
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
PostgreSQL
Docker images
Docker containers
Docker Compose services
Git branching
local infrastructure with Docker
```