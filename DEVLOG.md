# Suot API Development Log

This file tracks the development progress, technical decisions, architecture changes, and lessons learned while building the Suot API.

---

## Day 1 — FastAPI Foundation

### Goal

Start the Suot API project and understand the basic structure of a FastAPI backend.

### Work Completed

- Created the initial FastAPI project.
- Added a health check endpoint with `GET /health`.
- Started designing the item inventory API.
- Created initial project folders for routers, schemas, services, and models.

### Concepts Learned

An API acts as the interface between clients and the application.

Routers handle HTTP requests and route them to the correct application logic.

A health check endpoint confirms that the API is running correctly.

### Endpoint Added

```http
GET /health
```

### Phase Status

Phase 1 started: FastAPI foundation created.

---

## Day 2 — In-Memory CRUD

### Goal

Build the first version of item CRUD using temporary in-memory storage.

### Work Completed

- Added item inventory endpoints.
- Implemented in-memory CRUD using a Python list.
- Added item lookup by ID.
- Added update and delete logic.
- Added `404` error handling.

### Endpoints Added

```http
GET    /items
POST   /items
GET    /items/{item_id}
PUT    /items/{item_id}
DELETE /items/{item_id}
```

### Concepts Learned

CRUD means:

```txt
Create → POST
Read   → GET
Update → PUT
Delete → DELETE
```

The first version stored items in memory:

```python
items = []
```

This was useful for learning request flow, but data disappeared whenever the server restarted.

### 404 Error Handling

If an item does not exist, the API returns:

```http
404 Not Found
```

This prevents an expected missing-resource case from becoming an internal server error.

### ID Design Decision

IDs should not be reused after deletion.

Reason:

```txt
IDs represent stable record identity.

If an old ID is reused, historical references such as
orders, favorites, logs, or audit records could accidentally
point to the wrong item.
```

### Phase Status

Phase 1 complete: in-memory item CRUD finished.

---

## Day 3 — ORM and Database Concepts

### Goal

Understand how HTTP requests become data stored in a SQL database and how that data can later be retrieved.

### What Is an ORM?

ORM means:

```txt
Object Relational Mapper
```

An ORM maps between programming-language objects and relational database tables.

It helps with both:

```txt
Python objects → database rows
database rows  → Python objects
```

Instead of writing raw SQL for every operation, the application can work with Python objects.

### SQLAlchemy

SQLAlchemy is the ORM used by Suot.

It allows the service layer to create, read, update, and delete database records using Python objects and query expressions.

### `db.add()` vs `db.commit()`

```python
db.add(item)
```

Stages a new object for insertion.

```python
db.commit()
```

Persists pending changes in the current transaction.

Important distinction:

```txt
db.add()    → stage the change
db.commit() → persist the change
```

### Phase Status

Database and ORM concepts introduced.

---

## Day 4 — SQLite Persistence

### Goal

Replace temporary in-memory storage with persistent storage so data survives server restarts.

### Work Completed

- Added SQLite database support.
- Added SQLAlchemy database infrastructure.
- Created the `items` table through `ItemModel`.
- Replaced in-memory item storage with database-backed CRUD.
- Added `.gitignore`.
- Switched route handlers from `async def` to `def` because the app currently uses synchronous SQLAlchemy.

### Old Storage

```python
items = []
```

Problem:

```txt
Restart server
  ↓
data disappears
```

### New Storage

```txt
SQLite database file
```

Result:

```txt
Restart server
  ↓
data survives
```

### Request Flow for Creating an Item

```txt
POST /items
  ↓
Router receives request
  ↓
FastAPI creates database session
  ↓
Service creates ItemModel
  ↓
SQLAlchemy inserts row
  ↓
db.commit() persists it
  ↓
db.refresh() loads generated values
  ↓
API returns JSON
```

### Architecture After Persistence

```txt
Client
  ↓
Router
  ↓
Pydantic schema validation
  ↓
Service layer
  ↓
SQLAlchemy Session
  ↓
SQLite
```

### Phase Status

Phase 2 complete: SQLite persistence with SQLAlchemy finished.

---

## Day 5 — API Testing with pytest

### Goal

