from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_upload_text_policy_returns_parsed_metadata():
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/api/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("policy.txt", b"Policy Name: Password Rotation Policy\nVersion: v4.2\nDepartment: Security Engineering\nOwner: Dana Whitmore\nEffective Date: 2024-06-01\nLast Reviewed: 2025-11-02\n\nThe policy shall require MFA for all users.\nUsers must rotate passwords every 30 days.\n", "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "uploaded"
    assert payload["parsed"]["policy_name"] == "Password Rotation Policy"
    assert payload["parsed"]["version"] == "v4.2"
    assert payload["parsed"]["department"] == "Security Engineering"
    assert payload["parsed"]["owner"] == "Dana Whitmore"
    assert payload["parsed"]["sections"] >= 1
    assert "must" in payload["parsed"]["raw_text"].lower()
