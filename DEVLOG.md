# Suot API Development Log

This file tracks the learning process, design decisions, and backend concepts explored while building Suot API.

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

Before testing, I had to manually check endpoints through Swagger UI.

Now, pytest can automatically verify that the API still works.

This matters because as the project grows, tests help catch broken behavior early.

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

The test file overrides the normal database dependency:

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

This means every test starts from a clean database state.

That makes the tests predictable and repeatable.

### CRUD Tests Added

The tests cover:

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

Example:

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

In this project:

```txt
Dockerfile          → builds the FastAPI API image
docker-compose.yml → runs the API and database services
.dockerignore       → prevents unnecessary/private files from being copied into the image
api service         → FastAPI application
db service          → PostgreSQL database
postgres_data       → persistent PostgreSQL storage
```

### Testing Clarification

`uv run pytest` still runs tests locally.

It does not run tests inside Docker yet.

Current meaning:

```txt
uv run pytest
  → local automated tests for API behavior

http://localhost:8000/docs
  → manual test of the Dockerized API runtime

psql inside suot-postgres
  → direct verification of database rows
```

### Git Branching Lesson

`main` should represent the stable version of the project.

Feature branches should be used for meaningful work that could break the app.

The basic sequence is:

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
- Added `alembic.ini`.
- Added the `alembic/` folder.
- Connected Alembic to the app’s `DATABASE_URL`.
- Connected Alembic to SQLAlchemy’s `Base.metadata`.
- Removed `Base.metadata.create_all()` from FastAPI startup.
- Generated the first migration for the `items` table.
- Applied the first migration to PostgreSQL with `alembic upgrade head`.
- Added an optional `brand` column to `ItemModel`.
- Updated Pydantic schemas, service logic, and tests for the new `brand` field.
- Generated and applied a second migration to add `brand` to the existing `items` table.
- Confirmed old rows had `brand = null`.
- Confirmed new rows could store a real brand value.
- Removed tracked `__pycache__` files from Git.

### Why Alembic Was Added

Before this phase, the app used:

```python
Base.metadata.create_all(bind=engine)
```

This created tables automatically when the app started.

That was useful early on, but it is not ideal for a growing backend project.

Problem:

```txt
Changing SQLAlchemy models does not safely update existing database tables.
```

Alembic solves this by making database schema changes explicit and versioned.

Simple definition:

```txt
SQLAlchemy model = blueprint for the table
PostgreSQL = real database storing the table
Alembic migration = update patch that changes the database schema
```

### Migration Flow

The professional migration flow is:

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

Command to generate a migration:

```bash
uv run alembic revision --autogenerate -m "migration message"
```

Command to apply migrations:

```bash
uv run alembic upgrade head
```

### `alembic_version`

Alembic creates a table called:

```txt
alembic_version
```

This table stores the current migration revision applied to the database.

It tells Alembic:

```txt
This database is currently at this schema version.
```

### Proving Schema Evolution

The model changed from:

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

The new model field:

```python
brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
```

The Pydantic schema was also updated:

```python
brand: str | None = None
```

### Why `brand` Was Nullable

The `brand` column was added as nullable because old rows already existed in the database.

If the new column had been added as:

```python
nullable=False
```

PostgreSQL would require every existing row to immediately have a brand value.

But old rows did not have one yet.

Using:

```python
nullable=True
```

allowed old rows to safely receive:

```txt
brand = NULL
```

### Docker Volume Lesson

During migration setup, the local Docker PostgreSQL database was reset with:

```bash
docker compose down -v
```

Important distinction:

```txt
docker compose down
  → stops containers but keeps database volume

docker compose down -v
  → stops containers and deletes the database volume
```

### Git Cleanup Lesson

Important rule:

```txt
.gitignore prevents new ignored files from being added.
.gitignore does not automatically remove files that are already tracked.
```

Tracked cache files were removed with:

```bash
git rm --cached -r --ignore-unmatch app/__pycache__ app/models/__pycache__ app/schemas/__pycache__ app/services/__pycache__
```

After that, `.gitignore` prevents those files from being added again.

### Phase Status

