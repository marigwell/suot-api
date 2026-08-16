# Suot API

Suot API is a backend engineering project for building a user-owned fashion inventory and recommendation system.

The project is designed as a practical backend learning system. It currently covers REST API design, layered architecture, PostgreSQL persistence, Docker, Alembic migrations, automated testing, authentication, row-level authorization, closet analytics, and item filtering.

Detailed documentation is split into:

- `DEVLOG.md` — day-by-day development history and completed milestones.
- `NOTES.md` — reusable backend concepts and the current understanding summary.

---

## Tech Stack

- Python
- FastAPI
- Pydantic
- pydantic-settings
- SQLAlchemy
- PostgreSQL
- SQLite for local and isolated test scenarios
- Alembic
- Docker and Docker Compose
- uv
- pytest
- Ruff
- Git and GitHub pull requests
- email-validator
- python-multipart
- PyJWT
- pwdlib with Argon2 password hashing

---

## Current Features

### API Foundation

- FastAPI application with automatic Swagger/OpenAPI documentation.
- Health check endpoint.
- Layered router, schema, service, model, and database structure.
- Environment-based configuration.
- PostgreSQL persistence through SQLAlchemy.
- Dockerized API and PostgreSQL services.
- Versioned database schema changes with Alembic.

### Authentication

- User registration.
- Email and username uniqueness validation.
- Argon2 password hashing.
- Safe user responses that exclude passwords and password hashes.
- OAuth2 password-form login.
- Signed JWT access tokens with expiration.
- Bearer token authentication.
- Protected `GET /auth/me` endpoint.

### User-Owned Inventory

- Authenticated item CRUD.
- Each item belongs to one user through `items.user_id`.
- Ownership is assigned from the authenticated user, not client input.
- Item list, detail, update, and delete operations are scoped to `current_user.id`.
- Cross-user authorization tests verify private inventory isolation.

### Richer Item Data

- Name.
- Brand.
- Category.
- Color.
- Size.
- Price stored precisely with `Numeric(10, 2)` and `Decimal`.
- Purchase date.
- Condition.
- Notes.

### Analytics and Filtering

- Protected closet analytics endpoint.
- Total item count.
- Total closet value.
- Item counts by category and brand.
- Most expensive item.
- Empty-closet analytics behavior.
- Basic item filtering by category, brand, and condition.
- Combined filters.
- Analytics and filters remain scoped to the current user.

### Testing

- Isolated test database.
- FastAPI dependency overrides.
- Registration, login, and `/auth/me` tests.
- Authenticated item CRUD tests.
- Cross-user authorization tests.
- Richer item field tests.
- Closet analytics tests.
- Basic and combined filtering tests.

---

## API Endpoints

### Health

```http
GET /health
```

### Authentication

```http
POST /auth/register
POST /auth/login
GET  /auth/me
```

### Items

```http
GET    /items
POST   /items
GET    /items/stats
GET    /items/{item_id}
PUT    /items/{item_id}
DELETE /items/{item_id}
```

All item endpoints require:

```http
Authorization: Bearer <access_token>
```

### Item Filters

```http
GET /items?category=Shirt
GET /items?brand=UNIQLO
GET /items?condition=new
GET /items?category=Shirt&brand=UNIQLO
```

---

## Authentication Examples

### Register

```http
POST /auth/register
Content-Type: application/json
```

```json
{
  "email": "jim@example.com",
  "username": "jim",
  "password": "password123"
}
```

Example response:

```json
{
  "id": 1,
  "email": "jim@example.com",
  "username": "jim",
  "is_active": true,
  "created_at": "2026-08-01T05:12:13.071212Z",
  "updated_at": "2026-08-01T05:12:13.071222Z"
}
```

The API never returns:

```txt
password
hashed_password
```

Duplicate emails or usernames return:

```http
409 Conflict
```

### Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

The OAuth2 form uses:

```txt
username → the user's email address
password → the user's password
```

Example response:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

Invalid credentials return `401 Unauthorized` without revealing whether the email exists.

### Current User

```http
GET /auth/me
Authorization: Bearer <access_token>
```

This route verifies the token, reads the user ID from its `sub` claim, and returns the authenticated user.

---

## Item Examples

### Create an Item

```http
POST /items
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "name": "New Balance 9060",
  "brand": "New Balance",
  "category": "Shoes",
  "color": "Grey",
  "size": "10",
  "price": "138.00",
  "purchase_date": "2026-08-10",
  "condition": "new",
  "notes": "Everyday sneakers"
}
```

The client does not send `user_id`. The backend assigns ownership from the verified access token:

```txt
JWT access token
  ↓
get_current_user()
  ↓
current_user.id
  ↓
item.user_id
```

Example response:

```json
{
  "id": 1,
  "user_id": 1,
  "name": "New Balance 9060",
  "brand": "New Balance",
  "category": "Shoes",
  "color": "Grey",
  "size": "10",
  "price": "138.00",
  "purchase_date": "2026-08-10",
  "condition": "new",
  "notes": "Everyday sneakers"
}
```

### List and Filter Items

```http
GET /items
GET /items?category=Shoes
GET /items?brand=New%20Balance
GET /items?condition=new
GET /items?category=Shoes&condition=new
```

The service always begins with the ownership condition and then adds optional filters:

```txt
user_id == current_user.id
AND optional category
AND optional brand
AND optional condition
```

### Closet Analytics

```http
GET /items/stats
Authorization: Bearer <access_token>
```

Example response:

```json
{
  "total_items": 3,
  "total_closet_value": "307.99",
  "category_counts": {
    "Shirt": 2,
    "Shoes": 1
  },
  "brand_counts": {
    "Saturn LA": 1,
    "UNIQLO": 1,
    "New Balance": 1
  },
  "most_expensive_item": {
    "id": 3,
    "name": "New Balance 9060",
    "brand": "New Balance",
    "price": "138.00"
  }
}
```

An empty closet returns zero values, empty count objects, and `null` for the most expensive item.

---

## Architecture

```txt
Client
  ↓
FastAPI router
  ↓
Pydantic validation
  ↓
Authentication dependency
  ↓
Service layer
  ↓
SQLAlchemy Session
  ↓
PostgreSQL
```

### Responsibilities

```txt
Router
  → HTTP paths and methods
  → request parameters and dependencies
  → status codes and exceptions

Schema
  → request and response validation

Service
  → database queries and application logic
  → ownership filtering
  → analytics calculations

Model
  → database table shape and relationships

Session
  → active database communication and transactions
```

Services receive `user_id` as a plain integer. They do not call FastAPI dependencies directly.

---

## Authentication and Authorization

```txt
Authentication
  → Who are you?
  → login, JWT, and get_current_user()

Authorization
  → What are you allowed to access?
  → owner-scoped item queries
```

The core item authorization rule is:

```txt
item.user_id == current_user.id
```

An authenticated user receives `404 Not Found` when an item is missing or inaccessible.

```txt
No valid token
  → 401 Not authenticated

Valid token but no accessible item
  → 404 Item not found
```

Returning `404` for another user's item avoids revealing whether that private resource exists.

---

## Database Design

### Users

```txt
users
├── id
├── email
├── username
├── hashed_password
├── is_active
├── created_at
└── updated_at
```

### Items

```txt
items
├── id
├── user_id
├── name
├── brand
├── category
├── color
├── size
├── price
├── purchase_date
├── condition
└── notes
```

Relationship:

```txt
users.id → items.user_id

One user can own many items.
Each item belongs to one user.
```

Suot uses one shared `items` table. Private inventories are created by scoping rows to the authenticated user's stable ID.

---

## Database Migrations

Alembic manages explicit, versioned database changes.

```txt
Change SQLAlchemy model
  ↓
Generate migration
  ↓
Review migration
  ↓
Apply migration
  ↓
PostgreSQL schema updates
```

Current migrations cover:

- Initial `items` table.
- Optional `brand` field.
- `users` table.
- User ownership on items.
- Richer item fields: `price`, `purchase_date`, `condition`, and `notes`.

Create a migration:

```bash
uv run alembic revision --autogenerate -m "migration message"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

---

## Project Structure

```txt
app/
├── main.py
├── config.py
├── database.py
├── security.py
├── routers/
│   ├── auth.py
│   ├── health.py
│   └── items.py
├── schemas/
│   ├── item.py
│   └── user.py
├── services/
│   ├── item_service.py
│   └── user_service.py
└── models/
    ├── item.py
    └── user.py

alembic/
└── versions/

tests/
├── test_auth.py
└── test_items.py

Dockerfile
.dockerignore
docker-compose.yml
.env.example
alembic.ini
pyproject.toml
README.md
DEVLOG.md
NOTES.md
uv.lock
```

---

## Configuration

Create a local `.env` file from `.env.example`.

Example:

```env
DATABASE_URL=postgresql+psycopg://suot:suot@localhost:5432/suot
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Important:

```txt
.env         → contains real local values; do not commit
.env.example → safe configuration template; commit this
```

Database hostname distinction:

```txt
localhost → API or Alembic running on the laptop
db        → API running inside Docker Compose
```

Use a strong secret supplied through secure environment configuration in production.

