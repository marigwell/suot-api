from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_create_item():
    response = client.post(
        "/items",
        json={
            "name": "Carbon Core - Lucy",
            "category": "Jacket",
            "color": "Black",
            "size": "M"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Carbon Core - Lucy"
    assert data["category"] == "Jacket"
    assert data["color"] == "Black"
    assert data["size"] == "M"
    assert "id" in data