Add automated tests so CRUD behavior can be verified without manually using Swagger UI every time.

### Work Completed

- Created a `tests/` directory outside `app/`.
- Added `tests/test_items.py`.
- Added pytest configuration.
- Fixed import-path issues.
- Added an isolated test database.
- Added tests for item CRUD.
- Confirmed the test suite runs with `uv run pytest`.

### Why Tests Matter

Before automated testing, endpoints had to be manually checked through Swagger.

Now pytest can verify API behavior repeatedly as the application changes.

### Test Database Isolation

Normal application:

```txt
get_db()
  ↓
development database
```

Tests:

```txt
get_db()
  ↓
test.db
```

This prevents automated tests from polluting development data.

### Dependency Override

```python
app.dependency_overrides[get_db] = override_get_db
```

Meaning:

```txt
Normal application
  → real database session

Tests
  → isolated test database session
```

### Database Reset

Before each test:

```python
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
```

Each test therefore starts with predictable database state.

### CRUD Tests Added

```txt
POST   /items       → create
GET    /items       → list
GET    /items/{id}  → retrieve
GET    /items/999   → missing-item 404
PUT    /items/{id}  → update
PUT    /items/999   → missing-item 404
DELETE /items/{id}  → delete
DELETE /items/999   → missing-item 404
```

### Phase Status

Phase 3 complete: item CRUD is covered by automated tests.

---

## Day 6 — Configuration, PostgreSQL, Docker, and Git Branching

### Goal

Move Suot closer to a production-style backend by separating configuration from application logic, introducing PostgreSQL, containerizing the application, and using feature branches.

### Work Completed

- Added `pydantic-settings`.
- Created `app/config.py`.
- Updated database setup to read `DATABASE_URL` from configuration.
- Added `.env.example`.
- Kept `.env` ignored by Git.
- Installed Docker.
- Created `docker-compose.yml`.
- Ran PostgreSQL inside Docker.
- Connected the local FastAPI application to PostgreSQL.
- Verified database contents with `psql`.
- Introduced feature branches for infrastructure work.
- Created a `Dockerfile`.
- Created `.dockerignore`.
- Updated Docker Compose to run both API and database services.
- Built and ran the FastAPI container.
- Confirmed Swagger and CRUD functionality through the Dockerized application.

### Why Configuration Matters

Instead of:

```txt
database URL hardcoded in application logic
```

Suot now follows:

```txt
Environment
  ↓
Configuration layer
  ↓
Database setup
  ↓
Application
```

This allows the same application to run in different environments.

```txt
Tests            → isolated SQLite
Local backend    → PostgreSQL
Docker Compose   → PostgreSQL service
Production       → hosted PostgreSQL
```

### PostgreSQL Architecture

SQLite:

```txt
FastAPI
  ↓
local database file
```

PostgreSQL:

```txt
FastAPI
  ↓
DATABASE_URL
  ↓
PostgreSQL server
```

The API and database are now independent processes.

### Local vs Docker Hostnames

Local API:

```env
DATABASE_URL=postgresql+psycopg://suot:suot@localhost:5432/suot
```

Dockerized API:

```env
DATABASE_URL=postgresql+psycopg://suot:suot@db:5432/suot
```

```txt
localhost → API runs on the host machine
db        → API runs inside Docker Compose
```

### Docker Concepts

```txt
image     → blueprint for containers
container → running image instance
volume    → persistent container data
network   → container communication
Compose   → coordinates multiple services
```

Suot:

```txt
Dockerfile
  → builds FastAPI image

api service
  → FastAPI

db service
  → PostgreSQL

postgres_data
  → persistent database volume
```

### Git Branching Lesson

```txt
main
  → stable code

feature branch
  → isolated feature development
```

Workflow:

```txt
branch
  ↓
build
  ↓
test
  ↓
commit
  ↓
PR / merge
```

### Phase Status

Phase 4 complete: PostgreSQL configuration established.

Phase 5 complete: FastAPI and PostgreSQL run together with Docker Compose.

---

## Day 7 — Alembic Migrations and Schema Evolution

### Goal

Replace automatic table creation with explicit, versioned database migrations.

### Work Completed

- Installed Alembic.
- Initialized Alembic.
- Added `alembic.ini` and the `alembic/` directory.
- Connected Alembic to `DATABASE_URL`.
- Connected Alembic to SQLAlchemy `Base.metadata`.
- Removed application-startup `Base.metadata.create_all()`.
- Generated and applied the initial `items` migration.
- Added optional `brand` to `ItemModel`.
- Updated schemas, services, and tests.
- Generated and applied a migration adding `brand`.
- Confirmed existing rows received `NULL`.
- Confirmed new rows could store brand values.
- Cleaned tracked Python cache files from Git.

### Why Alembic Was Added

Early approach:

```python
Base.metadata.create_all(bind=engine)
```

This creates missing tables but does not safely evolve existing schemas.

Mental model:

```txt
SQLAlchemy model
  → desired schema

PostgreSQL
  → real schema

Alembic migration
  → versioned transformation between schemas
```

### Migration Flow

```txt
Change model
  ↓
Generate migration
  ↓
Review migration
  ↓
Apply migration
  ↓
Database schema updates
```

Commands:

```bash
uv run alembic revision --autogenerate -m "migration message"
uv run alembic upgrade head
```

### `alembic_version`

Alembic stores the currently applied migration revision in:

```txt
alembic_version
```

### Schema Evolution

Items evolved from:

```txt
id
name
category
color
size
```

to:

```txt
id
name
brand
category
color
size
```

`brand` was nullable so old rows could survive the migration safely.

### Docker Volume Lesson

```txt
docker compose down
→ stop containers, keep data

docker compose down -v
→ stop containers, remove database volume
```

### Phase Status

Phase 6 complete: database schema evolution is managed by Alembic.

---

## Day 8 — User Model, Users Table, and Registration

### Goal

Build the foundation for authentication by introducing user accounts and secure password storage.

### Work Completed

- Created `UserModel`.
- Added email, username, password hash, active status, and timestamps.
- Created user request and response schemas.
- Installed `email-validator`.
- Updated Alembic metadata imports.
- Generated and applied the `users` migration.
- Installed Argon2 password hashing through `pwdlib`.
- Created `security.py`.
- Added password hashing and verification helpers.
- Created `user_service.py`.
- Added email and username lookup helpers.
- Added user creation.
- Created the auth router.
- Added `POST /auth/register`.
- Tested registration.
- Confirmed API responses never expose password fields.
- Added duplicate email and username tests.

### User Table

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

### Email vs Username

```txt
email
→ private login identity

username
→ public-facing identity
```

### Request vs Response Schemas

Registration needs:

```txt
email
username
password
```

Responses must not expose:

```txt
password
hashed_password
```

Important rule:

> Response schemas should not inherit secret fields from request schemas.

### Password Hashing

```txt
raw password
  ↓
Argon2
  ↓
password hash
  ↓
database
```

Raw passwords are never stored.

### Registration Flow

```txt
POST /auth/register
  ↓
validate request
  ↓
check duplicate email
  ↓
check duplicate username
  ↓
hash password
  ↓
create UserModel
  ↓
commit
  ↓
return safe user representation
```

Duplicate identity conflicts return:

```http
409 Conflict
```

### Phase Status

Phase 7A complete: user model and users table created.

Phase 7B complete: secure registration works.

---

## Day 9 — Login, JWT Access Tokens, and `/auth/me`

### Goal

Add login and allow protected routes to identify the authenticated user.

### Work Completed

- Installed PyJWT.
- Added JWT configuration.
- Added token response schema.
- Added JWT creation and decoding helpers.
- Added user authentication logic.
- Added lookup by user ID.
- Added `POST /auth/login`.
- Installed `python-multipart`.
- Added `OAuth2PasswordBearer`.
- Added reusable `get_current_user()`.
- Added protected `GET /auth/me`.
- Tested authentication through Swagger.
- Added tests for login and current-user behavior.

### Login Flow

```txt
POST /auth/login
  ↓
receive email + password
  ↓
find user
  ↓
verify password hash
  ↓
invalid → 401
valid   → create JWT
  ↓
return access token
```

The OAuth2 form's `username` field contains the user's email address.

