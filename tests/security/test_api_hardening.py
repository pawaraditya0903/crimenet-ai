import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_api_security_headers():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert "X-Correlation-ID" in res.headers

def test_request_size_limit_rejection():
    # Attempting to send Content-Length > 10MB limit
    headers = {
        "Content-Length": str(15 * 1024 * 1024),
        "Content-Type": "application/json"
    }
    res = client.post("/api/cases", data="{}", headers=headers)
    assert res.status_code == 413
    assert "payload too large" in res.json()["error"].lower()

def test_verify_face_requires_auth_and_pydantic_validation():
    # 1. Unauthenticated request must be rejected
    unauth_res = client.post("/api/security/verify-face", json={"vector": [1.0] * 32})
    assert unauth_res.status_code == 401

    # Login to obtain valid token
    login_res = client.post("/api/auth/token", json={"username": "admin", "password": "Aditya@4912"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 2. Vector length < 16 must be rejected by Pydantic validation (422)
    short_vec_res = client.post("/api/security/verify-face", json={"vector": [0.5, 0.2]}, headers=auth_headers)
    assert short_vec_res.status_code == 422

    # 3. Register master face vector and verify persistence to SQLite
    vec = [0.1 * i for i in range(32)]
    enroll_res = client.post("/api/security/register-master-face", json={"vector": vec}, headers=auth_headers)
    assert enroll_res.status_code == 200
    assert enroll_res.json()["success"] is True

    # 4. Verify face matching
    verify_res = client.post("/api/security/verify-face", json={"vector": vec, "device": "TestLab"}, headers=auth_headers)
    assert verify_res.status_code == 200
    data = verify_res.json()
    assert data["authorized"] is True
    assert data["status"] == "AUTHORIZED_DEMO"
    assert "PROTOTYPE DISCLAIMER" in data["disclaimer"]

def test_forensic_intruder_logs_endpoints():
    # 1. Access logs unauthenticated post (gate probe)
    log_res = client.post("/api/security/log-access-attempt", json={
        "ip": "198.51.100.99",
        "device": "ProbeBrowser",
        "action": "PASSCODE_FAILED",
        "status": "BLOCKED (1/5 Fails)",
        "badge": "UNAUTHORIZED_PROBE"
    })
    assert log_res.status_code == 200
    assert log_res.json()["success"] is True

    # 2. Intruder logs requires authentication
    unauth_res = client.get("/api/security/intruder-logs")
    assert unauth_res.status_code == 401

    # 3. Authenticated retrieval works for /intruder-logs
    login_res = client.post("/api/auth/token", json={"username": "admin", "password": "Aditya@4912"})
    token = login_res.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    intruder_res = client.get("/api/security/intruder-logs", headers=auth_headers)
    assert intruder_res.status_code == 200
    assert "logs" in intruder_res.json()
    assert intruder_res.json()["total"] >= 1

    # Clean up test database pollution so live incident log is clean
    from backend.app.models.database import get_db
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM intruder_logs WHERE ip = '198.51.100.99' OR device IN ('ProbeBrowser', 'TestLab')")

