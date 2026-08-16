# Suot API Development Log

This file tracks the learning process, design decisions, and backend milestones completed while building Suot API.

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

- An API acts as the interface between clients and the application.
- Routers handle HTTP requests and route them to the correct logic.
- A health check endpoint confirms that the API is running correctly.

### Endpoints Added

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
- Added 404 error handling.

### Endpoints Added

```http
GET /items
POST /items
GET /items/{item_id}
PUT /items/{item_id}
DELETE /items/{item_id}
```

### Concepts Learned

CRUD means:

```txt
Create  → POST
Read    → GET
Update  → PUT
Delete  → DELETE
```

The first version stored items in memory:

```python
items = []
```

This worked for learning API flow, but data disappeared when the server restarted.

### 404 Error Handling

If an item does not exist, the API returns:

```http
404 Not Found
```

This prevents the server from crashing with a `500 Internal Server Error`.

### ID Design Decision

IDs should not be reused after deletion.

Reason:

```txt
IDs represent stable record identity.
If an old ID is reused, historical references such as orders, favorites, logs, or audit records could accidentally point to the wrong item.
```

### Phase Status

Phase 1 complete: in-memory item CRUD finished.

---

## Day 3 — ORM and Database Concepts

### Goal

Understand how HTTP requests can become data stored in a SQL database, and how that data can be retrieved later.

### What Is an ORM?

ORM means:

```txt
Object Relational Mapper
```

An ORM maps between programming language objects and relational database tables.

It helps with both:

```txt
Python objects → database rows
database rows → Python objects
```

Instead of writing raw SQL for every operation, the application can work with Python objects.

### SQLAlchemy

SQLAlchemy is the ORM being used in this project.

It allows the service layer to create, read, update, and delete database records using Python objects.

### `db.add()` vs `db.commit()`

```python
db.add(item)
```

Stages a new object to be inserted into the database.

```python
db.commit()
```

Permanently saves pending database changes in the current transaction.

Important distinction:

```txt
db.add()     → prepare the change
db.commit()  → save the change
```

### Phase Status

Database and ORM concepts introduced.

---

## Day 4 — SQLite Persistence

### Goal

Replace temporary in-memory storage with persistent storage so data survives after restarting the server.

### Work Completed

- Added SQLite database support.
- Added SQLAlchemy database setup.
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
Restart server → data disappears
```

### New Storage

```txt
SQLite database file
```

Result:

```txt
Restart server → data survives
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
SQLAlchemy inserts row into SQLite
  ↓
db.commit() saves it
  ↓
db.refresh() gets the generated ID
  ↓
API returns JSON
```

### Architecture After Persistence

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

### Phase Status

Phase 2 complete: SQLite persistence with SQLAlchemy finished.

---

## Day 5 — API Testing with pytest

### Goal

Add automated tests so item CRUD behavior can be verified without manually using Swagger UI every time.

### Work Completed

- Created a `tests/` folder outside of the `app/` folder.
- Added `tests/test_items.py`.
- Added pytest configuration to `pyproject.toml`.
- Fixed import path issues so tests can import the FastAPI app.
- Added an isolated test database.
- Added tests for item CRUD endpoints.
- Confirmed all tests pass with `uv run pytest`.

### Why Tests Matter

Before testing, item endpoints had to be checked manually through Swagger UI.

Now, pytest can automatically verify that the API still works. As the project grows, these tests help catch broken behavior early.

### Test Database Isolation

The tests use a separate database instead of the normal development database.

Normal app:

```txt
get_db() → suot.db
```

Tests:

```txt
get_db() → test.db
```

This prevents tests from polluting local development data.

### Dependency Override

FastAPI allows dependencies to be overridden during tests.

```python
app.dependency_overrides[get_db] = override_get_db
```

This means:

```txt
During normal app usage:
    use the real database session

During tests:
    use the test database session