Phase 6 complete: Alembic is installed, configured, and managing database schema changes.

---

## Day 8 — User Model, Users Table, and Registration

### Goal

Start the authentication foundation by creating a user database model, adding a users table, and implementing user registration with password hashing.

This phase does not include login or JWT access tokens yet.

The focus is:

```txt
Create user accounts safely.
Store password hashes, not raw passwords.
Return safe user responses.
Prepare the backend for login and protected routes later.
```

### Work Completed

- Created `app/models/user.py`.
- Added `UserModel` as the SQLAlchemy model for the `users` table.
- Added `email`, `username`, `hashed_password`, `is_active`, `created_at`, and `updated_at` fields.
- Created `app/schemas/user.py`.
- Added user request and response schemas.
- Installed `email-validator` for Pydantic `EmailStr`.
- Updated Alembic to import `UserModel`.
- Generated and applied a migration for the `users` table.
- Installed `pwdlib[argon2]` for password hashing.
- Created `app/security.py`.
- Added `hash_password()` and `verify_password()`.
- Created `app/services/user_service.py`.
- Added user lookup helpers by email and username.
- Added user creation logic.
- Created `app/routers/auth.py`.
- Added `POST /auth/register`.
- Updated `app/main.py` to include the auth router.
- Tested registration through Swagger.
- Confirmed registered users receive a safe response without `password` or `hashed_password`.
- Added registration tests for successful registration, duplicate email, and duplicate username.

### User Table Design

The `users` table stores account identity data.

Current fields:

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

Email and username have different purposes.

```txt
email
  → private login identifier

username
  → public/searchable identity for future profile features
```

Important rule:

```txt
Do not expose email publicly in future public profile endpoints.
```

### Request Schema vs Response Schema Lesson

A registration request needs a password.

```python
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
```

But the response should not include a password.

Incorrect design:

```python
class User(UserCreate):
    ...
```

That caused `User` to inherit the `password` field from `UserCreate`.

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

The backend should never store raw passwords.

Bad:

```txt
password = "password123"
```

Good:

```txt
hashed_password = "argon2_hash_here"
```

Registration flow:

```txt
raw password
  ↓
hash_password()
  ↓
hashed_password
  ↓
users table
```

### Registration Flow

Current endpoint:

```http
POST /auth/register
```

Request body:

```json
{
  "email": "jim@example.com",
  "username": "jim",
  "password": "password123"
}
```

Registration flow:

```txt
POST /auth/register
  ↓
Client sends email, username, and password
  ↓
Pydantic validates the request body
  ↓
Auth router receives UserCreate
  ↓
User service checks whether email already exists
  ↓
User service checks whether username already exists
  ↓
Password is hashed
  ↓
UserModel is created with hashed_password
  ↓
SQLAlchemy saves the user row
  ↓
API returns safe User response
```

The response does not include:

```txt
password
hashed_password
```

### Duplicate Account Validation

If a user registers with an email that already exists, the API returns:

```http
409 Conflict
```

If a user registers with a username that already exists, the API returns:

```http
409 Conflict
```

Reason:

```txt
409 Conflict means the request is valid, but it conflicts with existing server state.
```

### Phase Status

Phase 7A complete: the user model, user schemas, and users table migration are complete.

Phase 7B complete: user registration works with password hashing, duplicate validation, and safe response schemas.

---

## Day 9 — Login, JWT Access Tokens, and `/auth/me`

### Goal

Complete the next part of authentication by adding login, creating JWT access tokens, and building a protected route that can identify the current user from a token.

Before this phase, Suot could create user accounts.

After this phase, Suot can:

```txt
Register a user.
Log in with valid credentials.
Create a JWT access token.
Receive that token on a protected route.
Decode the token.
Find the current user.
Return the current authenticated user.
```

### Work Completed