### JWT Claims

```txt
sub → authenticated user's stable ID
exp → token expiration
```

Mental model:

```txt
Password
→ proves identity at login

JWT
→ represents authenticated identity afterward
```

### Protected Requests

```http
Authorization: Bearer <access_token>
```

### OAuth2 Helpers

```txt
OAuth2PasswordRequestForm
→ reads login form data

OAuth2PasswordBearer
→ extracts Bearer token from protected requests
```

### `get_current_user()`

```txt
Bearer token
  ↓
extract token
  ↓
decode + verify JWT
  ↓
read sub claim
  ↓
load user
  ↓
return UserModel
```

### Phase Status

Phase 7C complete: login and JWT issuance work.

Phase 7D complete: authenticated users can be resolved through `/auth/me`.

---

## Day 10 — User-Owned Items and Row-Level Authorization

### Goal

Upgrade inventory records from globally accessible items to private user-owned resources.

```txt
Authentication
→ Who are you?

Authorization
→ What are you allowed to access?
```

For Suot:

```txt
item.user_id == current_user.id
```

### Work Completed

- Added `user_id` to `ItemModel`.
- Added foreign key from `items.user_id` to `users.id`.
- Generated and applied ownership migration.
- Updated item responses to include `user_id`.
- Updated services to receive `user_id`.
- Assigned ownership using the authenticated user.
- Scoped list, detail, update, and delete operations to the authenticated user.
- Protected item endpoints with `get_current_user()`.
- Updated tests to authenticate before item operations.

### Relationship

```txt
users.id → items.user_id

One user owns many items.
Each item has one owner.
```

### Stable Ownership Identity

```txt
user_id
→ stable database identity

username
→ can potentially change
```

Database relationships therefore use IDs.

### Client Does Not Send Ownership

```txt
JWT
  ↓
get_current_user()
  ↓
current_user.id
  ↓
item.user_id
```

The client cannot choose another user's ID when creating an item.

### Owner-Scoped CRUD

```txt
GET /items
→ current user's items

GET /items/{id}
PUT /items/{id}
DELETE /items/{id}
→ match item ID AND user ID
```

### 401 vs 404

```txt
No valid authentication
→ 401

Authenticated, but no accessible item
→ 404
```

### Phase Status

Phase 8A complete: private user-owned inventory implemented.

---

## Day 11 — Cross-User Authorization Tests

### Goal

Prove through automated behavior that users cannot access one another's inventory.

### Work Completed

- Added helper for authenticating multiple users.
- Created items under User A.
- Attempted operations using User B.
- Tested list isolation.
- Tested detail isolation.
- Tested update isolation.
- Tested delete isolation.
- Confirmed inaccessible items return `404`.
- Confirmed the real owner remains able to manage the item.

### Why These Tests Matter

Authorization code can look correct while still containing security bugs.

Testing proves the actual API behavior.

```txt
User A authenticates
  ↓
User A creates item
  ↓
item.user_id = User A
  ↓
User B authenticates
  ↓
User B attempts access
  ↓
API does not expose or modify User A's item
```

### Query Mindset

Do not ask:

```txt
Does item 7 exist?
```

Ask:

```txt
Does item 7 exist for this authenticated user?
```

### Expected Behavior

```txt
User B lists items
→ User A's item absent

User B retrieves User A's item
→ 404

User B updates User A's item
→ 404

User B deletes User A's item
→ 404
```

### Phase Status

Phase 8B complete: automated tests prove cross-user inventory isolation.

---

## Day 12 — Richer Item Fields

### Goal

Expand basic clothing records into more useful wardrobe inventory records.

### Fields Added

```txt
price
purchase_date
condition
notes
```

### Work Completed

- Added richer fields to `ItemModel`.
- Used `Numeric(10, 2)` for price.
- Used SQL `Date` for purchase date.
- Used `String(50)` for condition.
- Used `Text` for notes.
- Generated and applied Alembic migration.
- Updated Pydantic schemas.
- Updated create and update services.
- Updated tests.

### Why These Fields Matter

```txt
price
→ closet value and spending analytics

purchase_date
→ purchase history and time-based analysis

condition
→ wardrobe maintenance and resale context

notes
→ flexible user context
```