```

### Test Database Reset

Before each test, the test database is reset:

```python
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
```

Every test starts from a clean database state, making the tests predictable and repeatable.

### CRUD Tests Added

```txt
POST   /items           → create item
GET    /items           → list all items
GET    /items/{id}      → get one item
GET    /items/999       → return 404 for missing item
PUT    /items/{id}      → update item
PUT    /items/999       → return 404 for missing item
DELETE /items/{id}      → delete item
DELETE /items/999       → return 404 for missing item
```

### Phase Status

Phase 3 complete: item CRUD API is now covered by automated tests.

---

## Day 6 — Configuration, PostgreSQL, Docker, and Git Branching

### Goal

Move Suot closer to a real backend system by separating configuration from application logic, running PostgreSQL as a database service, containerizing the FastAPI API, and using Git branches for safer feature work.

### Work Completed

- Added an application configuration layer with `pydantic-settings`.
- Created `app/config.py`.
- Updated `database.py` to read the database URL from settings.
- Added `.env.example` as a safe configuration template.
- Kept the real `.env` file ignored by Git.
- Installed Docker Desktop.
- Created `docker-compose.yml`.
- Ran PostgreSQL inside Docker.
- Connected the local FastAPI app to the PostgreSQL container.
- Verified PostgreSQL data directly with `psql`.
- Created feature branches for infrastructure work.
- Created a `Dockerfile` for the FastAPI API.
- Created a `.dockerignore` file.
- Updated Docker Compose to run both the API and database.
- Built and ran the API container.
- Confirmed Swagger works through `http://localhost:8000/docs`.
- Confirmed item CRUD works through the Dockerized API.

### Why Configuration Matters

Before this step, the database URL was hardcoded in `database.py`.

A better design is:

```txt
Environment
  ↓
Configuration layer
  ↓
Database setup
  ↓
Application logic
```

This allows the same application code to run with different databases depending on the environment.

```txt
Local development → SQLite
Testing           → test.db
Local Docker      → PostgreSQL in Docker
Production        → hosted PostgreSQL database
```

### PostgreSQL in Docker

SQLite was a local database file:

```txt
FastAPI app
  ↓
suot.db
```

PostgreSQL is a separate database server:

```txt
FastAPI app
  ↓
DATABASE_URL
  ↓
PostgreSQL service
```

This is closer to real backend architecture because the API and database are separate processes.

### Local API vs Dockerized API

When the API runs locally on the laptop, it connects to PostgreSQL with:

```env
DATABASE_URL=postgresql+psycopg://suot:suot@localhost:5432/suot
```

When the API runs inside Docker Compose, it connects to PostgreSQL with:

```env
DATABASE_URL=postgresql+psycopg://suot:suot@db:5432/suot
```

Important distinction:

```txt
localhost → used when the API runs on the laptop
db        → used when the API runs inside Docker Compose
```

### Docker Concepts Learned

A Docker image is a blueprint for creating a container.

A Docker container is a running instance of an image.

A Docker volume stores persistent data.

A Docker network lets containers communicate.

Docker Compose runs multiple services together.

```txt
Dockerfile          → builds the FastAPI API image
docker-compose.yml → runs the API and database services
.dockerignore       → excludes unnecessary or private files from the image
api service         → FastAPI application
db service          → PostgreSQL database
postgres_data       → persistent PostgreSQL storage
```

### Testing Clarification

```txt
uv run pytest
  → local automated tests for API behavior

http://localhost:8000/docs
  → manual test of the Dockerized API runtime

psql inside suot-postgres
  → direct verification of database rows
```

### Git Branching Lesson

`main` should represent the stable version of the project. Feature branches should be used for meaningful work that could break the app.

```txt
branch → build → test → commit → merge → push
```

Important Git rules:

```txt
Do not commit .env.
Do not commit local database files.
Use branches for backend infrastructure changes.
Run tests before committing.
Confirm Docker containers run before merging Docker changes.
Keep commit messages clear and human-readable.
```

### Phase Status

Phase 4 complete: PostgreSQL now runs locally through Docker.

Phase 5 complete: the FastAPI API now runs in Docker with PostgreSQL through Docker Compose.

---

## Day 7 — Alembic Migrations and Schema Evolution

### Goal

Replace automatic table creation with versioned database migrations, then prove that the database schema can evolve safely over time.

### Work Completed

