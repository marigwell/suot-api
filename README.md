# Suot API

Suot API is a backend engineering project for building a fashion inventory and recommendation system.

The goal of this project is to deeply understand backend API development, including REST design, service-layer architecture, database persistence, automated testing, application configuration, Docker, PostgreSQL, Alembic migrations, authentication, authorization, user-owned data, and future recommendation logic.

---

## Tech Stack

- Python
- FastAPI
- Pydantic
- pydantic-settings
- SQLAlchemy
- SQLite
- PostgreSQL
- Alembic
- Docker
- Docker Compose
- uv
- pytest
- ruff
- Git
- email-validator
- python-multipart
- PyJWT
- pwdlib / Argon2 password hashing

---

## Current Features

- Health check endpoint
- Item CRUD endpoints
- Optional `brand` field on items
- User-owned item inventory
- `items.user_id` ownership field
- Foreign key from `items.user_id` to `users.id`
- Protected item routes
- Item routes scoped to the current authenticated user
- Cross-user authorization tests
- User database model
- User request and response schemas
- User registration endpoint
- Password hashing for registered users
- Duplicate email validation
- Duplicate username validation
- User login endpoint
- OAuth2 password form login support
- JWT access token creation
- JWT access token decoding and validation
- Protected current-user endpoint with `GET /auth/me`
- Bearer token authentication through the `Authorization` header
- Safe user responses that do not expose passwords or password hashes
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
- Alembic database migrations
- Versioned database schema changes
- Initial migration for the `items` table
- Schema migration for adding `brand` to items
- Schema migration for creating the `users` table
- Schema migration for adding ownership to items

---

## API Endpoints

### Health

```http
GET /health
```

### Auth

```http
POST /auth/register
POST /auth/login
GET /auth/me
```

### Items

Item routes are protected.

A client must send:

```http
Authorization: Bearer <access_token>
```

Current item endpoints:

```http
GET /items
POST /items
GET /items/{item_id}
PUT /items/{item_id}
DELETE /items/{item_id}
```

---

## Auth Endpoints

### Register

```http
POST /auth/register
```

Current registration request body:

```json
{
  "email": "jim@example.com",
  "username": "jim",
  "password": "password123"
}
```

Current registration response body:

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

The API does not return:

```txt
password
hashed_password
```

### Login

```http
POST /auth/login
```

`POST /auth/login` uses OAuth2 password form data.

In Swagger, the login form uses:

```txt
username
password
```

For Suot, the `username` field is treated as the user's email address.

Example:

```txt
username: jim@example.com
password: password123
```

Current login response body:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Current User

```http
GET /auth/me
```

`GET /auth/me` is a protected route.

The client must send the JWT access token through the authorization header:

```http
Authorization: Bearer <access_token>
```

Current `/auth/me` response body:

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

---

## Item Endpoints

All item endpoints require authentication.

### Create Item

```http
POST /items
```

Current request body:

```json
{
  "name": "Saturn LA Shirt",
  "brand": "Saturn LA",
  "category": "Shirt",
  "color": "White",
  "size": "M"
}
```

The client does not send `user_id`.

The backend assigns ownership from the authenticated user:

```txt
current_user.id → item.user_id
```

Current response body:

```json
{
  "id": 1,
  "user_id": 1,
  "name": "Saturn LA Shirt",
  "brand": "Saturn LA",
  "category": "Shirt",
  "color": "White",
  "size": "M"
}
```

### List Items

```http
GET /items
```

Returns only items owned by the current authenticated user.

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

### Get Item by ID

```http
GET /items/{item_id}
```

Returns one item only if it belongs to the current authenticated user.

Query rule:

```txt
item.id == item_id
AND
item.user_id == current_user.id
```

If no accessible item is found, the API returns:

```http
404 Not Found
```

### Update Item

```http
PUT /items/{item_id}
```

Updates one item only if it belongs to the current authenticated user.