### Money Design

Price maps to Python `Decimal`.

```txt
float
→ binary floating point

Decimal
→ precise decimal arithmetic
```

Money should use precise decimal representation.

### Optional Fields

The new fields were nullable because:

```txt
existing database rows did not contain them
+
users may not know every value
```

### Schema Evolution Flow

```txt
Model
  ↓
Alembic migration
  ↓
Database
  ↓
Pydantic schemas
  ↓
Service logic
  ↓
Tests
```

### Phase Status

Phase 9 complete: richer inventory records implemented.

---

## Day 13 — Closet Analytics Endpoint

### Goal

Add a protected endpoint that summarizes the authenticated user's closet.

### Endpoint Added

```http
GET /items/stats
Authorization: Bearer <access_token>
```

### Work Completed

- Added `MostExpensiveItem` schema.
- Added `ItemStats` schema.
- Added `get_item_stats()`.
- Added `/items/stats`.
- Added total item count.
- Added total closet value.
- Added category counts.
- Added brand counts.
- Added most-expensive-item calculation.
- Added empty-closet tests.
- Added populated-closet tests.
- Added user isolation tests.

### Example Response

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

### Empty Closet

```json
{
  "total_items": 0,
  "total_closet_value": "0.00",
  "category_counts": {},
  "brand_counts": {},
  "most_expensive_item": null
}
```

### Route Ordering Lesson

Specific routes must come before dynamic routes:

```txt
/items/stats
→ define first

/items/{item_id}
→ define afterward
```

Otherwise FastAPI can attempt to parse `"stats"` as an integer item ID.

### Initial Analytics Strategy

The first implementation loads the user's items and calculates analytics in Python.

This prioritizes:

```txt
clarity
testability
learning
```

A later optimization can use:

```txt
COUNT
SUM
GROUP BY
ORDER BY
LIMIT
```

directly in SQL.

### Phase Status

Phase 10A complete: protected closet analytics implemented.

---

## Day 14 — Basic Item Filtering

### Goal

Allow users to query a useful subset of their inventory instead of always retrieving every item.

### Supported Filters

```http
GET /items?category=Shirt
GET /items?brand=UNIQLO
GET /items?condition=new
GET /items?category=Shirt&brand=UNIQLO
```

### Work Completed

- Added optional `category`, `brand`, and `condition` query parameters.
- Updated router parameter handling.
- Passed filters from router to service.
- Added conditional SQLAlchemy filters.
- Added category filter tests.
- Added brand filter tests.
- Added condition filter tests.
- Added combined filter tests.
- Fixed a router/service parameter-flow bug.
- Corrected filtering logic that had accidentally been placed in detail lookup logic.

### Query Parameter Flow

```txt
GET /items?category=Shirt
  ↓
Router receives category
  ↓
Router passes category to service
  ↓
Service builds WHERE condition
  ↓
Database returns matching current-user rows
```

### Owner-Scoped Base Query

```python
statement = select(ItemModel).where(
    ItemModel.user_id == user_id
)
```

Then optional filters narrow that private result set.

```python
if category is not None:
    statement = statement.where(
        ItemModel.category == category
    )
```

### List vs Detail Responsibility

```txt
get_items()
→ collection query
→ optional filters

get_item_by_id()
→ single resource query
→ item_id + user_id
```

```txt
/items?category=Shirt
→ get_items()

/items/7
→ get_item_by_id()
```

### Combined Filtering

```http
GET /items?category=Shirt&brand=UNIQLO
```

means:

```txt
user_id == current_user.id
AND category == "Shirt"
AND brand == "UNIQLO"
```

### Authorization Rule

Filtering always applies inside the authenticated user's inventory.

It never means:

```txt
all matching items in the database
```

It means:

```txt
matching items owned by this user
```

### Phase Status

Phase 11A complete: basic item filtering implemented.

---

## Day 15 — Price Range Filters

### Goal

Extend `GET /items` so users can filter their inventory by item price.

Before this phase, users could filter by category, brand, and condition. After this phase, users can also filter by minimum price, maximum price, or a price range.