- Installed Alembic.
- Initialized an Alembic migration environment.
- Added `alembic.ini` and the `alembic/` folder.
- Connected Alembic to the app's `DATABASE_URL`.
- Connected Alembic to SQLAlchemy's `Base.metadata`.
- Removed `Base.metadata.create_all()` from FastAPI startup.
- Generated and applied the first migration for the `items` table.
- Added an optional `brand` column to `ItemModel`.
- Updated Pydantic schemas, service logic, and tests for `brand`.
- Generated and applied a second migration to add `brand` to the existing table.
- Confirmed old rows had `brand = null`.
- Confirmed new rows could store a brand value.
- Removed tracked `__pycache__` files from Git.

### Why Alembic Was Added

The early app used:

```python
Base.metadata.create_all(bind=engine)
```

This creates missing tables, but changing SQLAlchemy models does not safely update existing database tables.

Alembic makes database schema changes explicit and versioned.

```txt
SQLAlchemy model = blueprint for the table
PostgreSQL       = real database storing the table
Alembic migration = update patch that changes the database schema
```

### Migration Flow

```txt
Change SQLAlchemy model
  ↓
Generate Alembic migration
  ↓
Review migration file
  ↓
Apply migration
  ↓
Database schema updates
```

```bash
uv run alembic revision --autogenerate -m "migration message"
uv run alembic upgrade head
```

### `alembic_version`

Alembic creates an `alembic_version` table that stores the current migration revision applied to the database.

### Proving Schema Evolution

The item table evolved from:

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

The new model field was nullable:

```python
brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
```

This allowed existing rows to safely receive `brand = NULL`.

### Docker Volume Lesson

```txt
docker compose down
  → stops containers but keeps the database volume

docker compose down -v
  → stops containers and deletes the database volume
```

### Git Cleanup Lesson

`.gitignore` prevents new ignored files from being added. It does not automatically remove files that Git already tracks.

### Phase Status

Phase 6 complete: Alembic is installed, configured, and managing database schema changes.

---

## Day 8 — User Model, Users Table, and Registration

### Goal

Start the authentication foundation by creating a user database model, adding a users table, and implementing user registration with password hashing.

The focus was:

```txt
Create user accounts safely.
Store password hashes, not raw passwords.
Return safe user responses.
Prepare the backend for login and protected routes.
```

### Work Completed

- Created `app/models/user.py` and added `UserModel`.
- Added `email`, `username`, `hashed_password`, `is_active`, `created_at`, and `updated_at`.
- Created `app/schemas/user.py` with request and response schemas.
- Installed `email-validator` for Pydantic `EmailStr`.
- Updated Alembic to import `UserModel`.
- Generated and applied a migration for the `users` table.
- Installed `pwdlib[argon2]` for password hashing.
- Created `app/security.py` with `hash_password()` and `verify_password()`.
- Created `app/services/user_service.py`.
- Added lookup helpers by email and username and added user creation logic.
- Created `app/routers/auth.py` and added `POST /auth/register`.
- Updated `app/main.py` to include the auth router.
- Tested registration through Swagger.
- Confirmed responses exclude `password` and `hashed_password`.
- Added tests for successful registration, duplicate email, and duplicate username.

### User Table Design

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

### Why Email and Username Are Separate

```txt
email
  → private login identifier

username
  → public/searchable identity for future profile features
```

Public profile endpoints should not expose email addresses.

### Request Schema vs Response Schema Lesson

A registration request needs a password, but the response must not include one.

Incorrect design:

```python
class User(UserCreate):
    ...
```

That makes the response schema inherit the secret `password` field.

Correct design:

```python
class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

Important rule:

```txt
Do not make response schemas inherit from request schemas that contain secrets.
```

### Password Hashing

```txt
raw password
  ↓
hash_password()
  ↓
hashed_password
  ↓
users table
```

The backend never stores raw passwords.

### Registration Flow

```txt
POST /auth/register
  ↓
Validate email, username, and password
  ↓
Check whether email or username already exists
  ↓
Hash password
  ↓
Create UserModel with hashed_password
  ↓
Save user row
  ↓
