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
    """
    Tests creating a new item
    """
    response = client.post(
        "/items",
        json={
            "name": "Carbon Core - Lucy Racing Jacket",
            "brand": "Carbon Core",
            "category": "Jacket",
            "color": "Black",
            "size": "M",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Carbon Core - Lucy Racing Jacket"
    assert data["brand"] == "Carbon Core"
    assert data["category"] == "Jacket"
    assert data["color"] == "Black"
    assert data["size"] == "M"
    assert "id" in data


def test_get_items():
    """
    Tests retrieving all items
    """
    client.post(
        "/items",
        json={
            "name": "Saturn Los Angeles Pleated Trousers",
            "category": "Pants",
            "color": "Gray",
            "size": "S",
        },
    )

    response = client.get("/items")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Saturn Los Angeles Pleated Trousers"
    assert data[0]["category"] == "Pants"
    assert data[0]["color"] == "Gray"
    assert data[0]["size"] == "S"


def test_get_item_by_id():
    """
    Tests retrieving a single item by its ID
    """
    create_response = client.post(
        "/items",
        json={
            "name": "UNIQLO Boxy Cropped Tee",
            "category": "T-Shirt",
            "color": "Green",
            "size": "XL",
        },
    )

    item_id = create_response.json()["id"]

    response = client.get(f"/items/{item_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == item_id
    assert data["name"] == "UNIQLO Boxy Cropped Tee"
    assert data["category"] == "T-Shirt"
    assert data["color"] == "Green"
    assert data["size"] == "XL"


def test_get_item_not_found():
    """
    Tests retrieving a non-existent item
    """
    response = client.get("/items/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_update_item():
    """
    Tests updating an existing item
    """
    create_response = client.post(
        "/items",
        json={
            "name": "UNIQLO Boxy Cropped Tee",
            "brand": "UNIQLO",
            "category": "T-Shirt",
            "color": "Green",
            "size": "XL",
        },
    )

    item_id = create_response.json()["id"]

    response = client.put(
        f"/items/{item_id}",
        json={
            "name": "UNIQLO Boxy Cropped Tee",
            "brand": "UNIQLO",
            "category": "T-Shirt",
            "color": "Blue",
            "size": "XS",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == item_id
    assert data["name"] == "UNIQLO Boxy Cropped Tee"
    assert data["brand"] == "UNIQLO"
    assert data["category"] == "T-Shirt"
    assert data["color"] == "Blue"
    assert data["size"] == "XS"


def test_update_item_not_found():
    """
    Tests updating a non-existent item
    """
    response = client.put(
        "/items/999",
        json={
            "name": "Fake Item",
            "category": "T-Shirt",
            "color": "Indigo",
            "size": "XS",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_delete_item():
    """
    Tests deleting an existing item
    """
    create_response = client.post(
        "/items",
        json={
            "name": "New Balance 9060",
            "category": "Shoes",
            "color": "White",
            "size": "8.5",
        },
    )

    item_id = create_response.json()["id"]

    delete_response = client.delete(f"/items/{item_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() is True

    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 404


def test_delete_item_not_found():
    """
    Tests deleting a non-existent item
    """
    response = client.delete("/items/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}
