# Suot API Development Log

This file tracks the learning process, design decisions, and backend concepts explored while building Suot API.

## Day 1 — FastAPI Foundation

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

---

## Day 2 — In-Memory CRUD

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

### PUT Algorithm

```txt
Receive item_id and updated item data

Loop through every item in inventory

If current item ID matches item_id:
    Replace the old item with updated data
    Return the updated item

If no item is found:
    Return None
```

### Why `enumerate()` Was Used

`enumerate()` gives access to both:

```txt
index
item
```

This matters because updating an item in a list requires knowing where the item is located.

Example:

```python
for index, item in enumerate(items):
    ...
```

### DELETE Algorithm

```txt
Receive item_id

Loop through every item in inventory

If current item ID matches item_id:
    Remove the item from the list using its index
    Return success

If no item is found:
    Return failure
```

### ID Design Decision

IDs should not be reused after deletion.

Reason:

```txt
IDs represent stable record identity.
If an old ID is reused, historical references such as orders, favorites, logs, or audit records could accidentally point to the wrong item.
```

### Phase 1 Status

Phase 1 complete: In-memory item CRUD finished.

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
db.add()    → prepare the change
db.commit() → save the change
```

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

This stored data only in memory.

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

### Phase 2 Status

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

### Test Folder Structure

```txt
suot-api/
├── app/
├── tests/
│   └── test_items.py
├── pyproject.toml
└── README.md
```

The `app/` folder contains the actual application.

The `tests/` folder contains code that checks whether the application works correctly.

### pytest Configuration

Added this to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

This tells pytest:

```txt
Use the project root as an import path.
Look for tests inside the tests folder.
```

This fixed the issue where pytest could not import:

```python
from app.main import app
```

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

### Test Result

```txt
8 passed
```

### Phase 3B Status

Phase 3B complete: item CRUD API is now covered by automated tests.

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
- Verified that the Docker CLI works.
- Created `docker-compose.yml`.
- Ran PostgreSQL inside Docker.
- Connected the local FastAPI app to the PostgreSQL container.
- Verified PostgreSQL data directly with `psql`.
- Created a feature branch for PostgreSQL setup.
- Created a feature branch for Dockerizing the API.
- Created a `Dockerfile` for the FastAPI API.
- Created a `.dockerignore` file.
- Updated Docker Compose to run both the API and database.
- Built and ran the API container.
- Confirmed `docker compose ps` shows both `suot-api` and `suot-postgres` running.
- Confirmed Swagger works through `http://localhost:8000/docs`.
- Confirmed item CRUD works through the Dockerized API.

### Why Configuration Matters

Before this step, the database URL was hardcoded in `database.py`.

That meant the app was directly tied to one database setup.

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

At first, only PostgreSQL was running in Docker.

```txt
Laptop
├── FastAPI app running locally with uvicorn
└── Docker
    └── PostgreSQL container
```

In that setup, the API connected to PostgreSQL with:

```env
DATABASE_URL=postgresql+psycopg://suot:suot@localhost:5432/suot
```

Then the API was containerized too.

```txt
Docker Compose
├── api container
│   └── FastAPI app
│
└── db container
    └── PostgreSQL database
```

In this setup, the API connects to PostgreSQL with:

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

### Amazon Warehouse Analogy

The PostgreSQL database is like a warehouse.

The item rows are like packages.

The database tables are like shelves.

The FastAPI API is like the delivery system that decides how packages are created, read, updated, and deleted.

When only PostgreSQL was in Docker, the warehouse was containerized but the delivery system was still running locally.

After Dockerizing the API, both the delivery system and warehouse run inside Docker Compose.

```txt
Docker Compose
├── delivery system → FastAPI API container
└── warehouse       → PostgreSQL database container
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

The current tests are still useful because they protect CRUD behavior.

However, they are not Docker integration tests yet.

### Git Branching Lesson

`main` should represent the stable version of the project.

Feature branches should be used for meaningful work that could break the app.

Examples:

```txt
feature/postgres-setup
feature/dockerize-api
feature/auth
feature/user-inventory
```

The basic sequence is:

```txt
branch → build → test → commit → merge → push
```

For PostgreSQL setup:

```txt
feature/postgres-setup
  ↓