### Supported Filters

```http
GET /items?min_price=50
GET /items?max_price=150
GET /items?min_price=50&max_price=150
```

### Work Completed

- Added optional `min_price` and `max_price` query parameters.
- Updated the item router to receive price filter values.
- Updated `get_items()` to pass price filters into the SQLAlchemy query.
- Used `Decimal` for price query parameters.
- Added minimum price filtering.
- Added maximum price filtering.
- Added combined price range filtering.
- Added tests proving price filters still respect current-user ownership.

### Query Logic

```txt
min_price → ItemModel.price >= min_price
max_price → ItemModel.price <= max_price
```

Example:

```http
GET /items?min_price=50&max_price=150
```

means:

```txt
user_id == current_user.id
AND price >= 50
AND price <= 150
```

### Important Ownership Rule

Price filtering does not mean:

```txt
Find all items in the database between $50 and $150.
```

It means:

```txt
Find the current user's items between $50 and $150.
```

Ownership remains the first required condition.

### Phase Status

Phase 11B complete: `GET /items` now supports minimum price, maximum price, and price range filtering.

---

## Day 16 — Item Sorting

### Goal

Upgrade `GET /items` so users can control the order of returned inventory items.

Filtering decides which rows are returned.

Sorting decides what order those rows come back in.

### Supported Sorting

```http
GET /items?sort_by=name&sort_order=asc
GET /items?sort_by=price&sort_order=desc
GET /items?sort_by=purchase_date&sort_order=desc
```

Supported `sort_by` values:

```txt
name
price
purchase_date
```

Supported `sort_order` values:

```txt
asc
desc
```

### Work Completed

- Added optional `sort_by` query parameter.
- Added `sort_order` query parameter with a default of `asc`.
- Used `Literal` types in the router to validate allowed sort values.
- Added a service-level sort column mapping.
- Added ascending and descending sort behavior.
- Added tests for sorting by price, name, and purchase date.
- Added tests proving invalid sort values return `422 Unprocessable Entity`.

### Sorting Flow

```txt
GET /items?sort_by=price&sort_order=desc
  ↓
Router validates sort_by and sort_order
  ↓
Service maps sort_by to a model column
  ↓
Service applies .order_by()
  ↓
Database returns sorted current-user rows
```

### Query Order

The correct order is:

```txt
ownership
  ↓
filters
  ↓
sorting
```

Sorting should happen after filtering because the API should sort the matching current-user rows, not unrelated database rows.

### Phase Status

Phase 11C complete: `GET /items` now supports sorting by name, price, and purchase date.

---

## Day 17 — Item Pagination

### Goal

Add pagination to `GET /items` so the API does not return an unlimited number of item records at once.

Pagination makes list endpoints safer and more frontend-friendly.

### Supported Pagination

```http
GET /items?limit=20&offset=0
GET /items?limit=20&offset=20
```

### Work Completed

- Added `limit` query parameter.
- Added `offset` query parameter.
- Added validation so `limit` must be between `1` and `100`.
- Added validation so `offset` must be `0` or greater.
- Updated `get_items()` to apply `.limit()` and `.offset()`.
- Added tests for limiting returned items.
- Added tests for skipping items with offset.
- Added tests for invalid pagination values.
- Added a test proving pagination still respects current-user ownership.

### Pagination Meaning

```txt
limit  → how many rows to return
offset → how many rows to skip
```

Example:

```txt
Sorted full result:
0: Alpha Tee
1: Beta Jacket
2: Gamma Shirt

limit=2&offset=1:
skip Alpha Tee
return Beta Jacket and Gamma Shirt
```

### Query Order

Pagination should happen last:

```txt
ownership
  ↓
filters
  ↓
sorting
  ↓
pagination
```

This order matters because the API should paginate the final matching result set, not the entire database.

### Phase Status

Phase 11D complete: `GET /items` now supports validated offset-based pagination.

---

## Day 18 — Pagination Metadata and Analytics Regression Fix

### Goal

Make `GET /items` more useful for frontend development by returning pagination metadata instead of a raw item list.

Before this phase, `GET /items` returned:

```json
[
  {
    "id": 1,
    "name": "Alpha Tee"
  }
]
```

