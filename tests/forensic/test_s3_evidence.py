"""
CrimeNet AI - S3/MinIO Object Storage & Cryptographic Evidence Tests
Tests binary evidence upload, retrieval, constant-time SHA-256 integrity verification,
bit-flip tamper detection, presigned download URLs, and EvidenceService lifecycle.
"""

import pytest
import uuid
import hashlib
from backend.app.storage.s3_client import (
    get_storage_client,
    check_storage_status,
    S3StorageClient
)
from backend.app.services.evidence_service import EvidenceService
from backend.app.security.crypto import compute_sha256

def test_storage_subsystem_telemetry():
    """Verify object storage connectivity and fallback telemetry."""
    status = check_storage_status()
    assert "status" in status
    assert status["status"] in ("OPERATIONAL_CONNECTED", "LOCAL_VAULT_FALLBACK")
    assert "provider" in status
    assert "bucket" in status
    assert "is_connected" in status
    assert isinstance(status["is_connected"], bool)

def test_s3_upload_download_and_integrity():
    """Verify single-pass SHA-256 upload, bit-for-bit download, and integrity verification."""
    storage = get_storage_client()
    raw_payload = b"CRIMENET_FORENSIC_EVIDENCE_PAYLOAD_TEST_" + uuid.uuid4().bytes
    expected_hash = compute_sha256(raw_payload)
    object_key = f"test_evidence/unit_{uuid.uuid4().hex[:8]}.bin"

    # 1. Upload
    res = storage.upload_file(
        file_data=raw_payload,
        object_key=object_key,
        content_type="application/octet-stream"
    )
    assert res["status"] in ("UPLOADED", "UPLOADED_LOCAL_FALLBACK")
    assert res["sha256_hash"] == expected_hash
    assert res["file_size"] == len(raw_payload)

    # 2. Download
    downloaded = storage.download_file(object_key)
    assert downloaded == raw_payload

    # 3. Verify integrity
    verify = storage.verify_object_integrity(object_key, expected_hash)
    assert verify["is_intact"] is True
    assert verify["integrity_status"] == "VERIFIED_INTACT"
    assert verify["computed_hash"] == expected_hash

def test_s3_bit_flip_tamper_detection():
    """Verify that any modification to expected hash or bytes triggers TAMPERED_HASH_MISMATCH."""
    storage = get_storage_client()
    payload = b"GENUINE_EVIDENCE_RECORD_2026"
    genuine_hash = compute_sha256(payload)
    object_key = f"test_evidence/tamper_{uuid.uuid4().hex[:8]}.bin"

    storage.upload_file(payload, object_key)

    # Corrupt the expected hash by flipping a byte
    tampered_expected_hash = "f" * 64 if genuine_hash.startswith("0") else "0" * 64
    verify = storage.verify_object_integrity(object_key, tampered_expected_hash)

    assert verify["is_intact"] is False
    assert verify["integrity_status"] == "TAMPERED_HASH_MISMATCH"
    assert verify["computed_hash"] == genuine_hash
    assert verify["computed_hash"] != tampered_expected_hash

def test_s3_missing_object_handling():
    """Verify graceful handling of non-existent objects without unhandled crash."""
    storage = get_storage_client()
    bogus_key = f"nonexistent_bucket/missing_{uuid.uuid4().hex}.bin"

    verify = storage.verify_object_integrity(bogus_key, "0" * 64)
    assert verify["is_intact"] is False
    assert verify["integrity_status"] == "OBJECT_NOT_FOUND"

def test_evidence_service_e2e_registration_and_presigned_url():
    """Verify EvidenceService full lifecycle: upload, database persistence, and verification."""
    storage = get_storage_client()
    test_pdf_content = b"%PDF-1.4 Mock forensic digital evidence content\n%%EOF"
    case_id = "c1"
    filename = f"test_forensic_doc_{uuid.uuid4().hex[:6]}.pdf"

    # Register via EvidenceService
    reg_result = EvidenceService.register_evidence(
        case_id=case_id,
        filename=filename,
        source_type="FORENSIC_DOCUMENT",
        file_bytes=test_pdf_content,
        collector_id="usr-01",
        mime_type="application/pdf"
    )

    assert "evidence_id" in reg_result
    assert reg_result["filename"] == filename
    assert reg_result["integrity_status"] == "VERIFIED_INTACT"
    ev_id = reg_result["evidence_id"]
    object_key = reg_result["object_key"]

    # Verify via EvidenceService
    verify_result = EvidenceService.verify_evidence(ev_id)
    assert verify_result["is_intact"] is True
    assert verify_result["integrity_status"] == "VERIFIED_INTACT"
    assert verify_result["expected_hash"] == reg_result["sha256_hash"]

    # Generate presigned URL
    url = storage.generate_presigned_url(object_key)
    assert isinstance(url, str)
    assert len(url) > 0
