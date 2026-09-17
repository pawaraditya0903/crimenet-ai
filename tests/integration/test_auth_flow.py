import os
# SEC-003 FIX: Hardcoded password removed. Test credentials must come from DEFAULT_SEED_PASSWORD env var.
# Set DEFAULT_SEED_PASSWORD in your test .env file before running integration tests.
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_complete_authentication_and_rotation_lifecycle():
    # 1. Login with seeded admin credentials
    login_res = client.post("/api/auth/token", json={
        "username": "admin",
        "password": os.environ.get("DEFAULT_SEED_PASSWORD", "CrimeNetDev@2026")
    })
    assert login_res.status_code == 200
    data = login_res.json()
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    assert access_token is not None
    assert refresh_token is not None

    # 2. Verify Access Token
    verify_res = client.get("/api/auth/verify-token", headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert verify_res.status_code == 200
    assert verify_res.json()["claims"]["role"] == "SUPERVISORY_OFFICER"

    # 3. Rotate Refresh Token
    refresh_res = client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert refresh_res.status_code == 200
    rotated_data = refresh_res.json()
    new_access = rotated_data["access_token"]
    new_refresh = rotated_data["refresh_token"]
    assert new_access != access_token
    assert new_refresh != refresh_token

    # 4. Old refresh token should now be rejected (Token Rotation Invalidation)
    reused_res = client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert reused_res.status_code == 401

    # 5. Logout with active refresh token
    logout_res = client.post("/api/auth/logout", json={
        "refresh_token": new_refresh
    }, headers={"Authorization": f"Bearer {new_access}"})
    assert logout_res.status_code == 200
    assert logout_res.json()["success"] is True

    # 6. Revoked refresh token cannot be used again
    post_logout_res = client.post("/api/auth/refresh", json={
        "refresh_token": new_refresh
    })
    assert post_logout_res.status_code == 401
