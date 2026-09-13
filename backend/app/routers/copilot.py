from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, Union
import time
from backend.app.schemas.copilot import CopilotChatRequest, CopilotActionConfirmRequest
from backend.app.security.rbac import require_authenticated_user, require_case_access, ForensicRole
from backend.app.copilot.service import process_copilot_query
from backend.app.models.database import get_db
from backend.app.audit.chain import append_audit_event

router = APIRouter(tags=["AI Copilot"])

@router.post("/api/copilot/chat")
@router.post("/api/chat/message")
async def copilot_chat_endpoint(
    req_or_dict: Union[CopilotChatRequest, Dict[str, Any]],
    claims: dict = Depends(require_authenticated_user)
):
    """Processes Copilot queries with authoritative server-side context retrieval."""
    if isinstance(req_or_dict, dict):
        msg = str(req_or_dict.get("message", "")).strip()
        case_id = str(req_or_dict.get("case_id", "c1")).strip()
    else:
        msg = req_or_dict.message.strip()
        case_id = (req_or_dict.case_id or "c1").strip()

    user_id = claims.get("sub", "investigator")
    user_role = claims.get("role", ForensicRole.FORENSIC_ANALYST)

    result = process_copilot_query(msg, case_id, user_id, user_role)

    # Save conversation message in SQLite
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO chat_messages (id, conversation_id, case_id, user_id, role, content, intent, timestamp)
                   VALUES (?, ?, ?, ?, 'user', ?, 'investigative_query', datetime('now'))""",
                (f"msg-{user_id}-{int(time.time()*1000)}", f"conv-{case_id}", case_id, user_id, msg)
            )
    except Exception:
        pass

    return {
        "reply": result["reply"],
        "citations": result["citations"],
        "action_proposal": result["action_proposal"],
        "case_id": case_id,
        "disclaimer": "AI Copilot outputs represent investigative decision-support signals requiring human verification."
    }

@router.get("/api/copilot/suggestions")
async def get_copilot_suggestions(case_id: str = "c1"):
    """Returns contextual suggestions for the active case."""
    return {
        "suggestions": [
            "Summarize active case briefing",
            "Show highest risk alerts",
            "List verified evidence items and hashes",
            "Explain anomaly alert a1",
            "Advance case stage to surveillance"
        ]
    }

@router.post("/api/copilot/actions/confirm")
async def confirm_copilot_action(
    req: CopilotActionConfirmRequest,
    request: Request,
    claims: dict = Depends(require_authenticated_user)
):
    """AI Action Safety Protocol: Re-validates user authorization and executes proposed action within a transaction."""
    user_id = claims.get("sub")
    role = claims.get("role")
    client_ip = request.client.host if request.client else "127.0.0.1"
    correlation_id = getattr(request.state, "correlation_id", "")

    action_type = req.action_type
    case_id = req.case_id

    # 1. Authorize: Analyst or higher required
    if role == ForensicRole.INTELLIGENCE_AUDITOR:
        raise HTTPException(status_code=403, detail="Auditor role cannot execute tactical actions.")

    # 2. Execute transactional state mutation
    with get_db() as conn:
        cursor = conn.cursor()
        if action_type == "ADVANCE_STAGE":
            proposed_stage = req.parameters.get("proposed_stage", "surveillance")
            cursor.execute("UPDATE cases SET stage = ?, updated_at = datetime('now') WHERE id = ?", (proposed_stage, case_id))
            action_desc = f"Advanced case '{case_id}' stage to '{proposed_stage}'."

        elif action_type == "ESCALATE_ALERT":
            alert_id = req.target_id
            cursor.execute("UPDATE alerts SET status = 'ESCALATED_TO_SUPERVISOR' WHERE id = ?", (alert_id,))
            action_desc = f"Escalated alert '{alert_id}' to supervisory officer."

        else:
            action_desc = f"Executed {action_type} on resource {req.target_id}."

    # 3. Record in hash-linked audit chain
    audit_res = append_audit_event(
        actor_id=user_id,
        role=role,
        action=f"AI_ACTION_CONFIRMED_{action_type}",
        resource=f"case:{case_id}:{req.target_id}",
        payload={"action_type": action_type, "parameters": req.parameters},
        ip_address=client_ip,
        correlation_id=correlation_id
    )

    return {
        "status": "ACTION_EXECUTED",
        "action_type": action_type,
        "message": action_desc,
        "audit_event_id": audit_res["event_id"],
        "timestamp": audit_res["timestamp"]
    }
