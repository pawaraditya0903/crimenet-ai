from fastapi import APIRouter, Depends
from backend.app.security.rbac import require_authenticated_user
from backend.app.models.database import get_db
from backend.app.audit.chain import verify_audit_chain

router = APIRouter(tags=["Audit Trail"])

@router.get("/api/audit/logs")
@router.get("/api/security/audit-logs")
async def get_system_audit_trail(claims: dict = Depends(require_authenticated_user)):
    """Returns hash-linked cryptographic audit trail records."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_id, timestamp, actor_id, role, action, resource, ip_address, correlation_id, previous_hash, current_hash
            FROM audit_chain
            ORDER BY rowid DESC
        """)
        rows = [dict(r) for r in cursor.fetchall()]

    return {
        "total_records": len(rows),
        "audit_trail": rows,
        "tamper_resistance_note": "Cryptographically linked hash-chain. Any alteration invalidates downstream hashes."
    }

@router.get("/api/reports/audit-chain/verify")
async def verify_audit_chain_endpoint(claims: dict = Depends(require_authenticated_user)):
    """Verifies the end-to-end cryptographic continuity of the hash-linked audit chain."""
    return verify_audit_chain()
