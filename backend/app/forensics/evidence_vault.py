import hashlib
from typing import Dict, Any, Union
from backend.app.security.crypto import constant_time_compare, compute_sha256

EVIDENCE_DISCLAIMER = (
    "CRYPTOGRAPHIC INTEGRITY NOTICE: SHA-256 verification establishes bit-level file integrity "
    "post-ingestion against tampering or corruption. It does NOT independently establish authenticity "
    "of origin, lawful collection, or judicial certification."
)

def compute_evidence_hash(data: Union[bytes, str]) -> str:
    """Computes SHA-256 hash of evidence binary data."""
    return compute_sha256(data)

def verify_evidence_hash(expected_hash: str, actual_data: Union[bytes, str]) -> Dict[str, Any]:
    """Verifies evidence file against its recorded ingestion hash using constant-time comparison."""
    computed = compute_evidence_hash(actual_data)
    is_intact = constant_time_compare(expected_hash, computed)

    return {
        "expected_hash": expected_hash,
        "computed_hash": computed,
        "integrity_status": "VERIFIED_INTACT" if is_intact else "TAMPERED_HASH_MISMATCH",
        "is_intact": is_intact,
        "disclaimer": EVIDENCE_DISCLAIMER
    }
