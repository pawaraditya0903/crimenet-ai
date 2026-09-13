from typing import List, Optional
from fastapi import Header, HTTPException, Depends, Path
from backend.app.security.jwt import verify_jwt_token
from backend.app.models.database import get_db

class ForensicRole:
    SUPERVISORY_OFFICER = "SUPERVISORY_OFFICER"
    LEAD_INVESTIGATOR = "LEAD_INVESTIGATOR"
    FORENSIC_ANALYST = "FORENSIC_ANALYST"
    INTELLIGENCE_AUDITOR = "INTELLIGENCE_AUDITOR"

ROLE_HIERARCHY = {
    ForensicRole.SUPERVISORY_OFFICER: 4,
    ForensicRole.LEAD_INVESTIGATOR: 3,
    ForensicRole.FORENSIC_ANALYST: 2,
    ForensicRole.INTELLIGENCE_AUDITOR: 1,
}

ALL_ROLES = [
    ForensicRole.SUPERVISORY_OFFICER,
    ForensicRole.LEAD_INVESTIGATOR,
    ForensicRole.FORENSIC_ANALYST,
    ForensicRole.INTELLIGENCE_AUDITOR,
]

def require_authenticated_user(authorization: Optional[str] = Header(None)) -> dict:
    """FastAPI Dependency: Validates Bearer JWT signature, structure, and expiration.
    Returns decoded token claims or raises HTTP 401.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Missing or malformed Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = authorization.split(" ", 1)[1].strip()
    claims = verify_jwt_token(token, expected_use="access")
    if not claims:
        raise HTTPException(
            status_code=401,
            detail="Invalid, tampered, or expired access token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return claims

def require_roles(allowed_roles: List[str]):
    """FastAPI Dependency: Enforces strict Role-Based Access Control (RBAC).
    Rejects unauthorized role escalation and manipulated JWT tokens.
    """
    def _role_verifier(claims: dict = Depends(require_authenticated_user)) -> dict:
        user_role = claims.get("role", "")
        if not user_role or user_role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Role '{user_role}' lacks required permissions. Allowed roles: {allowed_roles}"
            )
        return claims
    return _role_verifier

def require_case_access(case_id: str = Path(...), claims: dict = Depends(require_authenticated_user)) -> dict:
    """FastAPI Dependency: Enforces resource-level authorization to prevent Insecure Direct Object References (IDOR).
    Supervisory officers have platform oversight; investigators & analysts must be explicitly assigned to the case.
    """
    user_id = claims.get("sub", "")
    role = claims.get("role", "")

    # Supervisory officers have cross-case oversight
    if role == ForensicRole.SUPERVISORY_OFFICER:
        return claims

    # Check database for case ownership or explicit squad assignment
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Verify case exists
        cursor.execute("SELECT id, lead_investigator_id FROM cases WHERE id = ?", (case_id,))
        case_row = cursor.fetchone()
        if not case_row:
            raise HTTPException(status_code=404, detail=f"Investigation case '{case_id}' does not exist.")

        # 2. Check if user is lead investigator
        if case_row["lead_investigator_id"] == user_id:
            return claims

        # 3. Check if user is in assigned squad for this case
        cursor.execute("SELECT 1 FROM case_assignments WHERE case_id = ? AND user_id = ?", (case_id, user_id))
        assignment = cursor.fetchone()
        if assignment:
            return claims

    # Access Denied: User attempted to access a case not assigned to them (IDOR defense)
    raise HTTPException(
        status_code=403,
        detail=f"Access Denied: Investigator '{user_id}' is not assigned to case '{case_id}'."
    )