- Installed PyJWT for JWT access token creation and decoding.
- Added authentication settings to the app configuration.
- Added `SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES`.
- Added a `Token` response schema.
- Added `create_access_token()` to `security.py`.
- Added `decode_access_token()` to `security.py`.
- Added `authenticate_user()` to `user_service.py`.
- Added `get_user_by_id()` to `user_service.py`.
- Added `POST /auth/login`.
- Updated `/auth/login` to use OAuth2 password form data.
- Installed `python-multipart` for form-data parsing.
- Added `OAuth2PasswordBearer` for Bearer token authentication.
- Added `get_current_user()` as a reusable authentication dependency.
- Added `GET /auth/me`.
- Tested login through Swagger.
- Tested Swagger authorization with a Bearer token.
- Confirmed `/auth/me` returns the current authenticated user.
- Added auth tests for login and `/auth/me`.

### Login Flow

Current endpoint:

```http
POST /auth/login
```

The login endpoint uses OAuth2 password form data.

In Swagger, the login form shows:

```txt
username
password
```

For Suot, the `username` field is treated as the user’s email address.

Example:

```txt
username: jim@example.com
password: password123
```

Login flow:

```txt
POST /auth/login
  ↓
Client sends email and password as form data
  ↓
Backend finds user by email
  ↓
Backend verifies the raw password against hashed_password
  ↓
If credentials are invalid, return 401 Unauthorized
  ↓
If credentials are valid, create JWT access token
  ↓
Return access_token and token_type
```

Successful response:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Why Login Uses `401 Unauthorized`

If the email does not exist or the password is wrong, the API returns:

```http
401 Unauthorized
```

Response:

```json
{
  "detail": "Invalid email or password"
}
```

The response intentionally does not reveal whether the email exists.

Reason:

```txt
Do not help attackers discover registered emails.
```

### JWT Access Token Creation

After successful login, the backend creates a JWT access token.

The token currently contains:

```txt
sub
  → subject
  → user id

exp
  → expiration time
```

For Suot:

```txt
sub = user.id
```

This means:

```txt
This token represents a specific user account.
```

### Token Creation vs Token Consumption

Token creation:

```txt
POST /auth/login
  ↓
credentials are valid
  ↓
backend creates JWT
  ↓
client receives token
```

Token consumption:

```txt
GET /auth/me
  ↓
client sends token
  ↓
backend verifies token
  ↓
backend identifies current user
```

Important distinction:

```txt
/login creates the token.
/auth/me consumes the token.
```

### Bearer Token Authentication

Protected routes expect the client to send the token through the `Authorization` header.

```http
Authorization: Bearer <access_token>
```

The word `Bearer` means:

```txt
Whoever bears this token is treated as authenticated,
as long as the token is valid.
```

### `OAuth2PasswordRequestForm` vs `OAuth2PasswordBearer`

```txt
OAuth2PasswordRequestForm
  → used by /auth/login
  → receives username and password form data

OAuth2PasswordBearer
  → used by protected routes
  → reads Authorization: Bearer <token>
```

Important distinction:

```txt
OAuth2PasswordRequestForm handles login input.
OAuth2PasswordBearer handles token input.
```

### `get_current_user()`

`get_current_user()` is the reusable authentication dependency.

It does this:

```txt
Authorization: Bearer <token>
  ↓
OAuth2PasswordBearer extracts the token
  ↓
decode_access_token() verifies the token
  ↓
payload["sub"] gives the user id
  ↓
get_user_by_id() finds the user in the database
  ↓
return current user
```

Simple definition:

```txt
get_current_user() = convert a valid token into the current UserModel
```

### `/auth/me`

Current endpoint:

```http
GET /auth/me
```

This route answers:

```txt
Given this token, who am I?
```

Flow:

```txt
GET /auth/me
  ↓
Client sends Authorization: Bearer <access_token>
  ↓
Backend verifies and decodes JWT
  ↓
Backend reads sub as user id
  ↓
Backend finds user in PostgreSQL
  ↓
API returns current user
```

### Auth Test Coverage

Auth tests cover:

```txt
POST /auth/register
  → creates a user successfully

POST /auth/register with duplicate email
  → returns 409 Conflict

POST /auth/register with duplicate username
  → returns 409 Conflict

POST /auth/login with valid credentials
  → returns access_token

POST /auth/login with wrong password
  → returns 401 Unauthorized

GET /auth/me with valid token
  → returns current user

GET /auth/me without token
  → returns 401 Unauthorized
```

