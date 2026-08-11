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


def test_login_user_returns_token():
    """
    Test that a registered user can log in and receive a token.
    """

    # register a user first
    register_response = client.post(
        "/auth/register",
        json={
            "email": "jim@example.com",
            "username": "jim",
            "password": "password123",
        },
    )

    # verify user registration
    assert register_response.status_code == 201

    # now attempt to log in with the registered user's credentials
    login_response = client.post(
        "/auth/login",
        data={
            "username": "jim@example.com",
            "password": "password123",
        },
    )

    # verify that the login was successful and a token was returned
    assert login_response.status_code == 200

    data = login_response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_login_user_wrong_password():
    """
    Test that a registered user cannot log in with an incorrect password.
    """

    # register a user first
    register_response = client.post(
        "/auth/register",
        json={
            "email": "jim@example.com",
            "username": "jim",
            "password": "password123",
        },
    )

    # verify user registration
    assert register_response.status_code == 201

    # now attempt to log in with the registered user's credentials
    login_response = client.post(
        "/auth/login",
        data={
            "username": "jim@example.com",
            "password": "wrongpassword",
        },
    )

    # verify that the login failed
    assert login_response.status_code == 401
    assert login_response.json() == {"detail": "Invalid email or password"}


def test_read_current_user_with_valid_token():
    """
    Test that a registered user can retrieve their own information using a valid token.
    """

    # register a user first
    register_response = client.post(
        "/auth/register",
        json={
            "email": "jim@example.com",
            "username": "jim",
            "password": "password123",
        },
    )

    #verify user registration
    assert register_response.status_code == 201

    # log in to receive an access token
    login_response = client.post(
        "/auth/login",
        data={
            "username": "jim@example.com",
            "password": "password123",
        },
    )

    # verify that the login was successful and a token was returned
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200

    data = me_response.json()

    assert data["email"] == "jim@example.com"
    assert data["username"] == "jim"
    assert data["is_active"] is True
    assert "password" not in data
    assert "hashed_password" not in data


def test_read_current_user_without_token():
    """
    Test that a registered user cannot retrieve their own information without a token.
    """

    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}