After this phase, `GET /items` returns:

```json
{
  "items": [
    {
      "id": 1,
      "name": "Alpha Tee"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0,
  "has_more": false
}
```

### Work Completed

- Added an `ItemPage` response schema.
- Updated `GET /items` to return an object with item results and metadata.
- Added `total`, `limit`, `offset`, and `has_more`.
- Added a `count_items()` service function.
- Added shared filter-building logic so item listing and item counting use the same ownership and filters.
- Updated list endpoint tests to read from `response.json()["items"]`.
- Added tests for pagination metadata.
- Added tests for both `has_more = true` and `has_more = false`.
- Fixed a potential analytics bug caused by reusing paginated item queries.
- Added a regression test proving closet analytics include more than the default page size.

### Pagination Metadata

```txt
items     → current page of item records
total     → total matching rows before pagination
limit     → requested page size
offset    → number of skipped rows
has_more  → whether another page exists
```

### `has_more` Logic

```python
has_more = offset + len(items) < total
```

Example with another page:

```txt
total = 2
offset = 0
len(items) = 1

0 + 1 < 2
has_more = true
```

Example on the last page:

```txt
total = 2
offset = 1
len(items) = 1

1 + 1 < 2
has_more = false
```

### Why `count_items()` Was Needed

The list endpoint now needs two related operations:

```txt
get_items()
  → returns the current page

count_items()
  → returns the total number of matching rows before pagination
```

Both operations must use the same ownership and filter conditions.

The count query should not use sorting, limit, or offset.

### Important Real-World Bug Fixed

After pagination, `get_items()` only returns one page of results by default:

```txt
limit=20
offset=0
```

That means analytics should not call:

```python
items = get_items(db, user_id)
```

because that would only analyze the first page of items.

Wrong behavior for a user with 25 items:

```json
{
  "total_items": 20,
  "total_closet_value": "20.00"
}
```

Correct behavior:

```json
{
  "total_items": 25,
  "total_closet_value": "25.00"
}
```

The fix was to make closet analytics query the full current-user item set instead of reusing the paginated list function.

### Core Lesson

A function that returns a page should not be reused when the caller needs the full dataset.

Different parts of the app need different query semantics:

```txt
Inventory page
  → one paginated page

Analytics dashboard
  → full current-user item set

Export
  → all matching rows

Recommendations
  → full closet or a specifically chosen subset
```

### Phase Status

Phase 11E complete: `GET /items` now returns pagination metadata, and closet analytics are protected from pagination-related undercounting.

---

## Day 19 — Deployment Hardening Design

### Goal

Prepare Suot for a public AWS deployment while limiting the risk of abusive traffic creating unexpected infrastructure costs.

### Problem Identified

A public cloud deployment introduces a cost model that does not exist during local development.

If public endpoints can receive unlimited requests, abusive or automated traffic could increase:

- application compute usage
- database activity
- network traffic
- logging volume
- future AI inference costs

### Design Decision

The initial AWS deployment was intentionally delayed until basic abuse and cost controls are designed and implemented.

The system should favor bounded resource usage over unrestricted automatic scaling during the early public release.

### Planned Controls

```txt
Application-level rate limiting
  → restrict excessive API requests

Per-user request limits
  → prevent one authenticated account from consuming excessive resources

Stricter write limits
  → protect registration, login, and mutation endpoints

AI quotas
  → required before a future wardrobe-assistant endpoint becomes public

Bounded ECS scaling
  → prevent traffic spikes from creating excessive compute capacity

AWS Budgets
  → alert on unexpected spending

Cost Anomaly Detection
  → detect unusual AWS usage

AWS WAF / edge protections
  → reduce abusive traffic before it reaches the application
```

### Tradeoff

```txt
Earlier deployment
  → faster public availability
  → greater exposure to uncontrolled usage

Deployment after hardening
  → slightly slower release
  → better cost predictability
  → stronger abuse resistance
```

Suot chose the second option.

### Why This Decision Matters

The original deployment plan focused mainly on getting the application online.

Before deployment, another requirement became clear:

```txt
Public traffic
  ↓
AWS resource consumption
  ↓
variable infrastructure cost
```