Return safe User response
```

Duplicate email or username requests return:

```http
409 Conflict
```

### Phase Status

Phase 7A complete: the user model, schemas, and users table migration are complete.

Phase 7B complete: registration works with password hashing, duplicate validation, and safe responses.

---

## Day 9 — Login, JWT Access Tokens, and `/auth/me`

### Goal

Add login, create JWT access tokens, and build a protected route that identifies the current user from a token.

### Work Completed

- Installed PyJWT.
- Added `SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES` settings.
- Added a `Token` response schema.
- Added `create_access_token()` and `decode_access_token()`.
- Added `authenticate_user()` and `get_user_by_id()`.
- Added `POST /auth/login` using OAuth2 password form data.
- Installed `python-multipart` for form-data parsing.
- Added `OAuth2PasswordBearer` for Bearer token authentication.
- Added reusable `get_current_user()` authentication dependency.
- Added `GET /auth/me`.
- Tested login and protected-route authorization through Swagger.
- Added auth tests for login and `/auth/me` behavior.
- Fixed formatting, import sorting, Docker refresh, and Swagger integration issues.

### Login Flow

```txt
POST /auth/login
  ↓
Client sends email and password as form data
  ↓
Backend finds user by email
  ↓
Backend verifies raw password against hashed_password
  ↓
Invalid credentials → 401 Unauthorized
  ↓
Valid credentials → create JWT access token
  ↓
Return access_token and token_type
```

The OAuth2 form field named `username` is treated as the user's email address.

### Password Verification

Password hashes are one-way. Login verifies a raw password against the stored hash; it never decrypts or recovers the original password.

### JWT Access Token Design

The token contains:

```txt
sub → subject → user id
exp → expiration time
```

```txt
The password proves identity once during login.
The JWT proves identity on future requests.
```

### Token Creation vs Token Consumption

```txt
/auth/login
  → creates the token

/auth/me
  → consumes the token
  → identifies the current user
```

Protected requests send:

```http
Authorization: Bearer <access_token>
```

### `OAuth2PasswordRequestForm` vs `OAuth2PasswordBearer`

```txt
OAuth2PasswordRequestForm
  → receives login form data

OAuth2PasswordBearer
  → reads the Bearer token from protected requests
```

### `get_current_user()`

```txt
Authorization: Bearer <token>
  ↓
Extract token
  ↓
Verify and decode token
  ↓
Read user id from payload["sub"]
  ↓
Find user in database
  ↓
Return current UserModel
```

### Phase Status

Phase 7C complete: login works and returns JWT access tokens.

Phase 7D complete: `/auth/me` identifies the current user from a Bearer token.

---

## Day 10 — User-Owned Items and Row-Level Authorization

### Goal

Upgrade the inventory from global item records to user-owned resources.

```txt
Authentication → Who are you?
Authorization  → Are you allowed to access this item?
```

For Suot, authorization means:

```txt
item.user_id == current_user.id
```

### Work Completed

- Added `user_id` to `ItemModel`.
- Added a foreign key from `items.user_id` to `users.id`.
- Generated and applied the item ownership migration.
- Updated item response schemas to include `user_id`.
- Updated item services to accept `user_id`.
- Assigned new items to the authenticated user.
- Scoped item list, detail, update, and delete queries to the authenticated user.
- Protected item routes with `get_current_user()`.
- Updated item tests to use Bearer tokens.
- Confirmed authenticated user-owned item behavior passes.

### Database Design

```txt
users.id → items.user_id

One user can own many items.
Each item belongs to one user.
```

Suot keeps one shared `items` table. Privacy comes from filtering every relevant query by `user_id`.

### Why `user_id` Is Used Instead of Username

```txt
user_id is stable.
username can change.
```

Database relationships use `user_id`; usernames are for display, search, and public identity.

### Client Does Not Send `user_id`

The client sends item data only. The backend derives ownership from the authenticated token.

```txt
JWT access token
  ↓
get_current_user()
  ↓
current_user.id
  ↓
item.user_id = current_user.id
```

This prevents a client from assigning an item to an arbitrary account.

### Owner-Scoped CRUD

```txt
GET /items
  → return current user's items

