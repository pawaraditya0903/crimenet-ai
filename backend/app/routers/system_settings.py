import os
import json
import uuid
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["System Settings & Investigator Roster"])

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "crimenet_settings.json")

# In-memory storage with high-fidelity production defaults
SYSTEM_SETTINGS: Dict[str, Any] = {
    "agency": "CrimeNet Special Operations Intelligence Directorate (Central Command)",
    "jurisdiction": "Multi-Jurisdictional Inter-State Cyber & Hawala Taskforce (India)",
    "retention": "7 Years (PMLA & IT Act Statutory Requirement)",
    "telegram_alerts": True,
    "sms_raid_broadcast": False,
    "face_sensitivity": 0.82,
    "auto_lock_timeout": 15,
    "require_password_complexity": True,
    "multi_frame_averaging": True,
    "sound_enabled": True,
    "audio_theme": "cyber_subtle",
    "desktop_notifications": True,
    "toast_duration": 4,
    "critical_alerts_only_sound": False,
    "accent_theme": "cyan",
    "compact_mode": False,
    "scanlines_effect": True,
    "reduce_motion": False,
    "high_contrast": False,
    "default_case": "c1",
    "graph_layout": "force_directed",
    "simulation_tick_rate": 1.5,
    "anomaly_contamination": 0.044,
    "pmla_threshold_inr": 50000.0
}

# Try loading from disk if available
try:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            disk_data = json.load(f)
            if isinstance(disk_data, dict):
                if "settings" in disk_data:
                    SYSTEM_SETTINGS.update(disk_data["settings"])
except Exception:
    pass

def save_to_disk():
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({"settings": SYSTEM_SETTINGS, "investigators": INVESTIGATORS}, f, indent=2)
    except Exception:
        pass

INVESTIGATORS: List[Dict[str, Any]] = [
    {
        "id": "inv-1",
        "name": "Aditya Pawar",
        "email": "aditya.pawar@crimenet.ai",
        "badge": "INV-2026-AP01",
        "role": "Chief Intelligence Architect & Lead",
        "clearance": "Top Secret / Level 5",
        "skills": ["Telecom CDR & Tower Triangulation", "Cyber Forensics & Dark Web Tracing", "PMLA & Hawala Financial Auditing"]
    },
    {
        "id": "inv-2",
        "name": "Ramesh Sharma",
        "email": "ramesh.sharma@crimenet.ai",
        "badge": "INV-2026-RS02",
        "role": "Hawala & PMLA Financial Auditor",
        "clearance": "Secret / Level 4",
        "skills": ["PMLA & Hawala Financial Auditing", "Cryptocurrency & Blockchain Forensics"]
    },
    {
        "id": "inv-3",
        "name": "Suresh Kadam",
        "email": "suresh.kadam@crimenet.ai",
        "badge": "INV-2026-SK03",
        "role": "Cellular CDR & Tower Analyst",
        "clearance": "Secret / Level 4",
        "skills": ["Telecom CDR & Tower Triangulation", "ANPR Vehicle Toll Interception"]
    }
]

class CreateInvestigatorRequest(BaseModel):
    name: str
    email: Optional[str] = None
    role: Optional[str] = "Field Investigator"
    clearance: Optional[str] = "Secret / Level 3"
    skills: Optional[List[str]] = ["Field Investigation"]

@router.get("/settings")
async def get_system_settings():
    """Returns platform configuration, UI themes, and security parameters."""
    return SYSTEM_SETTINGS

@router.post("/settings")
async def update_system_settings(payload: Dict[str, Any]):
    """Updates platform configuration and operational parameters."""
    global SYSTEM_SETTINGS
    SYSTEM_SETTINGS.update(payload)
    save_to_disk()
    return {
        "status": "SETTINGS_SAVED",
        "settings": SYSTEM_SETTINGS
    }

@router.get("/investigators")
async def list_investigators():
    """Returns active roster of registered intelligence investigators and clearances."""
    return {
        "total": len(INVESTIGATORS),
        "investigators": INVESTIGATORS
    }

@router.post("/investigators")
async def create_investigator(req: CreateInvestigatorRequest):
    """Adds a new sworn investigator to the active clearance roster."""
    new_id = f"inv-{uuid.uuid4().hex[:6]}"
    badge_prefix = req.name[:2].upper() if len(req.name) >= 2 else "IN"
    badge = f"INV-2026-{badge_prefix}{uuid.uuid4().hex[:3].upper()}"
    email = req.email or f"{req.name.lower().replace(' ', '')}@crimenet.ai"

    inv_obj = {
        "id": new_id,
        "name": req.name.strip(),
        "email": email,
        "badge": badge,
        "role": req.role,
        "clearance": req.clearance,
        "skills": req.skills or ["Field Investigation"]
    }
    INVESTIGATORS.append(inv_obj)
    save_to_disk()
    return {
        "status": "INVESTIGATOR_CREATED",
        "investigator": inv_obj
    }

@router.delete("/investigators/{investigator_id}")
async def delete_investigator(investigator_id: str):
    """Revokes credentials and removes investigator from the roster."""
    global INVESTIGATORS
    original_len = len(INVESTIGATORS)
    INVESTIGATORS = [inv for inv in INVESTIGATORS if inv["id"] != investigator_id]
    if len(INVESTIGATORS) == original_len:
        raise HTTPException(status_code=404, detail="Investigator not found.")
    save_to_disk()
    return {
        "status": "INVESTIGATOR_DELETED",
        "id": investigator_id
    }
