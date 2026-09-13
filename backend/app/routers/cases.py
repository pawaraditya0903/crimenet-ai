import uuid
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Any
from backend.app.schemas.cases import CaseCreateRequest, CaseStageUpdateRequest, CaseResponse
from backend.app.security.rbac import require_authenticated_user, require_roles, require_case_access, ForensicRole
from backend.app.models.database import get_db
from backend.app.audit.chain import append_audit_event

router = APIRouter(prefix="/api/cases", tags=["Investigation Cases"])

@router.get("")
async def list_cases(claims: dict = Depends(require_authenticated_user)):
    """Lists investigation cases accessible to the authenticated user.
    Supervisors can view all cases; analysts and lead investigators see assigned cases.
    """
    user_id = claims.get("sub")
    role = claims.get("role")

    with get_db() as conn:
        cursor = conn.cursor()
        if role == ForensicRole.SUPERVISORY_OFFICER:
            cursor.execute("SELECT id, title, description, stage, priority, lead_investigator_id, squad, created_at, updated_at FROM cases ORDER BY updated_at DESC")
        else:
            cursor.execute("""
                SELECT DISTINCT c.id, c.title, c.description, c.stage, c.priority, c.lead_investigator_id, c.squad, c.created_at, c.updated_at
                FROM cases c
                LEFT JOIN case_assignments ca ON c.id = ca.case_id
                WHERE c.lead_investigator_id = ? OR ca.user_id = ?
                ORDER BY c.updated_at DESC
            """, (user_id, user_id))
        
        rows = [dict(r) for r in cursor.fetchall()]

    return {"cases": rows, "total": len(rows)}

@router.get("/{case_id}")
async def get_case_by_id(case_id: str, claims: dict = Depends(require_case_access)):
    """Retrieves specific case details. Protected against IDOR via require_case_access."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, stage, priority, lead_investigator_id, squad, created_at, updated_at FROM cases WHERE id = ?", (case_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")
        
        cursor.execute("SELECT name FROM suspects WHERE case_id = ?", (case_id,))
        suspects = [r["name"] for r in cursor.fetchall()]

    case_dict = dict(row)
    case_dict["suspects"] = suspects
    return case_dict

@router.post("")
async def create_case(
    req: CaseCreateRequest,
    request: Request,
    claims: dict = Depends(require_roles([ForensicRole.SUPERVISORY_OFFICER, ForensicRole.LEAD_INVESTIGATOR]))
):
    """Creates a new investigation case and assigns the creator."""
    user_id = claims.get("sub")
    role = claims.get("role")
    client_ip = request.client.host if request.client else "127.0.0.1"
    correlation_id = getattr(request.state, "correlation_id", "")

    with get_db() as conn:
        cursor = conn.cursor()
        new_case_id = f"case-{uuid.uuid4().hex[:8]}"

        cursor.execute(
            """INSERT INTO cases (id, title, description, stage, priority, lead_investigator_id, squad, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))""",
            (new_case_id, req.title, req.description, req.stage or "evidence", req.priority or "high", user_id, req.squad or "Forensic Cell")
        )

        cursor.execute(
            "INSERT INTO case_assignments (case_id, user_id, assigned_at) VALUES (?, ?, datetime('now'))",
            (new_case_id, user_id)
        )

        if req.suspects:
            for idx, s_name in enumerate(req.suspects, 1):
                cursor.execute(
                    "INSERT INTO suspects (id, case_id, name, created_at) VALUES (?, ?, ?, datetime('now'))",
                    (f"s-{new_case_id}-{idx}", new_case_id, s_name)
                )

    append_audit_event(
        actor_id=user_id,
        role=role,
        action="CASE_CREATED",
        resource=f"case:{new_case_id}",
        payload={"title": req.title, "priority": req.priority},
        ip_address=client_ip,
        correlation_id=correlation_id
    )

    return {"status": "created", "case_id": new_case_id, "title": req.title}

@router.patch("/{case_id}/stage")
async def update_case_stage(
    case_id: str,
    req: CaseStageUpdateRequest,
    request: Request,
    claims: dict = Depends(require_case_access)
):
    """Updates investigation case stage (evidence -> surveillance -> warrant -> trial -> closed)."""
    user_id = claims.get("sub")
    role = claims.get("role")
    client_ip = request.client.host if request.client else "127.0.0.1"
    correlation_id = getattr(request.state, "correlation_id", "")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT stage FROM cases WHERE id = ?", (case_id,))
        case_row = cursor.fetchone()
        if not case_row:
            raise HTTPException(status_code=404, detail="Case not found.")

        old_stage = case_row["stage"]
        cursor.execute("UPDATE cases SET stage = ?, updated_at = datetime('now') WHERE id = ?", (req.stage, case_id))

    append_audit_event(
        actor_id=user_id,
        role=role,
        action="CASE_STAGE_UPDATED",
        resource=f"case:{case_id}",
        payload={"previous_stage": old_stage, "new_stage": req.stage},
        ip_address=client_ip,
        correlation_id=correlation_id
    )

    return {"status": "updated", "case_id": case_id, "stage": req.stage, "previous_stage": old_stage}

@router.delete("/{case_id}")
async def delete_case(
    case_id: str,
    request: Request,
    claims: dict = Depends(require_roles([ForensicRole.SUPERVISORY_OFFICER, ForensicRole.LEAD_INVESTIGATOR]))
):
    """Deletes an investigation case and associated assignments and suspects."""
    user_id = claims.get("sub")
    role = claims.get("role")
    client_ip = request.client.host if request.client else "127.0.0.1"
    correlation_id = getattr(request.state, "correlation_id", "")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM cases WHERE id = ?", (case_id,))
        case_row = cursor.fetchone()
        if not case_row:
            raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")
        title = case_row["title"]

        cursor.execute("DELETE FROM case_assignments WHERE case_id = ?", (case_id,))
        cursor.execute("DELETE FROM suspects WHERE case_id = ?", (case_id,))
        cursor.execute("DELETE FROM cases WHERE id = ?", (case_id,))

    append_audit_event(
        actor_id=user_id,
        role=role,
        action="CASE_DELETED",
        resource=f"case:{case_id}",
        payload={"title": title},
        ip_address=client_ip,
        correlation_id=correlation_id
    )

    return {"status": "deleted", "case_id": case_id}