GET /items/{item_id}
PUT /items/{item_id}
DELETE /items/{item_id}
  → match both item_id and current_user.id
```

If no accessible item matches, the API returns `404 Not Found`. This avoids revealing whether another user's item exists.

### Layer Responsibilities

```txt
Router
  → HTTP request, authentication dependency, current_user, response

Service
  → database queries, ownership filtering, CRUD logic
```

Services receive `user_id` as a plain integer. They do not call FastAPI's `Depends()`.

### `401` vs `404`

```txt
No valid token
  → 401 Not authenticated

Valid token, but no accessible item
  → 404 Item not found
```

### Phase Status

Phase 8A complete: item routes require login and all item CRUD operations are scoped to the current user.

---

## Day 11 — Cross-User Authorization Tests

### Goal

Prove that user-owned inventory isolation works between separate accounts, not only for a single authenticated user.

### Work Completed

- Added a test helper that can register and authenticate different users.
- Created items as User A and attempted access as User B.
- Added a test proving User B's `GET /items` does not include User A's items.
- Added a test proving User B cannot retrieve User A's item by ID.
- Added a test proving User B cannot update User A's item.
- Added a test proving User B cannot delete User A's item.
- Confirmed inaccessible cross-user item requests return `404 Not Found`.
- Confirmed the original owner can still access and manage the item.
- Ran the full automated test suite after adding authorization coverage.

### Why These Tests Matter

Filtering by `current_user.id` looks correct in code, but authorization should be proven through behavior.

```txt
User A creates item
  ↓
Item is stored with User A's user_id
  ↓
User B authenticates with a different token
  ↓
User B tries to list, retrieve, update, or delete User A's item
  ↓
API does not expose or modify the item
```

### Isolation Rule

Every item query must answer:

```txt
Does this item exist for the current user?
```

not only:

```txt
Does this item ID exist anywhere?
```

The core condition remains:

```python
ItemModel.user_id == current_user.id
```

### Expected Cross-User Behavior

```txt
User B lists items
  → User A's items are absent

User B requests User A's item ID
  → 404 Not Found

User B updates User A's item ID
  → 404 Not Found

User B deletes User A's item ID
  → 404 Not Found
```

### Phase Status

Phase 8B complete: cross-user authorization tests prove that users cannot access or modify each other's private inventory.

---

## Day 12 — Richer Item Fields

### Goal

Upgrade item records from basic clothing entries into more useful inventory records.

Before this phase, items stored `name`, `brand`, `category`, `color`, and `size`.

After this phase, items can also store `price`, `purchase_date`, `condition`, and `notes`.

### Work Completed

- Added `price`, `purchase_date`, `condition`, and `notes` to `ItemModel`.
- Used `Numeric(10, 2)` for price.
- Used `Date` for purchase date.
- Used `String(50)` for condition.
- Used `Text` for notes.
- Generated and applied an Alembic migration for the new fields.
- Updated item schemas to accept and return the new fields.
- Updated item creation and update service logic.
- Updated tests to verify richer data is created, returned, and updated correctly.

### Why These Fields Matter

```txt
price
  → closet value and spending analytics

purchase_date
  → spending over time and recent purchase tracking

condition
  → quality tracking, resale decisions, and wardrobe maintenance

notes
  → flexible personal context
```

### Price Design

`price` uses `Numeric(10, 2)` and maps to Python `Decimal`.

Money should not be stored with floating-point numbers because binary floating-point can introduce precision errors.

### Optional Field Design

The new fields are optional because existing items did not have these values and users may not know every detail when adding an item.

### Schema Evolution Flow

```txt
Update SQLAlchemy model
  ↓
Generate and review Alembic migration
  ↓
Apply migration
  ↓
Update Pydantic schemas
  ↓
Update service logic
  ↓