Run PostgreSQL in Docker
  ↓
Connect local FastAPI app to PostgreSQL
  ↓
Test with Swagger and psql
  ↓
Commit and merge into main
```

For Dockerizing the API:

```txt
feature/dockerize-api
  ↓
Create Dockerfile
  ↓
Create .dockerignore
  ↓
Add api service to docker-compose.yml
  ↓
Run docker compose up --build
  ↓
Test localhost:8000/docs
  ↓
Commit and merge into main
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

### Final Checkpoint

By the end of this phase, Suot could run as a local containerized backend system.

Confirmed working:

```txt
docker compose ps shows:
- suot-api running
- suot-postgres running
```

http://localhost:8000/docs opens Swagger UI

POST /items works through the Dockerized API

GET /items returns data from PostgreSQL

PostgreSQL stores the item rows inside the Dockerized database service

### Phase 4B Status

Phase 4B complete: PostgreSQL now runs locally through Docker.

### Phase 5 Status

Phase 5 complete: the FastAPI API now runs in Docker with PostgreSQL through Docker Compose.

---

## Day 7 — Alembic Migrations and Schema Evolution

### Goal

Replace automatic table creation with versioned database migrations, then prove that the database schema can evolve safely over time.

### Work Completed

- Installed Alembic.
- Initialized an Alembic migration environment.
- Added `alembic.ini`.
- Added the `alembic/` folder with `env.py`, `script.py.mako`, and `versions/`.
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

`head` means the latest migration version.

### First Migration

The first migration created the `items` table.

The migration contained an `upgrade()` function and a `downgrade()` function.

```txt
upgrade()   → apply the schema change
downgrade() → undo the schema change
```

For the initial migration:

```txt
upgrade()   → create items table
downgrade() → drop items table
```

After running:

```bash
uv run alembic upgrade head
```

PostgreSQL had the `items` table created through Alembic.

This means Alembic became responsible for database schema management instead of FastAPI startup code.

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

This prevents Alembic from rerunning migrations that were already applied.

### Proving Schema Evolution

To prove Alembic worked beyond the first migration, a new `brand` field was added to items.

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

The service layer was updated so create and update operations handle `brand`.

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

This made the migration safe for existing data.

### Result

Old row:

```json
{
  "name": "Never Content Anniversary RX-7 Shirt",
  "brand": null,
  "category": "Shirt",
  "color": "Gray",
  "size": "M"
}
```

New row:

```json
{
  "name": "Starfall Tour Shirt",
  "brand": "Saturn LA",
  "category": "Shirt",
  "color": "White",
  "size": "M"
}
```

This confirmed:

```txt
Old items can keep brand as null.
New items can store a brand value.
The API returns the brand field.
PostgreSQL has the new brand column.
Alembic successfully evolved the existing schema.
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

The `-v` flag removes the saved PostgreSQL data volume.

That means local rows, tables, and database state are deleted.

This is acceptable for local development resets, but it should be used carefully because it deletes database data.

### Git Cleanup Lesson

Some Python cache files were already tracked by Git.

Even though `.gitignore` included:

```gitignore
__pycache__/
*.pyc
```

Git still tracked cache files that had been committed earlier.

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

### Phase 6A Status

Phase 6A complete: Alembic is installed, configured, and managing the initial PostgreSQL schema.

### Phase 6B Status

Phase 6B complete: Alembic successfully updated an existing table by adding the optional `brand` column to items.

---

## Core Notes

### `database.py`

`database.py` sets up the SQLAlchemy database connection.

It creates:

```txt
engine
SessionLocal
Base
get_db()
```

It is responsible for database infrastructure, not item logic.

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

Simple definition:

```txt
ItemModel = blueprint for the items table
```

Current fields:

```txt
id
name
brand
category
color
size
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

### `db.get()`

```python
db.get(ItemModel, item_id)
```

Finds one row by primary key.

Example:

```txt
Find the item where id == item_id
```

### `select()`

```python
select(ItemModel)
```

Builds a database query.

Current use:

```txt
Select all items from the items table
```

Future use:

```python
select(ItemModel).where(ItemModel.category == "jacket")
```

This would select only items where the category is `"jacket"`.

