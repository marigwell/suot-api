# Suot API Core Notes

This file contains the reusable backend concepts, architecture notes, and current understanding developed while building Suot API through Day 14.

---

## Current Architecture

```txt
Client
  ↓
FastAPI router
  ↓
Pydantic request validation
  ↓
Authentication and current-user dependency
  ↓
Service layer
  ↓
SQLAlchemy Session
  ↓
PostgreSQL
```

Supporting systems:

```txt
pydantic-settings → environment configuration
Alembic           → versioned schema migrations
Docker Compose    → API and PostgreSQL services
pytest            → automated behavior verification
Ruff              → formatting and linting
```

---

## Layer Responsibilities

### Routers

Routers handle HTTP concerns:

```txt
paths and methods
request bodies
path and query parameters
dependencies
authentication
status codes
response models
HTTP exceptions
```

Routers should pass plain values, such as `current_user.id`, into the service layer.

### Pydantic Schemas

Schemas define API input and output shapes.

```txt
request schema  → what the client may send
response schema → what the API may return
```

Request schemas containing secrets should not be reused as response schemas.

### Services

Services handle database and application logic:

```txt
build SQLAlchemy queries
create model objects
apply ownership rules
update and delete rows
calculate analytics
return results to routers
```

Services should not call FastAPI's `Depends()` or import `get_current_user()`. They receive ordinary arguments such as `user_id: int`.

### SQLAlchemy Models

Models define how Python objects map to database tables.

```txt
ItemModel → items table
UserModel → users table
```

### Database Session

A SQLAlchemy `Session` is the application's active conversation with the database.

It can:

```txt
run queries
stage inserts
stage updates
stage deletes
commit transactions
rollback transactions
```

---

## Database Infrastructure

### `database.py`

`database.py` configures SQLAlchemy database infrastructure.

It creates:

```txt
engine
SessionLocal
Base
get_db()
```

It is responsible for the connection and sessions, not item or user business logic.

### `get_db()`

`get_db()` creates a session for one request and closes it when the request finishes.

```txt
Request starts
  ↓
get_db() creates session
  ↓
Router and service use session
  ↓
Request ends
  ↓
get_db() closes session
```

### `db.get()`

```python
db.get(ItemModel, item_id)
```

Finds one row by primary key. Owner-scoped item access requires an additional `user_id` condition, so Suot normally uses a `select()` statement for protected lookups.

### `select()`

```python
select(ItemModel)
```

Builds a query. Conditions can be added with `.where()`:

```python
select(ItemModel).where(
    ItemModel.id == item_id,
    ItemModel.user_id == user_id,
)
```

### `db.scalars()`

```python
list(db.scalars(statement).all())
```

This runs a `SELECT` statement, extracts model objects, and converts the result into a list.

### `db.add()`

```python
db.add(item)
```

Stages a new object for insertion. It does not permanently save the row until `db.commit()`.

### Field Assignment

```python
item.name = item_data.name
item.category = item_data.category
```

SQLAlchemy tracks changes made to loaded model objects. A later commit persists them.

### `db.delete()`

```python
db.delete(item)
```

Stages an already-loaded object for deletion.

### `db.commit()`

```python
db.commit()
```

Permanently saves pending inserts, updates, and deletes in the current transaction.

### `db.refresh()`

```python
db.refresh(item)
```

Reloads a model from the database. This is useful after creation because the database generates values such as `id`.

---

## Configuration and Environments

The database URL and authentication settings belong in configuration, not hardcoded throughout the app.

```txt
Environment variables
  ↓
pydantic-settings
  ↓
app configuration
  ↓
database and security setup
```

Important files:

```txt
.env         → real local values; never commit
.env.example → safe template; commit this
app/config.py → validated application settings
```

Database hosts differ by runtime:

```txt
API on laptop         → localhost
API in Docker Compose → db
```

---

## Docker Notes

```txt
image     → blueprint for a container
container → running instance of an image
volume    → persistent container data
network   → communication between containers
Compose   → multiple services managed together
```

Suot's Compose setup includes:

```txt
api service
  → FastAPI application

db service
  → PostgreSQL database

postgres_data volume
  → persistent database files
```

Volume distinction:

```txt
docker compose down
  → stop containers and keep data

docker compose down -v
  → stop containers and delete the database volume
```

---

## Alembic and Schema Evolution

SQLAlchemy models describe the desired table structure. Alembic migrations change the real database from one version to another.

