# Suot API Core Notes

This file contains reusable backend concepts, architecture notes, and current understanding developed while building Suot API through Phase 11E.

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

Routers should not contain heavy database logic. They translate HTTP requests into service calls.

### Pydantic Schemas

Schemas define API input and output shapes.

```txt
request schema  → what the client may send
response schema → what the API may return
```

Request schemas containing secrets should not be reused as response schemas.

For example:

```txt
UserCreate
  → contains password
  → used for registration input

User
  → excludes password and hashed_password
  → used for safe API output
```

Item response schemas now include both individual item responses and paginated item page responses.

```txt
Item
  → one item record

ItemPage
  → list of items plus pagination metadata
```

### Services

Services handle database and application logic:

```txt
build SQLAlchemy queries
create model objects
apply ownership rules
apply filters
apply sorting
apply pagination
count matching rows
update and delete rows
calculate analytics
return results to routers
```

Services should not call FastAPI's `Depends()` or import `get_current_user()`.

They receive ordinary arguments such as:

```python
user_id: int
```

This keeps the service layer reusable and easier to test.

### SQLAlchemy Models

Models define how Python objects map to database tables.

```txt
ItemModel → items table
UserModel → users table
```

Models describe database shape. They do not decide HTTP behavior.

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

Finds one row by primary key.

Owner-scoped item access requires an additional `user_id` condition, so Suot normally uses a `select()` statement for protected item lookups.

### `select()`

```python
select(ItemModel)
```

Builds a query.

Conditions can be added with `.where()`:

```python
select(ItemModel).where(
    ItemModel.id == item_id,
    ItemModel.user_id == user_id,
)
```

Multiple conditions stack together as `AND`.

### `db.scalars()`

```python
list(db.scalars(statement))
```

Runs a `SELECT` statement, extracts model objects, and converts the result into a list.

### `db.scalar()`

```python
db.scalar(statement)
```

Runs a statement and returns one scalar result.

Suot uses this for things like:

```python
count_items()
```

where the query returns a number instead of model objects.

### `db.add()`

```python
db.add(item)
```

Stages a new object for insertion.

It does not permanently save the row until `db.commit()`.

### Field Assignment

```python
item.name = item_data.name
item.category = item_data.category
```

SQLAlchemy tracks changes made to loaded model objects.

A later commit persists them.

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

Reloads a model from the database.

This is useful after creation because the database generates values such as `id`.

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
.env          → real local values; never commit
.env.example  → safe template; commit this
app/config.py → validated application settings
```

Database hosts differ by runtime:

```txt
API on laptop          → localhost
API in Docker Compose  → db
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

SQLAlchemy models describe the desired table structure.

Alembic migrations change the real database from one version to another.

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

When adding a column to a table with existing rows, nullability and default values must be considered.

Optional fields such as `brand`, `price`, `purchase_date`, `condition`, and `notes` allowed existing rows to survive schema changes safely.

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

The client never supplies item ownership.

The backend derives ownership from the authenticated user:

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

Every private item query begins with ownership:

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

### Price Range Filters

Price filters compare against the `price` column.

```python
if min_price is not None:
    statement = statement.where(ItemModel.price >= min_price)

if max_price is not None:
    statement = statement.where(ItemModel.price <= max_price)
```

Query examples:

```http
GET /items?min_price=50
GET /items?max_price=150
GET /items?min_price=50&max_price=150
```

Meaning:

```txt
min_price → ItemModel.price >= min_price
max_price → ItemModel.price <= max_price
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
  → returns a collection page
  → applies optional filters
  → applies optional sorting
  → applies pagination

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

## Sorting

Sorting controls the order of matching rows.

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

The router uses `Literal` types to reject invalid sorting options before the request reaches the service.

Invalid values return:

```http
422 Unprocessable Entity
```

Sorting happens after ownership and filters:

```txt
ownership
  ↓
filters
  ↓
sorting
```

---

## Pagination

Pagination returns a smaller slice of a larger result set.

```http
GET /items?limit=20&offset=0
GET /items?limit=20&offset=20
```

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

Pagination happens after ownership, filters, and sorting:

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

### Pagination Validation

`limit` is constrained:

```txt
minimum → 1
maximum → 100
```

`offset` is constrained:

```txt
minimum → 0
```

Invalid pagination values return:

```http
422 Unprocessable Entity
```

### Pagination Metadata

`GET /items` returns an item page response:

```json
{
  "items": [],
  "total": 0,
  "limit": 20,
  "offset": 0,
  "has_more": false
}
```

Metadata fields:

```txt
items    → current page of item records
total    → total matching rows before pagination
limit    → requested page size
offset   → number of skipped rows
has_more → whether another page exists
```

`has_more` is calculated as:

```python
offset + len(items) < total
```

Example with another page:

```txt
total = 37
offset = 0
len(items) = 20

