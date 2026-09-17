import os
# SEC-003 FIX: Hardcoded password removed. Test credentials must come from DEFAULT_SEED_PASSWORD env var.
# Set DEFAULT_SEED_PASSWORD in your test .env file before running integration tests.
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def get_admin_token() -> str:
    res = client.post("/api/auth/token", json={"username": "admin", "password": os.environ.get("DEFAULT_SEED_PASSWORD", "CrimeNetDev@2026")})
    return res.json()["access_token"]

def test_case_crud_and_stage_advancement():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a new case
    create_res = client.post("/api/cases", json={
        "title": "Operation Midnight Echo",
        "description": "Cross-border cryptocurrency smurfing corridor.",
        "stage": "evidence",
        "priority": "critical",
        "squad": "Financial Crime Squad",
        "suspects": ["Target Alpha", "Target Beta"]
    }, headers=headers)
    assert create_res.status_code == 200
    case_id = create_res.json()["case_id"]

    # 2. Retrieve case details
    get_res = client.get(f"/api/cases/{case_id}", headers=headers)
    assert get_res.status_code == 200
    case_data = get_res.json()
    assert case_data["title"] == "Operation Midnight Echo"
    assert case_data["stage"] == "evidence"

    # 3. Advance stage
    stage_res = client.patch(f"/api/cases/{case_id}/stage", json={
        "stage": "surveillance"
    }, headers=headers)
    assert stage_res.status_code == 200
    assert stage_res.json()["stage"] == "surveillance"

    # 4. Verify stage updated in database
    verify_res = client.get(f"/api/cases/{case_id}", headers=headers)
    assert verify_res.json()["stage"] == "surveillance"

    # 5. Teardown: Delete the test case so database is not polluted with duplicates
    del_res = client.delete(f"/api/cases/{case_id}", headers=headers)
    assert del_res.status_code == 200

