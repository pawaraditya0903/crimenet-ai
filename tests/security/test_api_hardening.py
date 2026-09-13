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