### Phase Status

Phase 7C complete: login works and returns JWT access tokens.

Phase 7D complete: `/auth/me` works and can identify the current user from a Bearer token.

Phase 7E complete: auth tests cover registration, login, and `/auth/me`.

---

## Day 10 — User-Owned Items and Row-Level Authorization

### Goal

Upgrade Suot from global item records to user-owned inventory.

Before this phase, items existed in the database, but they were not tied to a specific user.

After this phase, every item belongs to a user through:

```txt
items.user_id
```

This connects item ownership to authentication.

Core idea:

```txt
Authentication
  → Who are you?

Authorization
  → Are you allowed to access this item?
```

For Suot, authorization means:

```txt
item.user_id == current_user.id
```

### Work Completed

- Added `user_id` to `ItemModel`.
- Added a foreign key from `items.user_id` to `users.id`.
- Generated an Alembic migration for item ownership.
- Applied the migration to the database.
- Updated item schemas so item responses include `user_id`.
- Updated item service functions to accept `user_id`.
- Updated item creation so new items are owned by the authenticated user.
- Updated item queries so users only see their own items.
- Updated item update logic so users can only update their own items.
- Updated item delete logic so users can only delete their own items.
- Protected item routes with `get_current_user()`.
- Updated item tests to use authenticated requests with Bearer tokens.
- Confirmed item tests pass with user-owned item behavior.
- Practiced committing feature work and preparing it for a pull request.

### Database Design

The `items` table now has:

```txt
items
├── id
├── user_id
├── name
├── brand
├── category
├── color
└── size
```

The relationship is:

```txt
users.id → items.user_id
```

Meaning:

```txt
One user can own many items.
Each item belongs to one user.
```

### Shared Table, Private Inventory

Suot still uses one shared `items` table.

It does not create separate tables like:

```txt
jim_items
alex_items
mia_items
```

Instead, every item row has a `user_id`.

Example:

```txt
items
├── id: 1  user_id: 1  name: Saturn LA Shirt
├── id: 2  user_id: 1  name: Onitsuka Tigers
├── id: 3  user_id: 2  name: Black Hoodie
└── id: 4  user_id: 2  name: Denim Jacket
```

The database is shared, but the API filters by the authenticated user.

Simple analogy:

```txt
Shared closet = items table
Ownership tag = user_id
Door rule = only show items where user_id == current_user.id
```

### Why `user_id` Is Used Instead of Username

Items are linked to users through `user_id`, not `username`.

Reason:

```txt
user_id is stable.
username can change.
```

If a user changes their username, their items should still belong to the same account.

Important rule:

```txt
Use user_id for database relationships.
Use username for display, search, and public profile identity.
```

### Client Does Not Send `user_id`

The client should not decide item ownership.

Bad request design:

```json
{
  "user_id": 4,
  "name": "Saturn LA Shirt",
  "brand": "Saturn LA",
  "category": "Shirt",
  "color": "White",
  "size": "M"
}
```

This is unsafe because a malicious user could change `user_id`.

Correct request design:

```json
{
  "name": "Saturn LA Shirt",
  "brand": "Saturn LA",
  "category": "Shirt",
  "color": "White",
  "size": "M"
}
```

The backend gets ownership from the token:

```txt
JWT access token
  ↓
get_current_user()
  ↓
current_user.id
  ↓
item.user_id = current_user.id
```

Ownership comes from authentication, not from client input.

### Route Behavior

#### `POST /items`

Creates an item owned by the current authenticated user.

```txt
POST /items
  ↓
Require Bearer token
  ↓
get_current_user()
  ↓
Create item with user_id = current_user.id
  ↓
Return created item
```

#### `GET /items`

Returns only the current user's items.

```txt
GET /items
  ↓
Require Bearer token
  ↓
get_current_user()
  ↓
Query items where user_id == current_user.id
  ↓
Return current user's inventory
```

#### `GET /items/{item_id}`

Returns one item only if it belongs to the current user.

```txt
Find item where:
  id == item_id
  AND user_id == current_user.id
```

If no matching item is found, return:

```http
404 Not Found
```

#### `PUT /items/{item_id}`