### `db.scalars()`

```python
db.scalars(statement)
```

Executes a SELECT statement and returns the model objects from the result.

Full pattern:

```python
list(db.scalars(select(ItemModel)).all())
```

Meaning:

```txt
Build query
Run query
Get all ItemModel objects
Convert result into a Python list
```

### `db.add()`

```python
db.add(item)
```

Stages a new object for insertion into the database.

It does not permanently save until `db.commit()` is called.

### Field Assignment

Example:

```python
item.name = item_data.name
item.brand = item_data.brand
item.category = item_data.category
item.color = item_data.color
item.size = item_data.size
```

This changes the values on an existing database object.

SQLAlchemy tracks those changes.

When `db.commit()` is called, the updated values are saved to the database.

### `db.delete()`

```python
db.delete(item)
```

Stages an already-loaded object for deletion.

Typical flow:

```txt
Find item with db.get()
If item exists, pass it to db.delete()
Call db.commit()
```

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
```

### `db.refresh()`

```python
db.refresh(item)
```

Reloads the Python object from the database.

This is useful after creating a new item because the database generates values like:

```txt
id
```

After `db.refresh(item)`, Python has the latest version of that object.

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

### Alembic Migration

An Alembic migration is a versioned file that changes the database schema.

Migration files live in:

```txt
alembic/versions/
```

Each migration has:

```txt
revision ID
down_revision
upgrade()
downgrade()
```

Simple meaning:

```txt
upgrade()   → apply the database change
downgrade() → undo the database change
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

### `alembic_version`

`alembic_version` is a table created by Alembic.

It stores the current migration version applied to the database.

This lets Alembic know which migrations have already run.

### Nullable Columns

A nullable column allows a database value to be empty.

In PostgreSQL, this empty value is:

```txt
NULL
```

For the `brand` field:

```python
brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
```

This means:

```txt
brand can be a string
or
brand can be None / NULL
```

This was important because old rows already existed before the `brand` column was added.

### `TestClient`

`TestClient` allows pytest to call the FastAPI app without manually running the server.

Example:

```python
client = TestClient(app)
```

This lets tests make requests like:

```python
client.post("/items", json={...})
client.get("/items")
client.put("/items/1", json={...})
client.delete("/items/1")
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
git switch -c feature/dockerize-api
```

A good workflow is:

```txt
branch → build → test → commit → merge → push
```

This keeps the project organized and prevents half-working infrastructure changes from breaking the stable version.

### Dockerfile

A `Dockerfile` defines how to build the API image.

Simple definition:

```txt
Dockerfile = build instructions for the API container
```

In this project, the Dockerfile starts from a Python image, installs dependencies with `uv`, copies the app code, and starts FastAPI with Uvicorn.

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

The router handles HTTP concerns.

The service handles item logic.

The SQLAlchemy model defines the database table.

The database session handles communication with the database.

Pydantic schemas define the shape of incoming and outgoing API data.

The project moved from temporary in-memory storage to persistent SQLite storage.

The project then moved from SQLite to PostgreSQL running as a separate Docker service.

The project now has automated tests for item CRUD endpoints, which means the API behavior can be verified with pytest instead of only through manual Swagger testing.

The project also has an application configuration layer, which allows the database backend to change through `DATABASE_URL` without rewriting the router or service layer.

The project can now run through Docker Compose with both the FastAPI API and PostgreSQL database as separate containers.

The project now uses Alembic for database migrations, which means schema changes are versioned, explicit, and applied intentionally instead of being created automatically on app startup.

The project successfully proved schema evolution by adding an optional `brand` column to the existing `items` table.

Current Docker architecture:

```txt
Docker Compose
├── api container
│   └── FastAPI app
│
└── db container
    └── PostgreSQL database
```

The project now uses Git branches for larger changes.

The current Git workflow is:

```txt
branch → build → test → commit → merge → push
```

The most important system design lesson so far is that backend systems are made of separate services that communicate through defined interfaces.

FastAPI handles the API behavior.

PostgreSQL stores the data.

Alembic manages database schema changes.

Docker Compose runs the services together in a reproducible local environment.

Git branches keep major changes isolated until they are tested and ready to merge.