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

def test_create_item():
    response = client.post(
        "/items",
        json={
            "name": "Carbon Core - Lucy Racing Jacket",
            "category": "Jacket",
            "color": "Black",
            "size": "M",
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Carbon Core - Lucy Racing Jacket"
    assert data["category"] == "Jacket"
    assert data["color"] == "Black"
    assert data["size"] == "M"
    assert "id" in data