Updates one item only if it belongs to the current user.

```txt
Find item where:
  id == item_id
  AND user_id == current_user.id

If found:
  update item fields

If not found:
  return 404
```

The update request does not allow changing `user_id`.

#### `DELETE /items/{item_id}`

Deletes one item only if it belongs to the current user.

```txt
Find item where:
  id == item_id
  AND user_id == current_user.id

If found:
  delete item

If not found:
  return 404
```

### Why Inaccessible Items Return `404`

If a user tries to access another user's item, the API should return:

```http
404 Not Found
```

instead of:

```http
403 Forbidden
```

Reason:

```txt
403 Forbidden can reveal that the item exists.
404 Not Found says no accessible item was found.
```

Important mindset:

```txt
Do not ask:
  Does item 7 exist?

Ask:
  Does item 7 exist for this current user?
```

### Service Layer Changes

The item service changed from global item operations to owner-scoped operations.

Old mental model:

```txt
get_items()
get_item_by_id(item_id)
create_item(item_data)
update_item(item_id, item_data)
delete_item(item_id)
```

New mental model:

```txt
get_items(db, user_id)
get_item_by_id(db, item_id, user_id)
create_item(db, item_data, user_id)
update_item(db, item_id, item_data, user_id)
delete_item(db, item_id, user_id)
```

The important rule:

```txt
Every item operation receives user_id.
Every item query is scoped to user_id.
```

### Router Layer Changes

The item router now uses:

```txt
get_current_user()
```

This gives item routes access to:

```txt
current_user.id
```

The router handles:

```txt
HTTP request
authentication dependency
current_user
HTTP response
```

The service handles:

```txt
database queries
ownership filtering
CRUD logic
```

Important rule:

```txt
Services should not call Depends().
Services should not import get_current_user().
Services should receive user_id as a plain integer.
```

### Testing Changes

Item tests now need authenticated requests.

Before this phase:

```python
client.post("/items", json={...})
```

After this phase:

```python
client.post(
    "/items",
    json={...},
    headers={"Authorization": "Bearer <token>"},
)
```

The item tests use a helper that:

```txt
registers a test user
logs in as that user
extracts the access token
returns Authorization headers
```

### `401` vs `404`

A key testing lesson:

```txt
No token
  → 401 Not authenticated

Valid token, but item does not exist for this user
  → 404 Item not found
```

The authentication gate happens before item lookup.

### Test Coverage Updated

The item tests now cover authenticated item behavior:

```txt
POST   /items
  → authenticated user can create an owned item

GET    /items
  → authenticated user can list their own items

GET    /items/{item_id}
  → authenticated user can retrieve their own item

GET    /items/999
  → authenticated user receives 404 for a missing item

PUT    /items/{item_id}
  → authenticated user can update their own item

PUT    /items/999
  → authenticated user receives 404 for a missing item

DELETE /items/{item_id}
  → authenticated user can delete their own item

DELETE /items/999
  → authenticated user receives 404 for a missing item
```

### Phase Status

Phase 8 complete at the first level.

Current completed behavior:

```txt
Items have owners.
Item routes require login.
Item creation assigns ownership from current_user.id.
Item reads are scoped to current_user.id.
Item updates are scoped to current_user.id.
Item deletes are scoped to current_user.id.
Item tests pass with authenticated requests.
```

### Next Planned Phase

Next improvement:

```txt
Cross-user authorization tests
```

Planned test cases:

```txt
User A creates an item.
User B cannot retrieve User A's item.
User B cannot update User A's item.
User B cannot delete User A's item.
User B's GET /items does not include User A's item.
```

This will prove that users cannot access each other's private inventory.

---

## Core Notes

### Current Architecture

Suot API currently uses a layered backend structure:

```txt
Router
  ↓
Service
  ↓
SQLAlchemy Session
  ↓
Database
```

The router handles HTTP concerns.

The service handles business logic and database operations.

The SQLAlchemy models define database tables.

The Pydantic schemas define request and response shapes.

The database session handles communication with the database.

### Current Docker Architecture

```txt
Docker Compose
├── api container
│   └── FastAPI app
│
└── db container
    └── PostgreSQL database
```

