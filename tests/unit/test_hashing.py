import hashlib
import pytest
from backend.app.security.crypto import compute_sha256, constant_time_compare
from backend.app.forensics.evidence_vault import compute_evidence_hash, verify_evidence_hash

def test_sha256_deterministic_computation():
    data = b"FORENSIC_EVIDENCE_RECORD_2026"
    expected = hashlib.sha256(data).hexdigest()
    computed = compute_sha256(data)
    assert computed == expected
    assert len(computed) == 64

def test_constant_time_comparison():
    hash_a = "a4f81c9b2d8e41762a0c4f8812e569201a4e87bf23d10a97c45812e9b01c34a1"
    hash_b = "a4f81c9b2d8e41762a0c4f8812e569201a4e87bf23d10a97c45812e9b01c34a1"
    hash_diff = "7b192c8104ea583f120194827163019482019482716492018471928471920192"

    assert constant_time_compare(hash_a, hash_b) is True
    assert constant_time_compare(hash_a, hash_diff) is False

def test_evidence_hash_tamper_detection():
    clean_bytes = b"CDR_CALL_RECORDS_MUMBAI_2026_MARCH"
    recorded_hash = compute_evidence_hash(clean_bytes)

    # Intact data verification
    res_intact = verify_evidence_hash(recorded_hash, clean_bytes)
    assert res_intact["is_intact"] is True
    assert res_intact["integrity_status"] == "VERIFIED_INTACT"

    # Tampered 1-bit modified data
    tampered_bytes = b"CDR_CALL_RECORDS_MUMBAI_2026_NARCH"
    res_tampered = verify_evidence_hash(recorded_hash, tampered_bytes)
    assert res_tampered["is_intact"] is False
    assert res_tampered["integrity_status"] == "TAMPERED_HASH_MISMATCH"