```txt
Change model
  ↓
Generate migration
  ↓
Review migration
  ↓
Apply migration
  ↓
Database schema matches the new design
```

```bash
uv run alembic revision --autogenerate -m "migration message"
uv run alembic upgrade head
```

The `alembic_version` table records which migration revision the database has applied.

When adding a column to a table with existing rows, nullability and default values must be considered. Optional fields such as `brand`, `price`, `purchase_date`, `condition`, and `notes` allowed existing rows to survive schema changes safely.

---

## Current Database Models

### `UserModel`

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

```txt
email    → private login identifier
username → public/searchable identity
```

### `ItemModel`

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

Ownership relationship:

```txt
items.user_id → users.id

One user can own many items.
Each item belongs to one user.
```

### Money and `Decimal`

`price` uses SQLAlchemy `Numeric(10, 2)` and Python `Decimal`.

```txt
float   → binary floating-point; can introduce rounding errors
Decimal → precise base-10 arithmetic; appropriate for money
```

---

## Authentication

### Registration

```txt
POST /auth/register
  ↓
Validate email, username, and password
  ↓
Check duplicate email and username
  ↓
Hash password with Argon2
  ↓
Store hashed_password
  ↓
Return safe user response
```

Duplicate identity conflicts return `409 Conflict`.

The response excludes both `password` and `hashed_password`.

### `security.py`

Current low-level security helpers:

```txt
hash_password()
verify_password()
create_access_token()
decode_access_token()
```

Responsibilities:

```txt
password hashing
password verification
JWT creation
JWT decoding and validation
```

### Login

```txt
POST /auth/login
  ↓
Find user by email
  ↓
Verify raw password against stored hash
  ↓
Create signed JWT
  ↓
Return access_token and token_type
```

Invalid credentials return `401 Unauthorized` without revealing whether the email exists.

### JWT Claims

```txt
sub → subject; the user's stable ID
exp → expiration time
```

```txt
Password proves identity during login.
JWT represents authenticated identity on later requests.
```

### Bearer Token

Protected routes expect:

```http
Authorization: Bearer <access_token>
```

### OAuth2 Helpers

```txt
OAuth2PasswordRequestForm
  → receives username/password form data at login

OAuth2PasswordBearer
  → extracts the Bearer token from protected requests
```

For Suot, the OAuth2 form's `username` field contains the user's email.

### `get_current_user()`

```txt
Bearer token
  ↓
OAuth2PasswordBearer extracts token
  ↓
decode_access_token() verifies token
  ↓
payload["sub"] provides user ID
  ↓
get_user_by_id() loads user
  ↓
return current UserModel
```

### Authentication Endpoints

```http
POST /auth/register
POST /auth/login
GET  /auth/me
```

---

## Authentication vs Authorization

```txt
Authentication
  → Who are you?
  → solved with login, JWT, and get_current_user()

Authorization
  → What are you allowed to access?
  → solved by scoping item operations to current_user.id
```

Suot's core row-level authorization rule is:

```txt
item.user_id == current_user.id
```

The client never supplies item ownership. The backend derives it from the authenticated user:

```txt
JWT
  ↓
get_current_user()
  ↓
current_user.id
  ↓
item.user_id
```

### Why Inaccessible Items Return `404`

An item belonging to another user is treated as unavailable to the current user.

```txt
403 Forbidden → may reveal that the item exists
404 Not Found → no accessible item was found
```

Correct question:

```txt
Does this item exist for the current user?
```

### `401` vs `404`

```txt
Missing or invalid token
  → 401 Not authenticated

Valid token but no accessible matching item
  → 404 Item not found
```

### Cross-User Test Pattern

```txt
Authenticate User A
Authenticate User B
User A creates an item
User B attempts list/detail/update/delete operations
Assert User A's item is never exposed or modified
```

---

## Item Querying and Filtering

### Owner-Scoped Base Query

Every list query begins with ownership:

```python
statement = select(ItemModel).where(ItemModel.user_id == user_id)
```

Optional filters narrow that already-private result set:

```python
if category is not None:
    statement = statement.where(ItemModel.category == category)

if brand is not None:
    statement = statement.where(ItemModel.brand == brand)

if condition is not None:
    statement = statement.where(ItemModel.condition == condition)
```

### Router-to-Service Flow

```txt
URL query parameters
  ↓
Router function arguments
  ↓
Service function arguments
  ↓
SQLAlchemy WHERE conditions
  ↓
Filtered current-user rows
```