The API and database are separate services.

The API talks to PostgreSQL through `DATABASE_URL`.

### Current Auth Flow

```txt
/register
  → create account

/login
  → verify credentials
  → create JWT access token

/auth/me
  → consume JWT access token
  → identify current user
```

### Current Item Authorization Flow

```txt
Request to /items
  ↓
Require Bearer token
  ↓
get_current_user()
  ↓
current_user.id
  ↓
Query only rows where item.user_id == current_user.id
```

This means:

```txt
Authentication identifies the user.
Authorization decides which item rows the user can access.
```

### Important Backend Concepts Learned

```txt
FastAPI
  → API framework

Router
  → HTTP route layer

Pydantic schema
  → request and response validation

Service layer
  → application logic and database operations

SQLAlchemy model
  → Python representation of a database table

SQLAlchemy Session
  → active conversation with the database

PostgreSQL
  → persistent relational database server

Alembic
  → version control for database schema changes

Docker
  → container runtime

Docker Compose
  → runs API and database services together

JWT
  → signed access token used to identify logged-in users

Bearer token
  → token sent through the Authorization header

Authentication
  → proves who the user is

Authorization
  → controls what the user can access
```

### `ItemModel`

`ItemModel` is the SQLAlchemy model that defines how an item is represented in the database.

It maps:

```txt
Python class ItemModel
```

to:

```txt
SQL table items
```

Current fields:

```txt
id
user_id
name
brand
category
color
size
```

`user_id` identifies which user owns the item.

Database relationship:

```txt
items.user_id → users.id
```

### `UserModel`

`UserModel` is the SQLAlchemy model that defines how a user account is represented in the database.

It maps:

```txt
Python class UserModel
```

to:

```txt
SQL table users
```

Current fields:

```txt
id
email
username
hashed_password
is_active
created_at
updated_at
```

### `get_db()`

`get_db()` creates a database session for one request, gives it to the route, and closes it after the request finishes.

Flow:

```txt
Request starts
  ↓
get_db() creates session
  ↓
Route/service uses session
  ↓
Request ends
  ↓
get_db() closes session
```

### `Session`

A SQLAlchemy `Session` is the object the application uses to talk to the database.

It can:

```txt
run queries
stage inserts
stage updates
stage deletes
commit transactions
rollback transactions
```

Simple definition:

```txt
Session = active conversation with the database
```

### `db.add()`

```python
db.add(item)
```

Stages a new object for insertion into the database.

It does not permanently save until `db.commit()` is called.

### `db.commit()`

```python
db.commit()
```

Permanently saves pending changes to the database.

Pending changes can include:

```txt
new item inserted
existing item updated
item deleted
new user inserted
```

### `db.refresh()`

```python
db.refresh(item)
```

Reloads the Python object from the database.

This is useful after creating a new item or user because the database generates values like:

```txt
id
created_at
updated_at
```

### `db.delete()`

```python
db.delete(item)
```

Stages an already-loaded object for deletion.

Typical flow:

```txt
Find item.
If item exists, pass it to db.delete().
Call db.commit().
```

### `select()`

```python
select(ItemModel)
```

Builds a database query.

Example owner-scoped item query:

```txt
Select items where ItemModel.user_id == current_user.id
```

### `db.scalar()` vs `db.scalars()`

```python
db.scalar(statement)
```

Executes a SELECT statement and returns one result.

This is useful when only one row is expected.

```python
db.scalars(statement)
```

Executes a SELECT statement and returns multiple model objects.

This is useful when listing rows.

### Alembic

Alembic manages database schema changes over time.

Simple definition:

```txt
Alembic = version control for database schema changes
```

It creates migration files that describe how the database should change.

Example migration actions:

```txt
create table
add column
drop column
create index
add constraint
```

### `alembic upgrade head`

```bash
uv run alembic upgrade head
```

Applies all pending migrations up to the latest migration.

Simple definition:

```txt
alembic upgrade head = update the database to the latest schema version
```

### Request Schemas vs Response Schemas

Request schemas define what the client can send.

Response schemas define what the API is allowed to return.

Example:

