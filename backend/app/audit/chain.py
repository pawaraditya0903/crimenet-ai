import json
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from backend.app.models.database import get_db
from backend.app.security.crypto import compute_sha256

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

def _canonical_hash_input(previous_hash: str, event_id: str, timestamp: str, actor_id: str, action: str, resource: str, payload_json: str) -> str:
    """Creates a deterministic canonical string for hash calculation."""
    return f"{previous_hash}:{event_id}:{timestamp}:{actor_id}:{action}:{resource}:{payload_json}"

def append_audit_event(
    actor_id: str,
    role: str,
    action: str,
    resource: str,
    payload: Dict[str, Any],
    ip_address: str = "127.0.0.1",
    correlation_id: str = ""
) -> Dict[str, Any]:
    """Appends a cryptographically linked event to the audit chain in SQLite."""
    event_id = f"evt-{uuid.uuid4().hex[:12]}"
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    payload_json = json.dumps(payload, sort_keys=True)

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get latest current_hash to link the chain
        cursor.execute("SELECT current_hash FROM audit_chain ORDER BY rowid DESC LIMIT 1")
        latest = cursor.fetchone()
        previous_hash = latest["current_hash"] if latest else GENESIS_HASH

        # Compute new current_hash
        raw_str = _canonical_hash_input(previous_hash, event_id, now_utc, actor_id, action, resource, payload_json)
        current_hash = compute_sha256(raw_str)

        cursor.execute(
            """INSERT INTO audit_chain (
                event_id, timestamp, actor_id, role, action, resource,
                ip_address, correlation_id, event_payload_json, previous_hash, current_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (event_id, now_utc, actor_id, role, action, resource, ip_address, correlation_id, payload_json, previous_hash, current_hash)
        )

    return {
        "event_id": event_id,
        "timestamp": now_utc,
        "actor_id": actor_id,
        "role": role,
        "action": action,
        "resource": resource,
        "previous_hash": previous_hash,
        "current_hash": current_hash
    }

def verify_audit_chain() -> Dict[str, Any]:
    """Verifies the integrity of the hash-linked audit chain.
    If any event was altered, inserted, or deleted, reports CHAIN_INVALID with the exact broken index.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rowid, event_id, timestamp, actor_id, role, action, resource,
                   ip_address, correlation_id, event_payload_json, previous_hash, current_hash
            FROM audit_chain
            ORDER BY rowid ASC
        """)
        rows = cursor.fetchall()

    if not rows:
        return {"valid": True, "status": "CHAIN_EMPTY", "total_events_verified": 0}

    expected_prev = GENESIS_HASH

    for idx, row in enumerate(rows):
        # 1. Verify previous_hash link continuity
        if row["previous_hash"] != expected_prev:
            return {
                "valid": False,
                "status": "CHAIN_INVALID",
                "broken_at_index": idx,
                "event_id": row["event_id"],
                "reason": f"Broken chain link: recorded previous_hash '{row['previous_hash']}' does not match prior block hash '{expected_prev}'."
            }

        # 2. Recompute current_hash from event payload
        canonical = _canonical_hash_input(
            row["previous_hash"],
            row["event_id"],
            row["timestamp"],
            row["actor_id"],
            row["action"],
            row["resource"],
            row["event_payload_json"]
        )
        recalculated_hash = compute_sha256(canonical)

        if recalculated_hash != row["current_hash"]:
            return {
                "valid": False,
                "status": "CHAIN_INVALID",
                "broken_at_index": idx,
                "event_id": row["event_id"],
                "reason": f"Payload tampering detected: recalculated hash '{recalculated_hash}' does not match stored current_hash '{row['current_hash']}'."
            }

        expected_prev = row["current_hash"]

    return {
        "valid": True,
        "status": "CHAIN_VALID",
        "total_events_verified": len(rows),
        "head_hash": expected_prev,
        "verified_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }
