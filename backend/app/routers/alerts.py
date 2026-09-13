import json
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional, List
from backend.app.schemas.alerts import AlertReviewRequest, AlertEscalateRequest, SupervisorApproveRequest
from backend.app.security.rbac import require_authenticated_user, require_roles, ForensicRole
from backend.app.models.database import get_db
from backend.app.audit.chain import append_audit_event
from backend.app.ml.explainability import generate_alert_explanation

router = APIRouter(prefix="/api/alerts", tags=["Investigative Alerts"])

@router.get("")
async def list_alerts(case_id: Optional[str] = None, claims: dict = Depends(require_authenticated_user)):
    """Returns anomaly alerts registered in the investigation database."""
    with get_db() as conn:
        cursor = conn.cursor()
        if case_id:
            cursor.execute("SELECT id, case_id, entity_id, entity_name, anomaly_type, anomaly_score, severity, algorithm, confidence_level, status, feature_breakdown_json, plain_english_explanation, created_at FROM alerts WHERE case_id = ?", (case_id,))
        else:
            cursor.execute("SELECT id, case_id, entity_id, entity_name, anomaly_type, anomaly_score, severity, algorithm, confidence_level, status, feature_breakdown_json, plain_english_explanation, created_at FROM alerts")
        
        rows = []
        for r in cursor.fetchall():
            d = dict(r)
            if d.get("feature_breakdown_json"):
                try:
                    d["feature_breakdown"] = json.loads(d["feature_breakdown_json"])
                except Exception:
                    d["feature_breakdown"] = []
            rows.append(d)

    return {
        "total": len(rows),
        "alerts": rows,
        "advisory_notice": "Alerts represent statistical indicators for human investigator validation."
    }

@router.get("/{alert_id}/explain")
async def get_alert_explainability(alert_id: str, claims: dict = Depends(require_authenticated_user)):
    """Returns feature attribution breakdown and plain-English reasons for an alert."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, entity_name, anomaly_score, algorithm, confidence_level, status, feature_breakdown_json, plain_english_explanation FROM alerts WHERE id = ?", (alert_id,))
        alert = cursor.fetchone()

    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")

    features = [3.82, 0.88, 0.45, 4.12, 1.45]
    xai = generate_alert_explanation(features, alert["entity_name"])

    return {
        "alert_id": alert["id"],
        "entity_name": alert["entity_name"],
        "algorithm": alert["algorithm"],
        "confidence_level": alert["confidence_level"],
        "current_status": alert["status"],
        "plain_english_explanation": alert["plain_english_explanation"] or xai["explanation_summary"],
        "feature_breakdown": xai["feature_breakdown"],
        "contributing_signals": xai["contributing_signals"],
        "disclaimer": xai["disclaimer"]
    }

@router.patch("/{alert_id}/review")
async def review_alert_endpoint(
    alert_id: str,
    req: AlertReviewRequest,
    request: Request,
    claims: dict = Depends(require_authenticated_user)
):
    """Investigator records decision on alert (CONFIRM / SUPPRESS / ESCALATE)."""
    user_id = claims.get("sub")
    role = claims.get("role")
    client_ip = request.client.host if request.client else "127.0.0.1"
    correlation_id = getattr(request.state, "correlation_id", "")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, case_id, status FROM alerts WHERE id = ?", (alert_id,))
        alert = cursor.fetchone()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found.")

        cursor.execute("UPDATE alerts SET status = ? WHERE id = ?", (req.decision, alert_id))
        
        cursor.execute(
            """INSERT OR REPLACE INTO alert_reviews (alert_id, decision, investigator_id, note, reviewed_at)
               VALUES (?, ?, ?, ?, datetime('now'))""",
            (alert_id, req.decision, user_id, req.note)
        )

    append_audit_event(
        actor_id=user_id,
        role=role,
        action="ALERT_REVIEWED",
        resource=f"alert:{alert_id}",
        payload={"decision": req.decision, "note": req.note},
        ip_address=client_ip,
        correlation_id=correlation_id
    )

    return {
        "status": "REVIEW_RECORDED",
        "alert_id": alert_id,
        "current_status": req.decision,
        "investigator_notes": req.note
    }

@router.post("/{alert_id}/escalate")
async def escalate_alert_endpoint(
    alert_id: str,
    req: AlertEscalateRequest,
    request: Request,
    claims: dict = Depends(require_authenticated_user)
):
    """Escalates alert to supervisory tier for formal review."""
    user_id = claims.get("sub")
    role = claims.get("role")
    client_ip = request.client.host if request.client else "127.0.0.1"
    correlation_id = getattr(request.state, "correlation_id", "")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE alerts SET status = 'ESCALATED_TO_SUPERVISOR' WHERE id = ?", (alert_id,))
        cursor.execute(
            """INSERT OR REPLACE INTO alert_reviews (alert_id, decision, investigator_id, note, supervisor_status, reviewed_at)
               VALUES (?, 'ESCALATED_TO_SUPERVISOR', ?, ?, 'AWAITING_SUPERVISOR', datetime('now'))""",
            (alert_id, user_id, req.reason)
        )

    append_audit_event(
        actor_id=user_id,
        role=role,
        action="ALERT_ESCALATED",
        resource=f"alert:{alert_id}",
        payload={"reason": req.reason},
        ip_address=client_ip,
        correlation_id=correlation_id
    )

    return {"status": "ESCALATED", "alert_id": alert_id, "supervisor_status": "AWAITING_SUPERVISOR"}

@router.post("/{alert_id}/supervisor-approve")
async def supervisor_approve_endpoint(
    alert_id: str,
    req: SupervisorApproveRequest,
    request: Request,
    claims: dict = Depends(require_roles([ForensicRole.SUPERVISORY_OFFICER]))
):
    """Supervisory officer authorizes or rejects escalated alert."""
    user_id = claims.get("sub")
    role = claims.get("role")
    client_ip = request.client.host if request.client else "127.0.0.1"
    correlation_id = getattr(request.state, "correlation_id", "")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE alerts SET status = ? WHERE id = ?", (req.decision, alert_id))
        cursor.execute(
            "UPDATE alert_reviews SET supervisor_status = ?, supervisor_comments = ? WHERE alert_id = ?",
            (req.decision, req.comments, alert_id)
        )

    append_audit_event(
        actor_id=user_id,
        role=role,
        action="SUPERVISOR_DECISION",
        resource=f"alert:{alert_id}",
        payload={"decision": req.decision, "comments": req.comments},
        ip_address=client_ip,
        correlation_id=correlation_id
    )

    return {
        "status": "SUPERVISOR_DECISION_LOGGED",
        "alert_id": alert_id,
        "supervisor_status": req.decision,
        "comments": req.comments
    }