If the router receives a parameter but does not pass it to the service, the filter has no effect.

### List vs Detail Responsibility

```txt
get_items()
  → returns a collection
  → applies optional filters

get_item_by_id()
  → returns one item
  → matches item_id and user_id
```

```txt
/items?category=Shirt → list behavior
/items/7              → detail behavior
```

### Combined Filters

Multiple `.where()` calls stack as `AND` conditions.

```http
GET /items?category=Shirt&brand=UNIQLO
```

means:

```txt
user_id == current_user.id
AND category == "Shirt"
AND brand == "UNIQLO"
```

---

## Closet Analytics

### Endpoint

```http
GET /items/stats
```

It returns:

```txt
total item count
total closet value
category counts
brand counts
most expensive item
```

The first implementation calculates values in Python after loading the current user's items.

```txt
Require Bearer token
  ↓
Identify current user
  ↓
Fetch only that user's items
  ↓
Loop through items
  ↓
Calculate totals and counts
  ↓
Return ItemStats response
```

This favors clarity and testability. A later version can use SQL aggregation:

```txt
COUNT
SUM
GROUP BY
ORDER BY
LIMIT
```

### Route Ordering

Specific routes must appear before dynamic routes:

```txt
/items/stats
  → specific route; define first

/items/{item_id}
  → dynamic route; define later
```

Otherwise FastAPI may try to parse `stats` as an integer `item_id` and return `422`.

### Empty State

Analytics should return valid zero values for a new user:

```json
{
  "total_items": 0,
  "total_closet_value": "0.00",
  "category_counts": {},
  "brand_counts": {},
  "most_expensive_item": null
}
```

---

## Testing Notes

### Isolated Database

Tests override `get_db()` so they do not use development data.

```python
app.dependency_overrides[get_db] = override_get_db
```

The database is reset before each test:

```python
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
```

### Authenticated Item Tests

Protected item tests must:

```txt
register a test user
log in
extract access_token
send Authorization: Bearer <token>
```

The same headers should be reused for all requests in one user's test flow.

### What the Test Suite Proves

```txt
registration validation
login behavior
JWT-protected /auth/me
authenticated CRUD
missing-item behavior
cross-user isolation
richer item field persistence
empty and populated analytics
analytics user isolation
individual and combined filters
```

---

## Git and Workflow Notes

```txt
main should stay stable
feature work belongs on branches
run tests before committing
review migrations before applying them
review pull-request diffs before merging
never commit .env or local database files
```

Typical flow:

```txt
sync main
  ↓
create branch
  ↓
implement one focused feature
  ↓
format and test
  ↓
commit and push
  ↓
open and review PR
  ↓
merge
  ↓
sync main again
```

---

## Current Understanding Summary

Suot has evolved from an in-memory CRUD exercise into a layered, authenticated, database-backed inventory API.

The current request flow is:

```txt
Client request
  ↓
FastAPI router parses path, query, body, and token
  ↓
Pydantic validates input
  ↓
get_current_user() identifies the authenticated user
  ↓
Router passes current_user.id and request values to a service
  ↓
Service builds an owner-scoped SQLAlchemy query
  ↓
Session communicates with PostgreSQL
  ↓
Pydantic response schema controls returned data
```

The project currently supports:

```txt
health checks
database-backed item CRUD
environment-based configuration
Dockerized API and PostgreSQL
versioned Alembic migrations
isolated automated tests
user registration with Argon2 password hashing
login with expiring JWT access tokens
current-user identification through /auth/me
row-level item authorization
cross-user isolation tests
richer inventory data
current-user closet analytics
category, brand, and condition filters
combined filters
```

The most important security understanding is:

```txt
Authentication identifies a user.
Authorization limits which rows that user can access.
Ownership comes from the verified token, not client input.
Every private item query must remain scoped to user_id.
```

The most important database understanding is:

```txt
Models describe tables.
Alembic versions schema changes.
Sessions perform database work.
Transactions become permanent at commit.
Tests require isolated, repeatable state.
```

The most important query understanding is:

```txt
Start with the required ownership condition.
Add optional filters only when provided.
Keep list filtering in get_items().
Keep ID lookup in get_item_by_id().
Test filters individually and in combination.
```

Next planned backend improvement:

```txt
Phase 11B — Price range filters

GET /items?min_price=50
GET /items?max_price=150
GET /items?min_price=50&max_price=150

min_price → ItemModel.price >= min_price
max_price → ItemModel.price <= max_price
```
