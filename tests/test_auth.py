from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app


TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "email": "jim@example.com",
            "username": "jim",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "jim@example.com"
    assert data["username"] == "jim"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_user_duplicate_email():
    first_response = client.post(
        "/auth/register",
        json={
            "email": "jim@example.com",
            "username": "jim",
            "password": "password123",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/register",
        json={
            "email": "jim@example.com",
            "username": "jimtwo",
            "password": "password123",
        },
    )

    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "Email already registered"}


def test_register_user_duplicate_username():
    first_response = client.post(
        "/auth/register",
        json={
            "email": "jim@example.com",
            "username": "jim",
            "password": "password123",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/register",
        json={
            "email": "jimtwo@example.com",
            "username": "jim",
            "password": "password123",
        },
    )

    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "Username already taken"}
