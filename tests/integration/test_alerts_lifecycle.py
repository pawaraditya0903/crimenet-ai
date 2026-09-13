import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def get_tokens():
    admin_res = client.post("/api/auth/token", json={"username": "admin", "password": "Aditya@4912"})
    analyst_res = client.post("/api/auth/token", json={"username": "analyst1", "password": "Aditya@4912"})
    return admin_res.json()["access_token"], analyst_res.json()["access_token"]

def test_alert_review_escalation_and_supervisor_signoff():
    admin_token, analyst_token = get_tokens()
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Analyst inspects explainability
    explain_res = client.get("/api/alerts/a1/explain", headers=analyst_headers)
    assert explain_res.status_code == 200
    assert "feature_breakdown" in explain_res.json()

    # 2. Analyst reviews and confirms alert
    review_res = client.patch("/api/alerts/a1/review", json={
        "decision": "CONFIRMED_BY_INVESTIGATOR",
        "note": "Corroborated midnight wire transfer with customs manifest."
    }, headers=analyst_headers)
    assert review_res.status_code == 200
    assert review_res.json()["current_status"] == "CONFIRMED_BY_INVESTIGATOR"

    # 3. Analyst escalates to supervisor
    esc_res = client.post("/api/alerts/a1/escalate", json={
        "reason": "Exceeds ₹5 Crore threshold requiring warrant petition authorization."
    }, headers=analyst_headers)
    assert esc_res.status_code == 200
    assert esc_res.json()["supervisor_status"] == "AWAITING_SUPERVISOR"

    # 4. Analyst attempts to approve own escalation (Must be FORBIDDEN / 403)
    unauth_approve = client.post("/api/alerts/a1/supervisor-approve", json={
        "decision": "SUPERVISOR_APPROVED",
        "comments": "Self authorization attempt"
    }, headers=analyst_headers)
    assert unauth_approve.status_code == 403

    # 5. Supervisory Officer approves escalation
    auth_approve = client.post("/api/alerts/a1/supervisor-approve", json={
        "decision": "SUPERVISOR_APPROVED",
        "comments": "Reviewed cross-border wire logs; approved for formal dossier compilation."
    }, headers=admin_headers)
    assert auth_approve.status_code == 200
    assert auth_approve.json()["supervisor_status"] == "SUPERVISOR_APPROVED"