```txt
UserCreate
  → request schema
  → contains email, username, password

User
  → response schema
  → contains id, email, username, is_active, created_at, updated_at

Token
  → response schema
  → contains access_token and token_type
```

Important rule:

```txt
Secrets can exist in request schemas when needed.
Secrets should not exist in response schemas.
```

### Password Hashing

Password hashing turns a raw password into a one-way stored value.

Simple flow:

```txt
Raw password
  ↓
hash_password()
  ↓
hashed_password stored in database
```

The backend should never store raw passwords.

Login uses:

```txt
Raw login password
  ↓
verify_password(plain_password, hashed_password)
  ↓
true or false
```

### `security.py`

`security.py` contains low-level security helper functions.

Current functions:

```txt
hash_password()
verify_password()
create_access_token()
decode_access_token()
```

It handles:

```txt
password hashing
password verification
JWT access token creation
JWT access token decoding
```

### `user_service.py`

`user_service.py` contains user-related business and database logic.

Current responsibilities:

```txt
normalize_email()
normalize_username()
get_user_by_email()
get_user_by_username()
get_user_by_id()
create_user()
authenticate_user()
```

### `auth.py`

`auth.py` is the router for authentication-related HTTP endpoints.

Current endpoints:

```http
POST /auth/register
POST /auth/login
GET /auth/me
```

It handles:

```txt
registration HTTP flow
login HTTP flow
Bearer token authentication
current-user route protection
```

### `409 Conflict`

`409 Conflict` means the request is valid, but it conflicts with existing server state.

Current uses:

```txt
Email already registered
Username already taken
```

### `401 Unauthorized`

`401 Unauthorized` means the user failed authentication or did not provide valid authentication credentials.

Current uses:

```txt
Invalid email or password
Could not validate credentials
Missing Bearer token
Expired or invalid token
```

### `404 Not Found`

`404 Not Found` means the requested resource could not be found.

For private user-owned items, Suot also uses `404` when the item exists but does not belong to the current user.

Reason:

```txt
Do not reveal whether another user's private item exists.
```

### JWT

JWT means JSON Web Token.

In this project, JWTs are used as access tokens.

Current token payload includes:

```txt
sub
  → subject
  → user id

exp
  → expiration time
```

Simple definition:

```txt
JWT = signed proof that a user recently logged in
```

Important distinction:

```txt
JWT is encoded and signed.
JWT is not encrypted.
```

The backend can verify whether a token was created by Suot and whether it has been modified.

### Bearer Token

A Bearer token is sent in the HTTP `Authorization` header.

```http
Authorization: Bearer <access_token>
```

Simple definition:

```txt
Bearer token = whoever carries this valid token is treated as authenticated
```

### `get_current_user()`

`get_current_user()` is the reusable authentication dependency.

It converts a valid Bearer token into the current user.

Flow:

```txt
Authorization header
  ↓
OAuth2PasswordBearer extracts token
  ↓
decode_access_token() validates JWT
  ↓
read sub as user id
  ↓
get_user_by_id()
  ↓
return UserModel
```

This is the foundation for protected routes.

### `TestClient`

`TestClient` allows pytest to call the FastAPI app without manually running the server.

Example:

```python
client = TestClient(app)
```

This lets tests make requests like:

```python
client.post("/items", json={...}, headers={...})
client.post("/auth/register", json={...})
client.post("/auth/login", data={...})
client.get("/auth/me", headers={...})
client.put("/items/1", json={...}, headers={...})
client.delete("/items/1", headers={...})
```

Simple definition:

```txt
TestClient = a fake client used to test API endpoints automatically
```

### Test Database

The test database is separate from the development database.

This keeps tests isolated.

```txt
Development database → suot.db
Test database        → test.db
```

Tests should not depend on existing local data.

Each test should be able to run from a clean starting point.

### `app.dependency_overrides`

`app.dependency_overrides` lets the test replace one FastAPI dependency with another.

In this project, tests replace the normal `get_db()` dependency with a test version.

```python
app.dependency_overrides[get_db] = override_get_db
```

This allows the app to use `test.db` during tests instead of `suot.db`.

### `setup_function()`

