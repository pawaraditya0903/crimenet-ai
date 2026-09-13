import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def get_auth_headers():
    res = client.post("/api/auth/token", json={"username": "admin", "password": "Aditya@4912"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_alerts_explainability_alias():
    headers = get_auth_headers()
    # Test the alias used by AlertCentre.tsx
    res = client.get("/api/alerts/a1/explainability", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "feature_breakdown" in data
    assert "plain_english_explanation" in data
    assert data["alert_id"] == "a1"

def test_analytics_disrupt_simulation():
    # Empty targets test
    empty_res = client.post("/api/analytics/disrupt-simulation", json={"target_nodes": []})
    assert empty_res.status_code == 200
    assert empty_res.json()["syndicate_operational_fracture_pct"] == 0.0

    # Targeted kingpin disruption
    disrupt_res = client.post("/api/analytics/disrupt-simulation", json={
        "target_nodes": ["Arjun Mehta", "Mohammed Rafiq"]
    })
    assert disrupt_res.status_code == 200
    data = disrupt_res.json()
    assert data["syndicate_operational_fracture_pct"] > 50.0
    assert "tactical_assessment" in data
    assert data["remaining_nodes"] < data["original_nodes"]
    assert data["remaining_edges"] < data["original_edges"]

def test_osint_lifecycle():
    # 1. Fetch feeds
    feeds_res = client.get("/api/osint/feeds")
    assert feeds_res.status_code == 200
    assert len(feeds_res.json()["feeds"]) >= 5

    # 2. Search feeds
    scan_res = client.post("/api/osint/scan", json={"query": "TRC20", "deep_tor_scan": True})
    assert scan_res.status_code == 200
    assert scan_res.json()["total_results"] >= 1

    # 3. Ingest entity into graph
    ingest_res = client.post("/api/osint/ingest-entity", json={
        "name": "Deira Escrow Terminal 9",
        "type": "Organization",
        "role": "Offshore Escrow",
        "city": "Dubai",
        "risk_score": 88.5,
        "dossier": "OSINT discovered automated escrow node.",
        "connect_to_suspect": "Mohammed Rafiq",
        "relation_label": "ESCROW_CLEARANCE"
    })
    assert ingest_res.status_code == 200
    assert ingest_res.json()["status"] in ["ENTITY_INGESTED_TO_GRAPH", "ALREADY_EXISTS"]

def test_geospatial_kalman_and_dispatch():
    # 1. Kalman prediction
    kalman_res = client.post("/api/geospatial/kalman-predict", json={
        "target_name": "BMW X5 (MH-01-AB-5678)",
        "lat": 19.0596,
        "lng": 72.8295
    })
    assert kalman_res.status_code == 200
    kdata = kalman_res.json()
    assert len(kdata["predicted_trajectory"]) == 5
    assert kdata["kalman_filter_state"]["status"] == "CONVERGED"

    # 2. Dispatch unit
    disp_res = client.post("/api/geospatial/dispatch", json={
        "target_name": "BMW X5 (MH-01-AB-5678)",
        "lat": 19.0596,
        "lng": 72.8295,
        "unit": "Tactical Recon Delta Unit"
    })
    assert disp_res.status_code == 200
    assert "dispatched" in disp_res.json()["message"].lower()

def test_models_evaluation_and_tuning():
    # 1. Evaluation data
    eval_res = client.get("/api/models/evaluation")
    assert eval_res.status_code == 200
    edata = eval_res.json()
    assert "supervised_anomaly_metrics" in edata
    assert "confusion_matrix" in edata

    # 2. Hyperparameter tuning (optimal)
    tune_res = client.post("/api/models/tune", json={
        "n_estimators": 250,
        "max_depth": 12,
        "contamination": 0.044,
        "decision_threshold": 0.845
    })
    assert tune_res.status_code == 200
    tdata = tune_res.json()
    assert tdata["tuning_status_code"] == "OPTIMAL_EQUILIBRIUM_NO_OVERFITTING"
    assert tdata["metrics"]["f1_score"] >= 0.95

    # 3. Hyperparameter tuning (overfitting trigger)
    overfit_res = client.post("/api/models/tune", json={
        "n_estimators": 25,
        "max_depth": 24,
        "contamination": 0.044,
        "decision_threshold": 0.845
    })
    assert overfit_res.status_code == 200
    assert overfit_res.json()["tuning_status_code"] == "OVERFITTING_RISK_DETECTED"

def test_responsible_ai_diagnostics():
    diag_res = client.post("/api/tests/run-diagnostics")
    assert diag_res.status_code == 200
    ddata = diag_res.json()
    assert ddata["total_tests"] == 10
    assert ddata["passed_count"] == 10
    assert ddata["failed_count"] == 0
    assert ddata["pass_percentage"] == 100

def test_system_settings_and_investigators():
    # 1. Settings read & update
    s_res = client.get("/api/settings")
    assert s_res.status_code == 200
    assert "agency" in s_res.json()

    update_res = client.post("/api/settings", json={"compact_mode": True, "toast_duration": 6})
    assert update_res.status_code == 200
    assert update_res.json()["settings"]["compact_mode"] is True

    # 2. Investigators roster
    inv_res = client.get("/api/investigators")
    assert inv_res.status_code == 200
    assert len(inv_res.json()["investigators"]) >= 3

    # 3. Add investigator
    new_inv = client.post("/api/investigators", json={
        "name": "Kavita Rao",
        "role": "Cyber Forensics Specialist",
        "clearance": "Secret / Level 4",
        "skills": ["Cyber Forensics & Dark Web Tracing"]
    })
    assert new_inv.status_code == 200
    created_id = new_inv.json()["investigator"]["id"]

    # 4. Delete investigator
    del_res = client.delete(f"/api/investigators/{created_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "INVESTIGATOR_DELETED"

def test_dynamic_pdf_generation_content():
    headers = get_auth_headers()
    
    # Generate report for Arjun Mehta
    arjun_pdf = client.post("/api/reports/generate", json={
        "entity_name": "Arjun Mehta",
        "report_type": "full",
        "details": {
            "financial_flag": "INR 42.8 Crore Unaccounted Hawala Outflow",
            "telecom_detail": "92 nocturnal calls to Dubai (+971-501234567)",
            "legal_action": "Freeze order under Section 17 PMLA",
            "aliases": "Bhaijaan, Kingpin, AM-01",
            "role": "Kingpin & Cross-Border Syndicate Leader",
            "community": "Cell Alpha (Nariman Point Syndicate)",
            "threat_level": "CRITICAL"
        }
    }, headers=headers)
    assert arjun_pdf.status_code == 200
    assert arjun_pdf.headers["content-type"] == "application/pdf"
    assert len(arjun_pdf.content) > 1000

    # Generate report for Priya Desai
    priya_pdf = client.post("/api/reports/generate", json={
        "entity_name": "Priya Desai",
        "report_type": "risk",
        "details": {
            "financial_flag": "INR 18.2 Crore Fictitious Accounting Layering",
            "telecom_detail": "Encrypted VoIP logs linking to Dubai Hawala hub",
            "legal_action": "Section 50 PMLA summons issued",
            "aliases": "Accountant Priya, PD-Surat",
            "role": "Lead Financial Architect & Shell Controller",
            "community": "Cell Gamma (Surat Hawala Node)",
            "threat_level": "HIGH"
        }
    }, headers=headers)
    assert priya_pdf.status_code == 200
    assert priya_pdf.headers["content-type"] == "application/pdf"
    assert len(priya_pdf.content) > 1000

def test_simulation_controls_and_notifications():
    # 1. Simulation start, speed, pause, status
    start_res = client.post("/api/simulation/start")
    assert start_res.status_code == 200
    assert start_res.json()["simulation"]["is_running"] is True

    speed_res = client.post("/api/simulation/speed", json={"speed": 2.5})
    assert speed_res.status_code == 200
    assert speed_res.json()["speed"] == 2.5

    pause_res = client.post("/api/simulation/pause")
    assert pause_res.status_code == 200
    assert pause_res.json()["simulation"]["is_running"] is False

    status_res = client.get("/api/simulation/status")
    assert status_res.status_code == 200

    # 2. Biometric token login
    bio_res = client.post("/api/auth/biometric-token", json={
        "badge": "Chief Officer Aditya Pawar",
        "similarity_score": 84.5
    })
    assert bio_res.status_code == 200
    assert "access_token" in bio_res.json()
    bio_token = bio_res.json()["access_token"]
    
    # Verify the issued biometric token works with protected endpoints
    verify_res = client.get("/api/auth/verify-token", headers={"Authorization": f"Bearer {bio_token}"})
    assert verify_res.status_code == 200
    assert verify_res.json()["valid"] is True

    # 3. Notifications clear-all
    clear_res = client.post("/api/notifications/clear-all", headers={"Authorization": f"Bearer {bio_token}"})
    assert clear_res.status_code == 200
    assert clear_res.json()["success"] is True

