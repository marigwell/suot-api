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


def get_auth_headers() -> dict[str, str]:
    return get_auth_headers_for_user("jim@example.com", "jim")


def get_auth_headers_for_user(email: str, username: str) -> dict[str, str]:
    client.post(
        "/auth/register",
        json={
            "email": email,
            "username": username,
            "password": "password123",
        },
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


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
    Tests creating a new item for an authenticated user.
    """
    response = client.post(
        "/items",
        json={
            "name": "Saturn LA Shirt",
            "brand": "Saturn LA",
            "category": "Shirt",
            "color": "White",
            "size": "M",
            "price": "120.00",
            "purchase_date": "2026-08-14",
            "condition": "new",
            "notes": "Bought for testing richer item fields.",
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Saturn LA Shirt"
    assert data["brand"] == "Saturn LA"
    assert data["category"] == "Shirt"
    assert data["color"] == "White"
    assert data["size"] == "M"
    assert data["price"] == "120.00"
    assert data["purchase_date"] == "2026-08-14"
    assert data["condition"] == "new"
    assert data["notes"] == "Bought for testing richer item fields."
    assert "id" in data
    assert "user_id" in data


def test_get_items():
    """
    Tests retrieving all items for an authenticated user.
    """
    headers = get_auth_headers()

    client.post(
        "/items",
        json={
            "name": "Saturn Los Angeles Pleated Trousers",
            "category": "Pants",
            "color": "Gray",
            "size": "S",
            "price": "138.00",
            "purchase_date": "2026-08-14",
            "condition": "new",
            "notes": "Bought to climb at First Ascent.",
        },
        headers=headers,
    )

    response = client.get("/items", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Saturn Los Angeles Pleated Trousers"
    assert data[0]["category"] == "Pants"
    assert data[0]["color"] == "Gray"
    assert data[0]["size"] == "S"
    assert data[0]["price"] == "138.00"
    assert data[0]["purchase_date"] == "2026-08-14"
    assert data[0]["condition"] == "new"
    assert data[0]["notes"] == "Bought to climb at First Ascent."
    assert "id" in data[0]
    assert "user_id" in data[0]


def test_get_item_by_id():
    """
    Tests retrieving a single item by its ID
    """
    headers = get_auth_headers()

    create_response = client.post(
        "/items",
        json={
            "name": "UNIQLO Boxy Cropped Tee",
            "category": "T-Shirt",
            "color": "Green",
            "size": "XL",
            "price": "49.99",
            "purchase_date": "2026-05-28",
            "condition": "excellent",
            "notes": "Gifted from my cousin.",
        },
        headers=headers,
    )

    item_id = create_response.json()["id"]

    response = client.get(f"/items/{item_id}", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == item_id
    assert data["name"] == "UNIQLO Boxy Cropped Tee"
    assert data["category"] == "T-Shirt"
    assert data["color"] == "Green"
    assert data["size"] == "XL"
    assert data["price"] == "49.99"
    assert data["purchase_date"] == "2026-05-28"
    assert data["condition"] == "excellent"
    assert data["notes"] == "Gifted from my cousin."
    assert "user_id" in data


def test_get_item_not_found():
    """
    Tests retrieving a non-existent item
    """
    headers = get_auth_headers()

    response = client.get(
        "/items/999",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_update_item():
    """
    Tests updating an existing item
    """
    headers = get_auth_headers()

    create_response = client.post(
        "/items",
        json={
            "name": "UNIQLO Boxy Cropped Tee",
            "brand": "UNIQLO",
            "category": "T-Shirt",
            "color": "Green",
            "size": "XL",
            "price": "49.99",
            "purchase_date": "2026-05-28",
            "condition": "excellent",
            "notes": "Gifted from my cousin.",
        },
        headers=headers,
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
            "price": "49.99",
            "purchase_date": "2026-05-28",
            "condition": "good",
            "notes": "Signs of usage.",
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == item_id
    assert data["name"] == "UNIQLO Boxy Cropped Tee"
    assert data["brand"] == "UNIQLO"
    assert data["category"] == "T-Shirt"
    assert data["color"] == "Blue"
    assert data["size"] == "XS"
    assert data["price"] == "49.99"
    assert data["purchase_date"] == "2026-05-28"
    assert data["condition"] == "good"
    assert data["notes"] == "Signs of usage."


def test_update_item_not_found():
    """
    Tests updating a non-existent item
    """
    headers = get_auth_headers()

    response = client.put(
        "/items/999",
        json={
            "name": "Fake Item",
            "category": "T-Shirt",
            "color": "Indigo",
            "size": "XS",
        },
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_delete_item():
    """
    Tests deleting an existing item
    """
    headers = get_auth_headers()

    create_response = client.post(
        "/items",
        json={
            "name": "New Balance 9060",
            "category": "Shoes",
            "color": "White",
            "size": "8.5",
        },
        headers=headers,
    )

    item_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/items/{item_id}",
        headers=headers,
    )

    assert delete_response.status_code == 200
    assert delete_response.json() is True

    get_response = client.get(f"/items/{item_id}", headers=headers)
    assert get_response.status_code == 404


def test_delete_item_not_found():
    """
    Tests deleting a non-existent item
    """
    headers = get_auth_headers()

    response = client.delete(
        "/items/999",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_users_only_see_their_own_items():
    """
    Test that one user's items do not appear on another user's inventory.
    """
    user_one_headers = get_auth_headers_for_user("jim@example.com", "jim")
    user_two_headers = get_auth_headers_for_user("sam@example.com", "sam")

    client.post(
        "/items",
        json={
            "name": "Saturn LA Shirt",
            "brand": "Saturn LA",
            "category": "Shirt",
            "color": "Black",
            "size": "M",
        },
        headers=user_one_headers,
    )

    response = client.get("/items", headers=user_two_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_user_cannot_get_another_users_item():
    """
    Tests that one user cannot get another user's item despite knowing the item ID
    """
    user_one_headers = get_auth_headers_for_user("jim@example.com", "jim")
    user_two_headers = get_auth_headers_for_user("alex@example.com", "alex")

    create_response = client.post(
        "/items",
        json={
            "name": "Saturn LA Shirt",
            "brand": "Saturn LA",
            "category": "Shirt",
            "color": "White",
            "size": "M",
        },
        headers=user_one_headers,
    )

    item_id = create_response.json()["id"]

    response = client.get(f"/items/{item_id}", headers=user_two_headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_user_cannot_update_another_users_item():
    """
    Test that a user cannot update another user's item
    """
    user_one_headers = get_auth_headers_for_user("jim@example.com", "jim")
    user_two_headers = get_auth_headers_for_user("sam@example.com", "sam")

    create_response = client.post(
        "/items",
        json={
            "name": "Saturn LA Shirt",
            "brand": "Saturn LA",
            "category": "Shirt",
            "color": "Black",
            "size": "M",
        },
        headers=user_one_headers,
    )

    item_id = create_response.json()["id"]

    response = client.put(
        f"/items/{item_id}",
        json={
            "name": "Stolen Update",
            "brand": "Fake Brand",
            "category": "Jacket",
            "color": "Red",
            "size": "L",
        },
        headers=user_two_headers,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_user_cannot_delete_another_users_item():
    """
    Test that a user cannot delete another user's item.
    """
    user_one_headers = get_auth_headers_for_user("jim@example.com", "jim")
    user_two_headers = get_auth_headers_for_user("sam@example.com", "sam")

    create_response = client.post(
        "/items",
        json={
            "name": "Saturn LA Shirt",
            "brand": "Saturn LA",
            "category": "Shirt",
            "color": "Black",
            "size": "M",
        },
        headers=user_one_headers,
    )

    item_id = create_response.json()["id"]

    response = client.delete(f"/items/{item_id}", headers=user_two_headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_get_items_stats_with_no_items():
    """
    Tests closet analytics for a user with no items.
    """
    headers = get_auth_headers()

    response = client.get("/items/stats", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert data["total_items"] == 0
    assert data["total_closet_value"] == "0.00"
    assert data["category_counts"] == {}
    assert data["brand_counts"] == {}
    assert data["most_expensive_item"] is None


def test_get_item_stats_with_multiple_items():
    """
    Tests closet analytics with multiple priced items.
    """
    headers = get_auth_headers()

    client.post(
        "/items",
        json={
            "name": "Saturn LA Shirt",
            "brand": "Saturn LA",
            "category": "Shirt",
            "color": "White",
            "size": "M",
            "price": "120.00",
            "purchase_date": "2026-08-14",
            "condition": "new",
            "notes": "Statement shirt.",
        },
        headers=headers,
    )

    client.post(
        "/items",
        json={
            "name": "UNIQLO Boxy Tee",
            "brand": "UNIQLO",
            "category": "Shirt",
            "color": "Green",
            "size": "XL",
            "price": "49.99",
            "purchase_date": "2026-05-28",
            "condition": "excellent",
            "notes": "Daily tee.",
        },
        headers=headers,
    )

    client.post(
        "/items",
        json={
            "name": "New Balance 9060",
            "brand": "New Balance",
            "category": "Shoes",
            "color": "White",
            "size": "8.5",
            "price": "138.00",
            "purchase_date": "2026-06-01",
            "condition": "good",
            "notes": "Main shoes.",
        },
        headers=headers,
    )

    response = client.get("/items/stats", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert data["total_items"] == 3
    assert data["total_closet_value"] == "307.99"
    assert data["category_counts"] == {
        "Shirt": 2,
        "Shoes": 1,
    }
    assert data["brand_counts"] == {
        "Saturn LA": 1,
        "UNIQLO": 1,
        "New Balance": 1,
    }
    assert data["most_expensive_item"]["name"] == "New Balance 9060"
    assert data["most_expensive_item"]["brand"] == "New Balance"
    assert data["most_expensive_item"]["price"] == "138.00"


def test_item_stats_only_include_current_users_items():
    """
    Tests that closet analytics only include the current user's items.
    """
    user_one_headers = get_auth_headers_for_user("jim@example.com", "jim")
    user_two_headers = get_auth_headers_for_user("sam@example.com", "sam")

    client.post(
        "/items",
        json={
            "name": "Saturn LA Shirt",
            "brand": "Saturn LA",
            "category": "Shirt",
            "color": "White",
            "size": "M",
            "price": "120.00",
        },
        headers=user_one_headers,
    )

    client.post(
        "/items",
        json={
            "name": "Expensive Sam Jacket",
            "brand": "Sam Brand",
            "category": "Jacket",
            "color": "Black",
            "size": "L",
            "price": "999.00",
        },
        headers=user_two_headers,
    )

    response = client.get("/items/stats", headers=user_one_headers)

    assert response.status_code == 200

    data = response.json()

    assert data["total_items"] == 1
    assert data["total_closet_value"] == "120.00"
    assert data["category_counts"] == {"Shirt": 1}
    assert data["brand_counts"] == {"Saturn LA": 1}
    assert data["most_expensive_item"]["name"] == "Saturn LA Shirt"
    assert data["most_expensive_item"]["price"] == "120.00"


def test_filter_items_by_category():
    """
    Tests filtering the current user's items by category.
    """
    headers = get_auth_headers()

    client.post(
        "/items",
        json={
            "name": "Saturn LA Shirt",
            "brand": "Saturn LA ",
            "category": "Shirt",
            "color": "White",
            "size": "M",
            "price": "40.00",
            "condition": "new",
        },
        headers=headers,
    )

    client.post(
        "/items",
        json={
            "name": "New Balance 9060",
            "brand": "New Balance",
            "category": "Shoes",
            "color": "White",
            "size": "8.5",
            "price": "138.00",
            "condition": "good",
        },
        headers=headers,
    )

    response = client.get("/items?category=Shirt", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Saturn LA Shirt"
    assert data[0]["category"] == "Shirt"


def test_filter_items_by_brand():
    """
    Tests filtering the current user's items by brand.
    """
    headers = get_auth_headers()

    client.post(
        "/items",
        json={
            "name": "Saturn LA Shirt",
            "brand": "Saturn LA",
            "category": "Shirt",
            "color": "White",
            "size": "M",
            "price": "40.00",
            "condition": "new",
        },
        headers=headers,
    )

    client.post(
        "/items",
        json={
            "name": "UNIQLO Boxy Tee",
            "brand": "UNIQLO",
            "category": "Shirt",
            "color": "Green",
            "size": "XL",
            "price": "49.99",
            "condition": "excellent",
        },
        headers=headers,
    )

    response = client.get("/items?brand=UNIQLO", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "UNIQLO Boxy Tee"
    assert data[0]["brand"] == "UNIQLO"


def test_filter_items_by_condition():
    """
    Tests filtering the current user's items by condition
    """
    headers = get_auth_headers()

    client.post(
        "/items",
        json={
            "name": "Saturn LA Shirt",
            "brand": "Saturn LA",
            "category": "Shirt",
            "color": "White",
            "size": "M",
            "price": "40.00",
            "condition": "new",
        },
        headers=headers,
    )

    client.post(
        "/items",
        json={
            "name": "Some worn up hoodie",
            "brand": "Unknown",
            "category": "Hoodie",
            "color": "Black",
            "size": "L",
            "price": "30.00",
            "condition": "bad",
        },
        headers=headers,
    )

    response = client.get("/items?condition=bad", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Some worn up hoodie"
    assert data[0]["condition"] == "bad"


def test_filter_items_by_category_and_brand():
    """
    Tests filtering the current user's items by category and brand together.
    """
    headers = get_auth_headers()

    client.post(
        "/items",
        json={
            "name": "Saturn LA Shirt",
            "brand": "Saturn LA",
            "category": "Shirt",
            "color": "White",
            "size": "M",
            "price": "120.00",
            "condition": "new",
        },
        headers=headers,
    )

    client.post(
        "/items",
        json={
            "name": "UNIQLO Boxy Tee",
            "brand": "UNIQLO",
            "category": "Shirt",
            "color": "Green",
            "size": "XL",
            "price": "49.99",
            "condition": "excellent",
        },
        headers=headers,
    )

    client.post(
        "/items",
        json={
            "name": "UNIQLO Wide Pants",
            "brand": "UNIQLO",
            "category": "Pants",
            "color": "Black",
            "size": "M",
            "price": "59.99",
            "condition": "new",
        },
        headers=headers,
    )

    response = client.get(
        "/items?category=Shirt&brand=UNIQLO",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "UNIQLO Boxy Tee"
    assert data[0]["category"] == "Shirt"
    assert data[0]["brand"] == "UNIQLO"
