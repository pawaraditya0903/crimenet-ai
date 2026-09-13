import pytest
from backend.app.forensics.evidence_vault import compute_evidence_hash, verify_evidence_hash

def test_evidence_bit_flip_tampering():
    original_payload = b"CRIMENET_IMMUTABLE_EVIDENCE_RECORD_PAYLOAD"
    recorded_hash = compute_evidence_hash(original_payload)

    # Simulated bit-flip attack
    tampered_payload = bytearray(original_payload)
    tampered_payload[0] = tampered_payload[0] ^ 0x01  # Flip 1 bit

    res = verify_evidence_hash(recorded_hash, bytes(tampered_payload))
    assert res["is_intact"] is False
    assert res["integrity_status"] == "TAMPERED_HASH_MISMATCH"
    assert res["computed_hash"] != recorded_hash
