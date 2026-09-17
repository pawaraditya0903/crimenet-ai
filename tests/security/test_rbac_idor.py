import os
# SEC-003 FIX: Hardcoded password removed. Test credentials must come from DEFAULT_SEED_PASSWORD env var.
# Set DEFAULT_SEED_PASSWORD in your test .env file before running integration tests.
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def get_token(username: str) -> str:
    res = client.post("/api/auth/token", json={"username": username, "password": os.environ.get("DEFAULT_SEED_PASSWORD", "CrimeNetDev@2026")})
    return res.json()["access_token"]

def test_horizontal_idor_prevention_on_unassigned_case():
    # Analyst 1 is assigned to c1, but NOT to c2
    analyst_token = get_token("analyst1")
    headers = {"Authorization": f"Bearer {analyst_token}"}

    # 1. Access to assigned case c1 succeeds
    assigned_res = client.get("/api/cases/c1", headers=headers)
    assert assigned_res.status_code == 200

    # 2. Access to unassigned case c2 must be rejected with 403 Forbidden (IDOR Defense)
    unassigned_res = client.get("/api/cases/c2", headers=headers)
    assert unassigned_res.status_code == 403
    assert "not assigned" in unassigned_res.json()["detail"].lower()

def test_vertical_privilege_escalation_rejection():
    # Analyst attempts an operation reserved for Supervisory Officer
    analyst_token = get_token("analyst1")
    headers = {"Authorization": f"Bearer {analyst_token}"}

    res = client.post("/api/alerts/a1/supervisor-approve", json={
        "decision": "SUPERVISOR_APPROVED",
        "comments": "Unauthorized escalation attempt"
    }, headers=headers)
    assert res.status_code == 403

def test_auditor_role_read_only_restriction():
    # Auditor attempts to create an investigation case (reserved for Lead / Supervisor)
    auditor_token = get_token("auditor1")
    headers = {"Authorization": f"Bearer {auditor_token}"}

    res = client.post("/api/cases", json={
        "title": "Auditor Unauthorized Case",
        "description": "Should fail with 403"
    }, headers=headers)
    assert res.status_code == 403