The update request does not allow changing `user_id`.

### Delete Item

```http
DELETE /items/{item_id}
```

Deletes one item only if it belongs to the current authenticated user.

---

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

The project uses a layered backend structure.

```txt
Router
  → HTTP routes, request handling, dependencies, status codes

Schema
  → request and response validation

Service
  → business logic and database operations

Model
  → database table shape

Database session
  → active connection between app logic and database
```

---

## Current Auth Flow

### Registration Flow

```txt
POST /auth/register
  ↓
Client sends email, username, and password
  ↓
Pydantic validates the request body
  ↓
Auth router receives the request
  ↓
User service checks for duplicate email
  ↓
User service checks for duplicate username
  ↓
Password is hashed with Argon2
  ↓
UserModel is created with hashed_password
  ↓
SQLAlchemy saves the user row
  ↓
API returns a safe User response
```

Important rule:

```txt
The client sends a raw password during registration.
The backend never stores the raw password.
The backend stores only hashed_password.
The API never returns password or hashed_password.
```

### Login Flow

```txt
POST /auth/login
  ↓
Client sends email and password as OAuth2 form data
  ↓
Backend finds user by email
  ↓
Backend verifies the raw password against hashed_password
  ↓
If valid, backend creates a JWT access token
  ↓
API returns access_token and token_type
```

Important rule:

```txt
The password proves identity during login.
The JWT proves identity on future requests.
```

### Current User Flow

```txt
GET /auth/me
  ↓
Client sends Authorization: Bearer <access_token>
  ↓
OAuth2PasswordBearer extracts the token
  ↓
Backend decodes and verifies the JWT
  ↓
Backend reads sub from the token payload
  ↓
sub is treated as the user id
  ↓
Backend finds the user in PostgreSQL
  ↓
API returns the current user
```

Important rule:

```txt
Login creates the token.
/auth/me consumes the token.
```

---

## Current Item Authorization Flow

Item routes now use authentication and authorization.

Authentication answers:

```txt
Who are you?
```

Authorization answers:

```txt
What data are you allowed to access?
```

Current implementation:

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
Authorization scopes item access to that user.
```

For Suot, the core rule is:

```txt
item.user_id == current_user.id
```

---

## Database Design

### `items`

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

`user_id` identifies which user owns the item.

Database relationship:

```txt
items.user_id → users.id
```

Meaning:

```txt
One user can own many items.
Each item belongs to one user.
```

### `users`

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

Current design distinction:

```txt
email
  → private login identifier

username
  → public/searchable identity for future profile features

hashed_password
  → stored password hash, never plaintext password
```

---

## User-Owned Inventory Design

Suot uses one shared `items` table.

It does not create separate item tables per user.

Bad design:

```txt
jim_items
alex_items
mia_items
```

Better design:

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

### Why the Client Does Not Send `user_id`

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

Ownership comes from authentication, not from client input.

```txt
JWT access token
  ↓
get_current_user()
  ↓
current_user.id
  ↓
item.user_id = current_user.id
```

### Why Inaccessible Items Return `404`

If a user tries to access another user's item, the API returns:

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

---

## Cross-User Authorization Testing

Suot includes tests that prove item ownership isolation across users.

The main tested scenario is:

```txt
Create User A
Create User B
User A creates an item
User B tries to access User A's item
API denies access
```

The authorization tests prove:

```txt
User B does not see User A's item in GET /items.
User B cannot retrieve User A's item by ID.
User B cannot update User A's item.
User B cannot delete User A's item.
```

This matters because user-owned inventory is a security boundary.

The backend does not only test that authenticated CRUD works.

It also tests that authenticated users cannot access each other's private item data.

---

## Auth Design

Current authentication design:

```txt
Authentication
  → Who are you?

Authorization
  → What data are you allowed to access?
```

Current implementation:

```txt
/register
  → creates identity

/login
  → proves identity and returns JWT

/auth/me
  → uses JWT to identify current user

/items
  → uses current_user.id to scope item access
```

JWT payload currently includes:

```txt
sub
  → subject
  → user id

exp
  → expiration time
  → token stops being valid after this time
```

The token is signed with the app secret key.

```txt
JWT is encoded and signed, not encrypted.
The backend can verify whether the token was created by Suot and whether it has expired.
```

---

## Layer Responsibilities

### Models

Models define how data is stored in the database.

```txt
app/models/
├── item.py
└── user.py
```

Example:

```txt
UserModel
  → users table

ItemModel
  → items table
```

### Schemas

Schemas define how data enters and leaves the API.

```txt
app/schemas/
├── item.py
└── user.py
```

Examples:

```txt
ItemCreate
  → item creation and update request body

Item
  → item response body

UserCreate
  → registration request body

User
  → safe user response body

Token
  → login response body
```

Important rule:

```txt
Request schemas can contain secrets when needed.
Response schemas should not contain secrets.
```

Important item rule:

```txt
ItemCreate does not contain user_id.
Item responses can include user_id.
```

### Services

Services contain business and database logic.

```txt
app/services/
├── item_service.py
└── user_service.py
```

Examples:

```txt
create_user()
authenticate_user()
get_user_by_email()
get_user_by_id()
create_item()
get_items()
get_item_by_id()
update_item()
delete_item()
```

Item services receive `user_id` as a plain integer.

Important rule:

```txt
Services should not call Depends().
Services should not import get_current_user().
Services should receive user_id from the router.
```

### Routers

Routers define HTTP endpoints and HTTP behavior.

```txt
app/routers/
├── auth.py
├── health.py
└── items.py
```

Examples:

```txt
POST /auth/register
POST /auth/login
GET /auth/me
GET /items
POST /items
```

Routers handle:

```txt
HTTP requests
FastAPI dependencies
current_user
status codes
HTTP exceptions
response models
```

### Security

`app/security.py` contains low-level security helpers.

Current responsibilities:

```txt
hash_password()
verify_password()
create_access_token()
decode_access_token()
```

---

## Docker Architecture

The application can run with Docker Compose.

```txt
Docker Compose
├── api
│   └── FastAPI app
│       └── runs on container port 8000
│
└── db
    └── PostgreSQL database
        └── stores application data
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

This means Suot can run locally as a containerized backend system.

---

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
localhost → used when the API or Alembic runs from the laptop
db        → used when the API runs inside Docker Compose
```

---

## Auth Configuration

Authentication settings are controlled through environment variables.

Example:

```env
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Current meaning:

```txt
SECRET_KEY
  → used to sign and verify JWT access tokens

ALGORITHM
  → JWT signing algorithm

ACCESS_TOKEN_EXPIRE_MINUTES
  → how long an access token remains valid
```

Production warning:

```txt
The development secret key should not be used in production.
Production secrets should come from secure environment variables or a secret manager.
```

---

## Database Migrations

Suot API uses Alembic to manage database schema changes.

Before Alembic, the app used SQLAlchemy's `Base.metadata.create_all()` to create tables automatically when the API started.

That was useful for learning, but it is not ideal for a growing backend project because schema changes should be explicit, versioned, and reviewable.

Current migration flow:

```txt
Change SQLAlchemy model
  ↓
Generate Alembic migration
  ↓
Review migration file
  ↓
Apply migration
  ↓
PostgreSQL schema updates
```

Create a migration:

```bash
uv run alembic revision --autogenerate -m "migration message"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Check the current migration version in PostgreSQL:

```sql
SELECT * FROM alembic_version;
```

Alembic currently manages schema changes for:

```txt
items table creation
brand column added to items
users table creation
user ownership added to items
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
├── env.py
├── script.py.mako
└── versions/
    ├── <revision>_create_items_table.py
    ├── <revision>_add_brand_to_items.py
    ├── <revision>_create_users_table.py
    └── <revision>_add_user_ownership_to_items.py

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
uv.lock
```

---

## Running Locally Without Docker

Install dependencies:

```bash
uv sync
```

Create a local `.env` file:

```env
DATABASE_URL=sqlite:///./suot.db
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Run migrations:

```bash
uv run alembic upgrade head
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

---

## Running with Docker Compose

Start the PostgreSQL database:

```bash
docker compose up -d db
```

Run database migrations:

```bash
uv run alembic upgrade head
```

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

Reset the local PostgreSQL database volume only when intentionally starting fresh:

```bash
docker compose down -v
```

Important:

```txt
docker compose down
  → stops containers but keeps database data

docker compose down -v
  → stops containers and deletes the database volume
```

---

## Testing with Swagger

Open:

```txt
http://localhost:8000/docs
```

Current manual auth flow:

```txt
1. POST /auth/register
2. POST /auth/login
3. Copy access_token
4. Click Authorize
5. Paste the token
6. Run GET /auth/me
7. Use protected /items routes
```

In Swagger's OAuth2 authorize popup:

```txt
username
  → enter the user's email address

password
  → enter the user's password

client_id
  → leave blank

client_secret
  → leave blank
```

After authorization, Swagger sends:

```http
Authorization: Bearer <access_token>
```

---

## Automated Testing

Local automated tests are run with:

```bash
uv run pytest
```

Current tests run locally and use an isolated test database.

```txt
pytest locally
  → tests CRUD behavior, auth behavior, and route/service logic

Docker Compose manually
  → tests the containerized API and PostgreSQL runtime
```

The current automated test suite covers:

```txt
POST   /auth/register
POST   /auth/register duplicate email
POST   /auth/register duplicate username
POST   /auth/login with valid credentials
POST   /auth/login with wrong password
GET    /auth/me with valid token
GET    /auth/me without token

POST   /items with authenticated user
GET    /items with authenticated user
GET    /items/{item_id} with authenticated user
GET    /items/999 with authenticated user
PUT    /items/{item_id} with authenticated user
PUT    /items/999 with authenticated user
DELETE /items/{item_id} with authenticated user
DELETE /items/999 with authenticated user

GET    /items does not show another user's items
GET    /items/{item_id} rejects another user's item
PUT    /items/{item_id} rejects another user's item
DELETE /items/{item_id} rejects another user's item
```

Next planned tests:

```txt
Tests for richer item fields
Tests for item analytics
Tests for filtering, sorting, and pagination
```

---

## Git Workflow

`main` should represent the stable working version of the project.

Feature branches should be used for meaningful backend, database, Docker, authentication, authorization, or infrastructure changes.

### Basic Workflow

```txt
branch → build → test → commit → push → pull request → merge
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

Open a pull request on GitHub:

```txt
base: main
compare: feature/example-name
```

Review the changed files.

Merge the pull request after the feature works.

Sync local `main` after merging:

```bash
git switch main
git pull
```

### Branch Naming

```txt
feature/postgres-setup
feature/dockerize-api
feature/alembic-migrations
feature/add-item-brand
feature/user-model
feature/user-registration
feature/user-login
feature/auth-me
feature/user-owned-items
feature/item-details
feature/closet-analytics
feature/item-filtering-pagination
feature/recommendations
fix/item-not-found
docs/update-devlog
test/item-service-tests
test/auth-tests
test/item-authorization
```

### Git Rules

```txt
Use main for stable checkpoints.
Use feature branches for meaningful changes.
Use pull requests to review feature work before merging.
Do not commit .env files.
Do not commit local database files.
Do not commit Python cache files.
Run tests before committing.
Test Docker changes with docker compose ps and Swagger.
Merge only after the feature works.
```

---

## Roadmap

### Chapter 1 — Backend Foundations

