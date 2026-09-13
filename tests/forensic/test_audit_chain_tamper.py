import pytest
from backend.app.audit.chain import append_audit_event, verify_audit_chain
from backend.app.models.database import get_db

def test_hash_linked_audit_chain_tamper_detection():
    # 1. Ensure starting state is valid
    init_res = verify_audit_chain()
    assert init_res["valid"] is True, f"Starting audit chain was corrupted: {init_res}"

    # 2. Append authentic audit events
    evt1 = append_audit_event("usr-01", "SUPERVISORY_OFFICER", "CASE_CREATED", "case:c10", {"title": "Test Case"})
    evt2 = append_audit_event("usr-02", "LEAD_INVESTIGATOR", "EVIDENCE_ATTACHED", "case:c10", {"filename": "wire.csv"})
    evt3 = append_audit_event("usr-03", "FORENSIC_ANALYST", "ALERT_CONFIRMED", "alert:a10", {"status": "CONFIRMED"})

    try:
        # 3. Chain must verify as VALID
        res_valid = verify_audit_chain()
        assert res_valid["valid"] is True
        assert res_valid["status"] == "CHAIN_VALID"

        # 4. Simulate insider database tampering by directly updating the action in SQLite
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE audit_chain SET action = 'MALICIOUS_TAMPER_ACTION' WHERE event_id = ?", (evt2["event_id"],))

        # 5. Chain verification MUST fail and identify CHAIN_INVALID due to hash mismatch
        res_tampered = verify_audit_chain()
        assert res_tampered["valid"] is False
        assert res_tampered["status"] == "CHAIN_INVALID"
        assert "tampering detected" in res_tampered["reason"].lower() or "broken chain" in res_tampered["reason"].lower()

        # 6. Restore authentic action and verify chain integrity is recovered
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE audit_chain SET action = ? WHERE event_id = ?", (evt2["action"], evt2["event_id"]))

        res_restored = verify_audit_chain()
        assert res_restored["valid"] is True
        assert res_restored["status"] == "CHAIN_VALID"

    finally:
        # 7. Clean up test events in reverse order to preserve cryptographic chain integrity
        with get_db() as conn:
            cursor = conn.cursor()
            for eid in [evt3["event_id"], evt2["event_id"], evt1["event_id"]]:
                cursor.execute("DELETE FROM audit_chain WHERE event_id = ?", (eid,))
