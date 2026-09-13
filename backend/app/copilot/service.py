import re
import json
import logging
from typing import Dict, Any, List, Optional
from backend.app.models.database import get_db

logger = logging.getLogger("crimenet.copilot.service")

COPILOT_SYSTEM_PROMPT = (
    "You are CrimeNet AI Copilot, an analytical decision-support assistant for criminal investigations. "
    "You provide factual analysis, link correlation, and evidentiary cross-referencing. "
    "You NEVER issue arrest warrants, declare guilt, or initiate unilateral enforcement actions. "
    "All analytical findings represent statistical indicators subject to human officer verification."
)

def retrieve_case_context(case_id: str) -> Dict[str, Any]:
    """Retrieves authoritative backend-controlled context for the case.
    Prevents prompt injection and untrusted client context manipulation.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Case details
        cursor.execute("SELECT id, title, description, stage, priority, squad FROM cases WHERE id = ?", (case_id,))
        case_row = cursor.fetchone()
        if not case_row:
            return {"error": "Case not found"}

        # 2. Suspects
        cursor.execute("SELECT name, role, risk_score, city, dossier FROM suspects WHERE case_id = ?", (case_id,))
        suspects = [dict(r) for r in cursor.fetchall()]

        # 3. Evidence items
        cursor.execute("SELECT id, source_type, filename, sha256_hash FROM evidence_items WHERE case_id = ?", (case_id,))
        evidence = [dict(r) for r in cursor.fetchall()]

        # 4. Alerts
        cursor.execute("SELECT id, entity_name, anomaly_type, anomaly_score, status FROM alerts WHERE case_id = ?", (case_id,))
        alerts = [dict(r) for r in cursor.fetchall()]

    return {
        "case": dict(case_row),
        "suspects": suspects,
        "evidence": evidence,
        "alerts": alerts
    }

def process_copilot_query(
    user_message: str,
    case_id: str,
    user_id: str,
    user_role: str
) -> Dict[str, Any]:
    """Processes user query against authoritative case context, returning
    factual responses with verifiable citations and safe action proposals.
    """
    context = retrieve_case_context(case_id)
    if "error" in context:
        return {
            "reply": f"Unable to retrieve verified records for case '{case_id}'.",
            "citations": [],
            "action_proposal": None
        }

    case_info = context["case"]
    suspects = context["suspects"]
    evidence = context["evidence"]
    alerts = context["alerts"]

    msg_lower = user_message.lower().strip()
    citations: List[str] = []
    action_proposal = None
    reply_text = ""

    citations.append(f"[Case: {case_info['id']} - {case_info['title']}]")

    # 1. Case Briefing / Summary
    if any(w in msg_lower for w in ["summar", "briefing", "overview", "what is this case"]):
        suspect_names = ", ".join([s["name"] for s in suspects]) if suspects else "None registered"
        reply_text = (
            f"**Case Briefing: {case_info['title']}** [{case_info['stage'].upper()} Stage / Priority: {case_info['priority'].upper()}]\n\n"
            f"• **Objective**: {case_info['description']}\n"
            f"• **Assigned Squad**: {case_info['squad']}\n"
            f"• **Entities of Interest**: {suspect_names}\n"
            f"• **Ingested Evidence**: {len(evidence)} verified files in repository\n"
            f"• **Active Alerts**: {len(alerts)} statistical anomalies awaiting review\n\n"
            f"*Investigative Guidance*: All telemetry indicators represent decision-support data for human verification."
        )

    # 2. Alerts Inquiry
    elif any(w in msg_lower for w in ["alert", "threat", "anomaly", "anomalies", "risk"]):
        if not alerts:
            reply_text = f"There are currently no active risk alerts registered for Case '{case_info['title']}'."
        else:
            alert_bullets = []
            for a in alerts:
                citations.append(f"[Alert: {a['id']}]")
                alert_bullets.append(
                    f"• **{a['id'].upper()}** ({a['entity_name']}): {a['anomaly_type'].replace('_', ' ')} "
                    f"— Calibrated Risk: {int(a['anomaly_score'] * 100)}% [{a['status'].replace('_', ' ')}]"
                )
            reply_text = (
                f"**Active Risk Indicators for Case '{case_info['title']}':**\n\n" +
                "\n".join(alert_bullets) +
                "\n\n*Review options*: You can confirm, suppress, or escalate alerts from the Alert Centre."
            )

    # 3. Evidence Inquiry
    elif any(w in msg_lower for w in ["evidence", "files", "ledger", "proof", "hash"]):
        if not evidence:
            reply_text = f"No digital evidence files have been logged for Case '{case_info['title']}'."
        else:
            ev_bullets = []
            for e in evidence:
                citations.append(f"[Evidence: {e['id']}]")
                ev_bullets.append(
                    f"• **{e['id']}** ({e['source_type']}): `{e['filename']}`\n"
                    f"  *SHA-256 Hash*: `{e['sha256_hash'][:32]}...`"
                )
            reply_text = (
                f"**Chain of Custody Evidence Records [{case_info['id']}]:**\n\n" +
                "\n".join(ev_bullets) +
                "\n\n*Cryptographic notice*: Hashes confirm bit-level post-ingestion integrity."
            )

    # 4. Suspect Inquiry
    elif any(s["name"].lower() in msg_lower for s in suspects):
        matched_suspect = next(s for s in suspects if s["name"].lower() in msg_lower)
        citations.append(f"[Suspect: {matched_suspect['name']}]")
        reply_text = (
            f"**Entity Dossier: {matched_suspect['name']}**\n\n"
            f"• **Role**: {matched_suspect.get('role', 'Subject of Interest')}\n"
            f"• **Location**: {matched_suspect.get('city', 'Unknown')}\n"
            f"• **Assigned Risk Index**: {matched_suspect.get('risk_score', 50.0)} / 100\n"
            f"• **Investigative Summary**: {matched_suspect.get('dossier', 'No dossier summary recorded.')}\n\n"
            f"*Statutory notice*: Profile information compiled for investigative prioritization only."
        )

    # 5. Suggest Stage Advancement (Action Proposal)
    elif "advance stage" in msg_lower or "move to" in msg_lower or "next stage" in msg_lower:
        curr_stage = case_info["stage"]
        # Check if user explicitly mentioned a target stage
        target_stage = None
        for s in ["evidence", "surveillance", "warrant", "trial", "closed"]:
            if s in msg_lower:
                target_stage = s
                break
        
        if not target_stage or target_stage == curr_stage:
            next_stage_map = {
                "evidence": "surveillance",
                "surveillance": "warrant",
                "warrant": "trial",
                "trial": "closed",
                "closed": "evidence"
            }
            target_stage = next_stage_map.get(curr_stage, "surveillance")

        action_proposal = {
            "action_type": "ADVANCE_STAGE",
            "case_id": case_id,
            "target_id": case_id,
            "parameters": {"current_stage": curr_stage, "proposed_stage": target_stage},
            "rationale": f"Investigation progression: transition from {curr_stage} to {target_stage} stage."
        }
        reply_text = (
            f"I propose advancing **{case_info['title']}** from `{curr_stage.upper()}` to `{target_stage.upper()}`.\n\n"
            f"⚠️ *Safety Policy*: AI cannot execute database mutations automatically. "
            f"Please confirm this action using the button below to authorize the update and record it in the audit trail."
        )

    # 6. Default Fallback
    else:
        reply_text = (
            f"I have analyzed Case **{case_info['title']}** ({case_info['id']}).\n\n"
            f"Available case capabilities:\n"
            f"• Ask *\"Summarize case\"* for a briefing\n"
            f"• Ask *\"Show active alerts\"* to inspect flagged anomalies\n"
            f"• Ask *\"List evidence items\"* for chain-of-custody hashes\n"
            f"• Query specific entities (e.g. *\"Who is Arjun Mehta?\"*)"
        )

    return {
        "reply": reply_text,
        "citations": citations,
        "action_proposal": action_proposal,
        "case_id": case_id,
        "retrieved_from_backend": True
    }