---

## Running Locally

Install dependencies:

```bash
uv sync
```

Start PostgreSQL through Docker:

```bash
docker compose up -d db
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Start the FastAPI development server:

```bash
uv run uvicorn app.main:app --reload
```

Open Swagger:

```txt
http://127.0.0.1:8000/docs
```

Run tests:

```bash
uv run pytest
```

Run formatting and lint checks:

```bash
uv run ruff check .
uv run ruff format --check .
```

---

## Running with Docker Compose

Build and start the API and database:

```bash
docker compose up --build
```

Check services:

```bash
docker compose ps
```

Open Swagger:

```txt
http://localhost:8000/docs
```

Stop services while keeping database data:

```bash
docker compose down
```

Delete the local PostgreSQL volume only when intentionally resetting the database:

```bash
docker compose down -v
```

---

## Swagger Authentication Flow

```txt
1. Register with POST /auth/register.
2. Click Authorize.
3. Enter the user's email in the username field.
4. Enter the user's password.
5. Leave client_id and client_secret blank.
6. Click Authorize.
7. Run GET /auth/me.
8. Use the protected item routes.
```

In the OAuth2 login form:

```txt
username     → the user's email
password     → the user's password
client_id    → leave blank
client_secret → leave blank
```

---

## Automated Testing

Run the complete suite with:

```bash
uv run pytest
```

The suite currently covers:

```txt
successful registration
duplicate email and username rejection
valid and invalid login
protected /auth/me behavior
authenticated item CRUD
missing item behavior
cross-user inventory isolation
richer item field persistence and updates
empty and populated closet analytics
analytics user isolation
category, brand, and condition filtering
combined item filters
```

Tests use a separate database and reset state between test cases.

---

## Git Workflow

```txt
sync main
  ↓
create a focused branch
  ↓
implement one feature
  ↓
format and test
  ↓
commit and push
  ↓
open and review pull request
  ↓
merge
  ↓
sync main again
```

Important rules:

```txt
Keep main stable.
Use branches for meaningful changes.
Review migrations before applying them.
Run tests before committing.
Do not commit .env, local databases, or Python cache files.
```

---

## Roadmap

### Chapter 1 — Backend Foundations

- Phase 1: In-memory item CRUD — DONE
- Phase 2: SQLite persistence with SQLAlchemy — DONE
- Phase 3: Cleanup and item CRUD tests — DONE
- Phase 4A: Environment-based configuration — DONE
- Phase 4B: PostgreSQL with Docker — DONE
- Phase 5: Dockerized FastAPI API — DONE
- Phase 6A: Alembic setup and initial migration — DONE
- Phase 6B: Schema evolution with `brand` — DONE

### Chapter 2 — Authentication and User-Owned Data

- Phase 7A: User model and users table — DONE
- Phase 7B: User registration — DONE
- Phase 7C: Login and JWT access tokens — DONE
- Phase 7D: Protected `/auth/me` route — DONE
- Phase 7E: Authentication tests — DONE
- Phase 8A: User-owned inventory — DONE
- Phase 8B: Cross-user authorization tests — DONE

### Chapter 3 — Product-Grade Inventory API

- Phase 9: Richer item fields — DONE
- Phase 10A: Closet analytics endpoint — DONE
- Phase 11A: Basic item filtering — DONE
- Phase 11B: Price range filters — NEXT
- Phase 11C: Sorting and pagination
- Phase 12: Validation and error-handling polish

### Chapter 4 — CI, Deployment, and Release Workflow

- GitHub Actions CI checks
- Production-ready configuration
- Initial deployment
- Deployment documentation and release checklist

### Chapter 5 — Intelligence and Personalization

- Rule-based wardrobe recommendations
- Outfit generation logic
- Wardrobe gap analysis
- Spending insights and duplicate-purchase warnings
- Recommendation feedback loop

### Future Production Work

- PostgreSQL integration tests
- Refresh tokens and account security
- Image uploads and object storage
- Search and indexing
- Rate limiting
- Structured logging and observability
- Redis caching
- Background jobs
- Performance testing

---

## Current Project Status

The current backend checkpoint includes:

```txt
FastAPI application structure
PostgreSQL persistence
Docker Compose runtime
Alembic migrations
automated tests
user registration and secure password storage
JWT login and current-user authentication
user-owned inventory
cross-user authorization isolation
richer item records
closet analytics
basic and combined item filters
```

Next planned backend work:

```http
GET /items?min_price=50
GET /items?max_price=150
GET /items?min_price=50&max_price=150
```

This will extend the same owner-scoped query design with numeric price comparisons.
