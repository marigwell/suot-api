# Suot API

Suot API is a backend engineering project for building a fashion inventory and recommendation system.

The goal of this project is to deeply understand backend API development, including REST design, service-layer architecture, database persistence, automated testing, application configuration, Docker, PostgreSQL, Alembic migrations, authentication, user-owned data, and recommendation logic.

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

## Current Features

- Health check endpoint
- Item CRUD endpoints
- Optional `brand` field on items
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

#### Register

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

#### Login

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

#### Current User

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

## Database Design

### `items`

```txt
items
├── id
├── name
├── brand
├── category
├── color
└── size
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

### Security

`app/security.py` contains low-level security helpers.

Current responsibilities:

```txt
hash_password()
verify_password()
create_access_token()
decode_access_token()
```

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

## Database Migrations

Suot API uses Alembic to manage database schema changes.

Before Alembic, the app used SQLAlchemy’s `Base.metadata.create_all()` to create tables automatically when the API started.

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
```

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
    └── <revision>_create_users_table.py

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

## Automated Testing

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

POST   /auth/register
POST   /auth/register duplicate email
POST   /auth/register duplicate username
```

Planned auth tests:

```txt
POST   /auth/login with valid credentials
POST   /auth/login with invalid password
GET    /auth/me with valid token
GET    /auth/me without token
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
feature/alembic-migrations
feature/add-item-brand
feature/user-model
feature/user-registration
feature/user-login
feature/auth-me
feature/user-inventory
feature/recommendations
fix/item-not-found
docs/update-devlog
test/item-service-tests
test/auth-tests
```

### Git Rules

```txt
Use main for stable checkpoints.
Use feature branches for meaningful changes.
Do not commit .env files.
Do not commit local database files.
Do not commit Python cache files.
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
- Phase 6A: Alembic setup and initial migration — DONE
- Phase 6B: Schema evolution with `brand` field — DONE
- Phase 7A: User model and users table migration — DONE
- Phase 7B: User registration — DONE
- Phase 7C: Login and JWT access tokens — DONE
- Phase 7D: Protected auth route with `/auth/me` — DONE
- Phase 7E: Auth tests for login and `/auth/me`
- Phase 8: User-owned item inventory
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
Alembic migrations
schema evolution
database versioning
nullable columns
Docker images
Docker containers
Docker Compose services
Docker volumes
Git branching
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
```

## Current Auth Status

Completed auth foundation:

```txt
UserModel
User schemas
users table migration
password hashing helper
POST /auth/register
POST /auth/login
JWT access token creation
JWT access token decoding
GET /auth/me
registration tests
```

Next planned auth work:

```txt
POST /auth/login tests
GET /auth/me tests
```

Next planned backend feature:

```txt
User-owned inventory
  → add user_id to items
  → protect item routes
  → only return items owned by current_user.id
```

The long-term authentication design is:

```txt
Authentication
  → Who are you?

Authorization
  → What data are you allowed to access?
```

For Suot, that means:

```txt
JWT identifies the current user.
user_id scopes item access.
Users should only read, update, and delete their own items.
```