0 + 20 < 37
has_more = true
```

Example on the last page:

```txt
total = 37
offset = 20
len(items) = 17

20 + 17 < 37
has_more = false
```

The frontend can use `has_more` to disable the Next button.

---

## Counting Items

Pagination metadata needs the number of matching rows before pagination.

That is why Suot has a separate counting operation:

```txt
get_items()
  → returns the current page

count_items()
  → returns total matching rows before pagination
```

Both operations must use the same ownership and filter conditions.

The count query should not apply sorting, limit, or offset.

```txt
Count query:
  ownership
  filters

Page query:
  ownership
  filters
  sorting
  pagination
```

This keeps pagination metadata accurate.

---

## Shared Filter Helper

Suot uses a shared filter-building helper so `get_items()` and `count_items()` apply the same ownership and filtering rules.

Conceptually:

```txt
_build_item_filters()
  ↓
user ownership condition
  ↓
optional category filter
  ↓
optional brand filter
  ↓
optional condition filter
  ↓
optional min_price filter
  ↓
optional max_price filter
```

This prevents bugs where the list endpoint and count query disagree.

Example bug this avoids:

```txt
/items?category=Shirt
  → items returns only shirts
  → total accidentally counts all items
```

Correct behavior:

```txt
/items?category=Shirt
  → items returns only shirts
  → total counts only shirts
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

Current implementation calculates values in Python after loading the current user's full item set.

```txt
Require Bearer token
  ↓
Identify current user
  ↓
Fetch all of that user's items for analytics
  ↓
Loop through items
  ↓
Calculate totals and counts
  ↓
Return ItemStats response
```

This favors clarity and testability.

A later version can use SQL aggregation:

```txt
COUNT
SUM
GROUP BY
ORDER BY
LIMIT
```

### Analytics Must Not Use Paginated Items

This is an important backend bug pattern.

After pagination, `get_items()` returns only one page:

```txt
limit=20
offset=0
```

So analytics should not call:

```python
items = get_items(db, user_id)
```

because that would only analyze the first page.

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

The deeper lesson:

```txt
A function that returns a page should not be reused when the caller needs the full dataset.
```

Different use cases need different query semantics:

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

### List Endpoint Response Shape

`GET /items` now returns an object:

```json
{
  "items": [],
  "total": 0,
  "limit": 20,
  "offset": 0,
  "has_more": false
}
```

So tests for the list endpoint should inspect:

```python
data = response.json()["items"]
```

But single-item and stats endpoints still return direct objects.

```txt
POST /items          → response.json()
GET /items/{item_id} → response.json()
PUT /items/{item_id} → response.json()
GET /items/stats     → response.json()
GET /items           → response.json()["items"]
```

### Pagination Metadata Tests

Pagination metadata tests should verify both cases:

```txt
has_more = true
  → more results exist after the current page

has_more = false
  → current page reaches the end
```

Example:

```txt
total = 2
limit = 1
offset = 0
items returned = 1
has_more = true
```

```txt
total = 2
limit = 1
offset = 1
items returned = 1
has_more = false
```

### Analytics Regression Test

Suot includes a regression test to ensure analytics are not limited by pagination.

The test creates more than the default page size:

```txt
25 items
```

Then checks:

```txt
total_items == 25
total_closet_value == "25.00"
```

This catches the bug where `/items/stats` accidentally uses paginated `get_items()` and only counts the first 20 rows.

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
minimum price filtering
maximum price filtering
price range filtering
sorting by price, name, and purchase date
invalid sorting validation
pagination with limit and offset
invalid pagination validation
pagination metadata
analytics are not limited by pagination
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

Local branch cleanup after merge:

```bash
git branch -d feature/some-branch
```

This deletes the local branch only.

It does not delete:

```txt
main
merged commits
GitHub PR history
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
Service applies optional filters, sorting, pagination, or analytics logic
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
price range filters
combined filters
sorting
pagination
pagination metadata
analytics protected from pagination bugs
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
Sort only after filtering.
Paginate only after sorting.
Use a separate count query for pagination metadata.
Do not reuse paginated list queries for analytics.
Keep ID lookup in get_item_by_id().
Test filters, sorting, pagination, and ownership together.
```

The most important API design understanding is:

```txt
List endpoints often need metadata.
Raw arrays are simple, but paginated objects are more useful for frontends.
A frontend needs total, limit, offset, and has_more to build reliable pagination controls.
```

Next planned project milestone:

```txt
Phase 12 — Frontend MVP

Goal:
Log in
  ↓
view your own closet items
  ↓
add new items
  ↓
filter, sort, and paginate inventory
  ↓
view basic closet analytics
```