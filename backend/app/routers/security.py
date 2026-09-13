import time
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, List
from backend.app.schemas.auth import ChangePasswordRequest
from backend.app.security.passwords import hash_password, verify_password, validate_password_strength
from backend.app.security.face_prototype import evaluate_face_prototype
from backend.app.security.rbac import require_authenticated_user
from backend.app.models.database import get_db

router = APIRouter(prefix="/api/security", tags=["Security & System Settings"])

_MASTER_FACE_DESCRIPTOR: List[float] = []

@router.post("/verify-face")
async def verify_face_endpoint(data: dict):
    """Evaluates probe vector using prototype ZNCC facial similarity calculation."""
    probe_vec = data.get("vector", [])
    device = data.get("device", "Workstation")
    ip = data.get("ip", "127.0.0.1")

    # If no master vector enrolled yet, simulate with enrollment guidance
    res = evaluate_face_prototype(probe_vec, _MASTER_FACE_DESCRIPTOR, threshold=62.0)

    # Log attempt to SQLite
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO intruder_logs (id, timestamp, ip, device, action, status, badge, photo, epoch)
               VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(int(time.time() * 1000)),
                ip,
                device,
                "PROTOTYPE_FACE_VERIFICATION",
                res["status"],
                "Investigator Scan",
                data.get("photo", ""),
                time.time()
            )
        )

    return res

@router.post("/register-master-face")
async def register_master_face_endpoint(data: dict, claims: dict = Depends(require_authenticated_user)):
    """Enrolls master facial descriptor vector for prototype verification."""
    global _MASTER_FACE_DESCRIPTOR
    vector = data.get("vector", [])
    if not vector:
        raise HTTPException(status_code=400, detail="Vector cannot be empty.")
    _MASTER_FACE_DESCRIPTOR = vector
    return {"success": True, "message": "Master face vector successfully enrolled on server."}

@router.post("/change-password")
async def change_password_endpoint(req: ChangePasswordRequest, claims: dict = Depends(require_authenticated_user)):
    """Changes password with strong password policy enforcement and PBKDF2 hashing."""
    user_id = claims.get("sub")
    
    # 1. Validate Password Strength
    is_valid, msg = validate_password_strength(req.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user or not verify_password(req.current_password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Current password incorrect.")

        new_hash, new_salt = hash_password(req.new_password)
        cursor.execute("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?", (new_hash, new_salt, user_id))

    return {"success": True, "message": "Password changed successfully."}

@router.get("/intruder-logs")
async def get_intruder_logs(claims: dict = Depends(require_authenticated_user)):
    """Returns access and security events."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, ip, device, action, status, badge, photo, epoch FROM intruder_logs ORDER BY epoch DESC LIMIT 100")
        rows = [dict(r) for r in cursor.fetchall()]
    return {"logs": rows, "total": len(rows)}
