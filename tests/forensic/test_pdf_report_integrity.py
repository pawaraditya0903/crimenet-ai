import pytest
from backend.app.forensics.report_builder import build_pdf_report

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