Update tests
```

### Phase Status

Phase 9 complete: items now support richer inventory details.

---

## Day 13 — Closet Analytics Endpoint

### Goal

Add a protected analytics endpoint that summarizes the current user's closet.

### Endpoint Added

```http
GET /items/stats
Authorization: Bearer <access_token>
```

### Work Completed

- Added `MostExpensiveItem` and `ItemStats` response schemas.
- Added `get_item_stats()` service function.
- Added `GET /items/stats` route.
- Calculated total item count and total closet value.
- Calculated category and brand counts.
- Found the most expensive item.
- Added tests for an empty closet and a closet with multiple items.
- Added tests proving analytics include only the current user's items.

### Analytics Response

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

### Empty Closet Behavior

```json
{
  "total_items": 0,
  "total_closet_value": "0.00",
  "category_counts": {},
  "brand_counts": {},
  "most_expensive_item": null
}
```

### Important Route Ordering Lesson

`/items/stats` must be defined before `GET /items/{item_id}`.

FastAPI checks routes from top to bottom. If the dynamic route comes first, it may treat `stats` as an integer item ID and return `422`.

```txt
Specific routes first.
Dynamic routes last.
```

### Python Calculation First

The first version fetches the current user's items and calculates stats in Python. This is easy to understand and test.

Later, it can be optimized with SQL aggregation using `COUNT`, `SUM`, `GROUP BY`, `ORDER BY`, and `LIMIT`.

### Authorization Rule

Closet analytics follow the same ownership rule as item CRUD:

```txt
item.user_id == current_user.id
```

### Phase Status

Phase 10A complete: Suot now has a protected closet analytics endpoint.

---

## Day 14 — Basic Item Filtering

### Goal

Upgrade `GET /items` so users can filter their inventory instead of always fetching every item.

### Supported Filters

```http
GET /items?category=Shirt
GET /items?brand=UNIQLO
GET /items?condition=new
GET /items?category=Shirt&brand=UNIQLO
```

### Work Completed

- Added optional `category`, `brand`, and `condition` query parameters.
- Updated the router to receive the parameters and pass them into the service.
- Updated `get_items()` to build conditional SQLAlchemy filters.
- Added tests for category, brand, condition, and combined filtering.
- Fixed a router/service parameter-flow issue.
- Corrected filtering logic that had been placed in the detail lookup function.
- Confirmed item tests pass after the filtering changes.

### Query Parameter Flow

```txt
GET /items?category=Shirt&brand=UNIQLO
  ↓
Router receives category, brand, and condition
  ↓
Router passes them to get_items()
  ↓
Service adds SQLAlchemy WHERE conditions
  ↓
Database returns matching user-owned rows
```

### Service Layer Filtering

The query begins with ownership:

```python
statement = select(ItemModel).where(ItemModel.user_id == user_id)
```

Optional filters are added only when provided:

```python
if category is not None:
    statement = statement.where(ItemModel.category == category)

if brand is not None:
    statement = statement.where(ItemModel.brand == brand)

if condition is not None:
    statement = statement.where(ItemModel.condition == condition)
```

Important rule:

```txt
Always scope by user_id.
Then narrow by optional inventory filters.
```

### `get_items()` vs `get_item_by_id()`

`get_items()` handles list behavior and optional filters.

`get_item_by_id()` handles one specific item lookup by `item_id` and `user_id`.

```txt
/items?category=Shirt → get_items()
/items/7              → get_item_by_id()
```

Filters belong in the list function; IDs belong in the detail function.

### Combined Filtering

Combined filters stack together.

```http
GET /items?category=Shirt&brand=UNIQLO
```

This returns rows where the item belongs to the current user and matches both the category and brand.

### Authorization Rule

Filtering never means “all items matching this category.” It always means “the current user's items matching this category.”

### Phase Status

Phase 11A complete: `GET /items` now supports basic filtering by category, brand, and condition.

---

## Current Checkpoint

Suot now includes:

```txt
FastAPI foundation
database-backed CRUD
PostgreSQL and Docker
Alembic migrations
automated tests
user registration and password hashing
JWT login and protected routes
user-owned inventory
cross-user authorization isolation
richer item fields
closet analytics
basic item filtering
```

Next planned backend improvement:

```txt
Phase 11B — Price range filters

GET /items?min_price=50
GET /items?max_price=150
GET /items?min_price=50&max_price=150
```
