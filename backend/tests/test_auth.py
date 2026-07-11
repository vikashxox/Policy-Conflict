from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_login_returns_access_token():
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"]
    assert payload["token_type"] == "bearer"
    assert payload["user"]["username"] == "admin"


def test_dashboard_requires_authentication():
    response = client.get("/api/dashboard")
    assert response.status_code == 401

    token_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    token = token_response.json()["access_token"]

    auth_response = client.get(
        "/api/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert auth_response.status_code == 200
    body = auth_response.json()
    assert "kpis" in body
    assert body["kpis"]["healthScore"] >= 0
