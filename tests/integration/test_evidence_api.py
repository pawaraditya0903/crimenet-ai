import os
# SEC-003 FIX: Hardcoded password removed. Test credentials must come from DEFAULT_SEED_PASSWORD env var.
# Set DEFAULT_SEED_PASSWORD in your test .env file before running integration tests.
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def get_analyst_token() -> str:
    res = client.post("/api/auth/token", json={"username": "analyst1", "password": os.environ.get("DEFAULT_SEED_PASSWORD", "CrimeNetDev@2026")})
    return res.json()["access_token"]

def test_evidence_retrieval_and_merkle_root():
    token = get_analyst_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List evidence items
    list_res = client.get("/api/evidence/items", headers=headers)
    assert list_res.status_code == 200
    items = list_res.json()["evidence_items"]
    assert len(items) > 0
    ev_id = items[0]["id"]

    # 2. Verify evidence integrity
    verify_res = client.get(f"/api/evidence/verify/{ev_id}", headers=headers)
    assert verify_res.status_code == 200
    assert verify_res.json()["verification_result"] == "MATCH"

    # 3. Retrieve Merkle Root
    merkle_res = client.get("/api/evidence/merkle-root", headers=headers)
    assert merkle_res.status_code == 200
    m_data = merkle_res.json()
    assert m_data["status"] == "MERKLE_TREE_VALIDATED"
    assert len(m_data["merkle_root_hash"]) == 64
    assert m_data["total_evidence_leaves"] >= len(items)