`setup_function()` runs before each test function.

In this project, it resets the test database:

```python
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
```

This makes each test independent and predictable.

### Git Branching

Git branches allow risky or meaningful changes to happen away from `main`.

Simple definition:

```txt
main = stable project checkpoint
feature branch = safe workspace for one focused change
```

Example:

```bash
git switch main
git pull
git switch -c feature/user-owned-items
```

A good workflow is:

```txt
branch → build → test → commit → push → pull request → merge
```

This keeps the project organized and prevents half-working infrastructure changes from breaking the stable version.

### Pull Requests

A pull request is a formal review step before merging a feature branch into `main`.

Current workflow:

```txt
Create feature branch
  ↓
Build feature
  ↓
Run tests
  ↓
Commit changes
  ↓
Push branch to GitHub
  ↓
Open pull request
  ↓
Review files changed
  ↓
Merge into main
```

This is useful even for a solo project because it creates a professional project history.

### Dockerfile

A `Dockerfile` defines how to build the API image.

Simple definition:

```txt
Dockerfile = build instructions for the API container
```

### Docker Image

A Docker image is a blueprint.

It contains the runtime environment, dependencies, and application code needed to create a container.

Simple definition:

```txt
Image = blueprint for a container
```

### Docker Container

A Docker container is a running instance of an image.

Simple definition:

```txt
Container = running service created from an image
```

In this project:

```txt
suot-api      → running FastAPI container
suot-postgres → running PostgreSQL container
```

### Docker Compose

Docker Compose runs multiple services together.

Simple definition:

```txt
Docker Compose = tool for running multiple containers as one local system
```

In this project, Docker Compose runs:

```txt
api service → FastAPI app
db service  → PostgreSQL database
```

### Docker Volume

A Docker volume stores persistent data outside the container lifecycle.

This matters because containers can be stopped, removed, and recreated.

The PostgreSQL data survives because it is stored in a volume.

Simple definition:

```txt
Volume = persistent storage for container data
```

### `docker compose down` vs `docker compose down -v`

```bash
docker compose down
```

Stops and removes containers, but keeps the database volume.

```bash
docker compose down -v
```

Stops and removes containers and deletes the database volume.

Important rule:

```txt
Use docker compose down for normal shutdowns.
Use docker compose down -v only when intentionally resetting local database data.
```

### Docker Network

Docker Compose creates a network so services can talk to each other.

This is why the API container can connect to the database using:

```txt
db
```

The name `db` comes from the Compose service name:

```yaml
services:
  db:
```

### `localhost` vs `db`

When the API runs locally on the laptop, it connects to PostgreSQL through:

```txt
localhost
```

When the API runs inside Docker Compose, it connects to PostgreSQL through:

```txt
db
```

Reason:

```txt
localhost inside a container means the container itself.
db means the PostgreSQL service on the Docker Compose network.
```

---

## Current Understanding Summary

Suot API currently uses a layered backend structure:

```txt
Router
  ↓
Service
  ↓
SQLAlchemy Session
  ↓
Database
```

The project moved from temporary in-memory storage to persistent SQLite storage.

The project then moved from SQLite to PostgreSQL running as a separate Docker service.

The project now runs with Docker Compose using an API container and a PostgreSQL container.

The project uses Alembic for database migrations, which means schema changes are versioned, explicit, and applied intentionally.

The project supports user registration with hashed passwords.

The project supports login with JWT access tokens.

The project supports `/auth/me`, which identifies the current authenticated user from a Bearer token.

The project supports user-owned inventory.

Items are no longer global anonymous records.

Each item has:

```txt
user_id
```

which links it to the user who owns it.

The current item authorization flow is:

```txt
Request to /items
  ↓
Require Bearer token
  ↓
get_current_user()
  ↓
current_user.id
  ↓
Query only rows where item.user_id == current_user.id
```

This means:

```txt
Authentication identifies the user.
Authorization decides which item rows the user can access.
```

The next major backend improvement is stronger cross-user authorization testing:

```txt
User A creates item
  ↓
User B tries to access it
  ↓
API returns 404
```

This will prove that users cannot access each other's private inventory.