- Phase 1: In-memory item CRUD — DONE
- Phase 2: SQLite persistence with SQLAlchemy — DONE
- Phase 3: Code review, cleanup, and item CRUD tests — DONE
- Phase 4A: Environment-based app configuration — DONE
- Phase 4B: Local PostgreSQL setup with Docker — DONE
- Phase 5: Dockerize the FastAPI API — DONE
- Phase 6A: Alembic setup and initial migration — DONE
- Phase 6B: Schema evolution with `brand` field — DONE

### Chapter 2 — Authentication and User-Owned Data

- Phase 7A: User model and users table migration — DONE
- Phase 7B: User registration — DONE
- Phase 7C: Login and JWT access tokens — DONE
- Phase 7D: Protected auth route with `/auth/me` — DONE
- Phase 7E: Auth tests for login and `/auth/me` — DONE
- Phase 8: User-owned item inventory — DONE
- Phase 8B: Cross-user authorization tests — DONE

### Chapter 3 — Product-Grade Inventory API

- Phase 9: Richer item fields such as price, purchase date, condition, and notes — NEXT
- Phase 10: Closet analytics endpoint
- Phase 11: Item filtering, sorting, and pagination
- Phase 12: API validation and error-handling polish

### Chapter 4 — CI, Deployment, and Release Workflow

- Phase 13: GitHub Actions CI checks
- Phase 14: Production-ready environment configuration
- Phase 15: Initial deployment
- Phase 16: Deployment documentation and release checklist

### Chapter 5 — Intelligence and Personalization

- Phase 17: Rule-based wardrobe recommendations
- Phase 18: Outfit generation logic
- Phase 19: Wardrobe gap analysis
- Phase 20: Spending insights and duplicate-purchase warnings
- Phase 21: Recommendation feedback loop

### Chapter 6 — Production Hardening and Scale

- Phase 22: PostgreSQL integration tests
- Phase 23: Redis caching
- Phase 24: Rate limiting
- Phase 25: Structured logging and observability
- Phase 26: Background jobs
- Phase 27: Performance testing

### Future Chapters

- Event-driven analytics
- Image uploads and object storage
- Search and indexing
- Refresh tokens and account security
- Multi-service recommendation architecture
- Public profiles and social wardrobe features

---

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
Alembic migrations
schema evolution
database versioning
nullable columns
foreign keys
user-owned data
row-level authorization
cross-user authorization testing
Docker images
Docker containers
Docker Compose services
Docker volumes
Git branching
pull request workflow
local infrastructure with Docker
password hashing
safe response schemas
duplicate account validation
OAuth2 password flow
Bearer token authentication
JWT access tokens
JWT token creation
JWT token decoding
current-user dependencies
authentication design
authorization design
```

---

## Current Project Status

Completed backend foundation:

```txt
FastAPI app structure
health endpoint
item CRUD
SQLite persistence
PostgreSQL support
Dockerized API
Dockerized database
Docker Compose setup
Alembic migrations
brand field migration
users table migration
user registration
password hashing
user login
JWT access tokens
/auth/me
auth tests
user-owned item inventory
protected item routes
authenticated item tests
cross-user authorization tests
```

Current item authorization behavior:

```txt
Items have owners.
Item routes require login.
Item creation assigns ownership from current_user.id.
Item reads are scoped to current_user.id.
Item updates are scoped to current_user.id.
Item deletes are scoped to current_user.id.
Users cannot access another user's item even if they know the item ID.
```

Next planned backend work:

```txt
Richer item fields
  → price
  → purchase_date
  → condition
  → notes

Closet analytics
  → total closet value
  → item counts by category
  → item counts by brand
  → spending insight

Recommendation logic
  → recommend outfits or items based on inventory data
```

Long-term design direction:

```txt
Authentication
  → Who are you?

Authorization
  → What data are you allowed to access?

Inventory analytics
  → What does your closet contain?

Recommendation
  → What useful insight can the system generate from your inventory?
```