Without request controls, a user, bot, or abusive client could repeatedly call endpoints and consume resources.

The deployment design therefore changed from:

```txt
Build
  ↓
Deploy
  ↓
Add protections later
```

to:

```txt
Build
  ↓
Add abuse controls
  ↓
Add cloud cost controls
  ↓
Deploy
```

### Rate Limiting Strategy

Not every endpoint needs the same limits.

Sensitive or mutation-heavy endpoints should have stricter limits:

```http
POST /auth/register
POST /auth/login
POST /items
PUT /items/{item_id}
DELETE /items/{item_id}
```

Read endpoints can generally tolerate higher limits:

```http
GET /items
GET /items/stats
GET /items/{item_id}
```

Future AI endpoints will require the strictest controls because each request may trigger paid inference.

### Future AI Cost Controls

Before a wardrobe assistant becomes publicly available, it should include:

```txt
authenticated access
  +
per-user rate limiting
  +
daily request quotas
  +
server-side usage limits
```

The AI assistant should never allow unrestricted model calls directly from the client.

### Infrastructure Cost Controls

The first AWS deployment should intentionally limit how much infrastructure can scale.

Initial direction:

```txt
ECS Fargate
  → small task size
  → one running task initially
  → tightly bounded maximum task count

RDS PostgreSQL
  → small Single-AZ database

AWS Budgets
  → multiple early warning thresholds

Cost Anomaly Detection
  → identify unexpected usage patterns
```

For an early-stage application, degraded performance during abusive traffic is preferable to unlimited infrastructure scaling and an uncontrolled bill.

### Core Lesson

Cloud scalability is not automatically desirable.

Scaling infrastructure solves availability and performance problems, but it can also increase cost.

For Suot's initial public release:

```txt
controlled capacity
+
request limits
+
cost monitoring
```

is more appropriate than unrestricted scaling.

### Phase Status

Deployment hardening design complete.

Application-level rate limiting, per-user request controls, and AWS cost protections are planned before public deployment.

---

## Current Checkpoint

Suot API currently includes:

```txt
FastAPI application structure
database-backed CRUD
PostgreSQL persistence
Docker Compose runtime
Alembic migrations
automated tests
user registration
Argon2 password hashing
JWT authentication
current-user authentication
user-owned inventory
row-level authorization
cross-user isolation
richer item records
closet analytics
category filtering
brand filtering
condition filtering
price range filtering
sorting
pagination
pagination metadata
analytics protected from pagination bugs
CORS support for the Next.js frontend
```

The current product-grade item list endpoint supports:

```http
GET /items?category=Shirt&brand=UNIQLO&min_price=50&max_price=150&sort_by=price&sort_order=asc&limit=20&offset=0
```

The query behavior follows this order:

```txt
ownership
  ↓
filters
  ↓
sorting
  ↓
pagination
```

The response shape is:

```json
{
  "items": [],
  "total": 0,
  "limit": 20,
  "offset": 0,
  "has_more": false
}
```

Suot also now has a separate frontend application:

```txt
suot-api
  → FastAPI backend

suot-web
  → Next.js frontend
```

The frontend can currently:

```txt
register users
log in
receive and store JWT access tokens
make authenticated requests
load the current user's closet
create new items
automatically refresh the closet after item creation
```

### Current System

```txt
Browser
  ↓
Next.js / React / TypeScript
  ↓
HTTP + JSON + Bearer JWT
  ↓
FastAPI
  ↓
SQLAlchemy
  ↓
PostgreSQL
```

### Next Planned Backend Work

Before public AWS deployment:

```txt
application-level rate limiting
per-user request controls
production configuration review
AWS budget alerts
AWS cost anomaly detection
bounded ECS scaling
public-deployment security review
```

### Deployment Direction

```txt
Next.js frontend
  ↓
AWS-hosted frontend

FastAPI Docker image
  ↓
Amazon ECR
  ↓
Amazon ECS Fargate

PostgreSQL
  ↓
Amazon RDS

Logs
  ↓
Amazon CloudWatch
```

Public AWS deployment will happen after basic abuse and cost protections are implemented.