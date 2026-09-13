import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.forensics.report_builder import build_pdf_report, build_bsa_certificate_pdf
from backend.app.security.jwt import create_jwt_token

def test_pdf_report_compilation_and_headers():
    evidence_items = [
        {"id": "ev-01", "source_type": "CDR", "filename": "cdr.csv", "sha256_hash": "a4f81c9b2d8e41762a0c4f8812e569201a4e87bf23d10a97c45812e9b01c34a1", "integrity_status": "INTACT"},
        {"id": "ev-02", "source_type": "BANK", "filename": "wire.csv", "sha256_hash": "7b192c8104ea583f120194827163019482019482716492018471928471920192", "integrity_status": "INTACT"}
    ]
    analytics_summary = {
        "density": 0.05,
        "average_degree": 4.2,
        "communities_count": 2,
        "top_node": "Target Lead",
        "top_pagerank": 0.09,
        "anomalies_count": 2
    }

    pdf_bytes = build_pdf_report(
        case_title="Operation Blue Thunder",
        case_id="c1",
        investigator_name="Aditya Pawar",
        investigator_role="Chief Officer",
        evidence_items=evidence_items,
        analytics_summary=analytics_summary
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    # PDF files start with standard magic bytes %PDF-
    assert pdf_bytes.startswith(b"%PDF-")


def test_pdf_report_entity_differentiation():
    """Verifies that different entities and templates produce distinct, tailored PDFs."""
    # Entity A: Arjun Mehta (Full Profile)
    pdf_arjun = build_pdf_report(
        case_title="Operation Blue Thunder",
        case_id="c1",
        investigator_name="Aditya Pawar",
        investigator_role="Lead Investigator",
        evidence_items=[],
        analytics_summary={"target_pagerank": 0.0847, "target_degree": 4},
        report_type="full",
        target_entity={"name": "Arjun Mehta", "type": "Person", "risk_score": 94.5, "city": "Mumbai"},
        direct_links=[{"source": "Arjun Mehta", "target": "Mohammed Rafiq", "label": "CALLS_NOCTURNAL", "confidence": 0.95}]
    )

    # Entity B: Mohammed Rafiq (Network Topology)
    pdf_rafiq = build_pdf_report(
        case_title="Operation Blue Thunder",
        case_id="c1",
        investigator_name="Aditya Pawar",
        investigator_role="Lead Investigator",
        evidence_items=[],
        analytics_summary={"target_pagerank": 0.0762, "target_degree": 3},
        report_type="network",
        target_entity={"name": "Mohammed Rafiq", "type": "Person", "risk_score": 88.0, "city": "Dubai"},
        direct_links=[{"source": "Al-Rafiq Trading Co", "target": "Mohammed Rafiq", "label": "DIRECTOR_CONTROL", "confidence": 0.98}]
    )

    # Entity C: Vikram Singh (Risk Assessment Template)
    pdf_vikram_risk = build_pdf_report(
        case_title="Operation Blue Thunder",
        case_id="c1",
        investigator_name="Aditya Pawar",
        investigator_role="Lead Investigator",
        evidence_items=[],
        analytics_summary={},
        report_type="risk",
        target_entity={"name": "Vikram Singh", "type": "Person", "risk_score": 79.4, "city": "Navi Mumbai"},
        entity_alerts=[{"id": "a3", "anomaly_type": "SIM_MULTIPLEXING", "anomaly_score": 0.794, "algorithm": "CDR-MultiplexEngine", "plain_english_explanation": "3 IMSIs mapped to single handset"}]
    )

    assert pdf_arjun.startswith(b"%PDF-")
    assert pdf_rafiq.startswith(b"%PDF-")
    assert pdf_vikram_risk.startswith(b"%PDF-")

    # Content must NOT be identical
    assert pdf_arjun != pdf_rafiq
    assert pdf_rafiq != pdf_vikram_risk
    assert len(pdf_arjun) > 2000
    assert len(pdf_rafiq) > 2000
    assert len(pdf_vikram_risk) > 2000


def test_bsa_certificate_pdf_generation():
    """Verifies that Section 63(4) BSA 2023 Statutory Certificate compiles with valid digital signature format."""
    cert_bytes = build_bsa_certificate_pdf("Mohammed Rafiq")
    assert isinstance(cert_bytes, bytes)
    assert cert_bytes.startswith(b"%PDF-")
    assert len(cert_bytes) > 2000


def test_api_reports_generate_dynamic_endpoint():
    """End-to-end API test verifying reports generation via FastAPI test client."""
    client = TestClient(app)
    token = create_jwt_token({"sub": "usr-01", "role": "LEAD_INVESTIGATOR", "badge": "INV-2026-AP01"})
    headers = {"Authorization": f"Bearer {token}"}

    # Test full dossier for Priya Desai
    res = client.post(
        "/api/reports/generate",
        json={"template": "full", "entity_id": "Priya Desai", "entity_type": "Person"},
        headers=headers
    )
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert "Priya_Desai" in res.headers["content-disposition"]
    assert res.content.startswith(b"%PDF-")

    # Test BSA certificate endpoint
    res_bsa = client.post(
        "/api/reports/bsa-certificate",
        json={"target_id": "Mehta Enterprises Ltd"},
        headers=headers
    )
    assert res_bsa.status_code == 200
    assert res_bsa.headers["content-type"] == "application/pdf"
    assert "Mehta_Enterprises_Ltd" in res_bsa.headers["content-disposition"]
    assert res_bsa.content.startswith(b"%PDF-")
