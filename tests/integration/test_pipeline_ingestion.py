import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.pipeline.ingestion import (
    MultiSourcePipeline,
    haversine_distance_km,
    normalize_phone,
    SAMPLE_CDR_DATA,
    SAMPLE_BANKING_DATA,
    SAMPLE_FIR_DATA,
    SAMPLE_ANPR_DATA,
    SAMPLE_WALLET_DATA
)

client = TestClient(app)

def test_haversine_distance_calculation():
    """Verify haversine distance calculates accurate geographic separation in kilometers."""
    # Bandra-Worli Sea Link Tower (19.0330, 72.8185) to Bandra Toll Plaza (19.0345, 72.8190)
    dist = haversine_distance_km(19.0330, 72.8185, 19.0345, 72.8190)
    assert 0.1 <= dist <= 0.3, f"Expected distance between tower and toll ~0.17 km, got {dist}"

def test_normalize_phone():
    """Verify phone normalization handles various standard Indian and UAE phone numbers."""
    assert normalize_phone("9876543210") == "+91-9876543210"
    assert normalize_phone("+91 9876543210") == "+91-9876543210"
    assert normalize_phone("+91-98765-43210") == "+91-9876543210"
    assert normalize_phone("+971-501234567") == "+971-501234567"

def test_multisource_pipeline_core_execution():
    """Verify that MultiSourcePipeline processes all 5 domains and discovers cross-domain links."""
    res = MultiSourcePipeline.process_and_link(
        cdr_records=SAMPLE_CDR_DATA,
        banking_records=SAMPLE_BANKING_DATA,
        fir_records=SAMPLE_FIR_DATA,
        anpr_records=SAMPLE_ANPR_DATA,
        wallet_records=SAMPLE_WALLET_DATA,
        persist_to_db=True
    )
    assert res["status"] == "PIPELINE_EXECUTED_SUCCESS"
    counts = res["counts"]
    assert counts["total_records_ingested"] >= 15
    assert counts["entities_resolved"] > 10
    assert counts["total_links_generated"] > 15
    assert counts["cross_domain_links_discovered"] >= 3

    labels = [link["label"] for link in res["links"]]
    assert "CALLED" in labels
    assert "FUNDS_TRANSFERRED" in labels
    assert "NAMED_IN_FIR" in labels
    assert "CAPTURED_AT_TOLL" in labels
    assert "WALLET_TRANSFER" in labels
    # Cross-domain links
    assert any("CROSS_DOMAIN_IDENTITY" == l or "SPATIOTEMPORAL_CO_LOCATION" == l or "SUSPECT_VEHICLE_CITED" == l for l in labels)

def test_pipeline_sample_data_endpoint():
    """Verify API endpoint returning sample datasets."""
    response = client.get("/api/pipeline/sample-data/all")
    assert response.status_code == 200
    data = response.json()
    assert "samples" in data
    assert len(data["samples"]["cdr"]) > 0
    assert len(data["samples"]["banking"]) > 0
    assert len(data["samples"]["fir"]) > 0
    assert len(data["samples"]["anpr"]) > 0
    assert len(data["samples"]["wallet"]) > 0

def test_pipeline_load_all_samples_api():
    """Verify POST /api/pipeline/load-all-samples endpoint."""
    response = client.post("/api/pipeline/load-all-samples")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PIPELINE_EXECUTED_SUCCESS"
    assert data["counts"]["total_records_ingested"] > 0
    assert len(data["links"]) > 0

def test_pipeline_summary_endpoint():
    """Verify GET /api/pipeline/summary endpoint."""
    response = client.get("/api/pipeline/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["total_entities"] > 0
    assert data["total_relationships"] > 0

def test_pipeline_csv_ingestion():
    """Verify CSV string parsing and ingestion."""
    csv_text = """caller,receiver,duration_sec,timestamp,tower_name,lat,lng
+91-9876543210,+91-9123456789,180,2026-03-12 10:00:00,Colaba Tower,18.9067,72.8147
"""
    response = client.post("/api/pipeline/ingest", json={
        "csv_content": csv_text,
        "csv_dataset_type": "cdr"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PIPELINE_EXECUTED_SUCCESS"
    assert data["counts"]["cdr_records"] >= 1
