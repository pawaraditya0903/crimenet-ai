import time
import socketio
import logging
from typing import Optional, Dict, Any
from backend.app.config import ALLOWED_ORIGINS
from backend.app.security.jwt import verify_jwt_token
from backend.app.security.rbac import ForensicRole
from backend.app.models.database import get_db

logger = logging.getLogger("crimenet.realtime")

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=ALLOWED_ORIGINS)
_active_sessions: Dict[str, Dict[str, Any]] = {}

@sio.event
async def connect(sid, environ, auth):
    """Authenticates incoming Socket.IO connection using JWT token."""
    token = None
    if isinstance(auth, dict):
        token = auth.get("token") or auth.get("jwt")
    
    if not token and "QUERY_STRING" in environ:
        # Extract token from query params if passed during handshake
        query = environ["QUERY_STRING"]
        for param in query.split("&"):
            if param.startswith("token="):
                token = param.split("=", 1)[1]
                break

    if not token:
        logger.warning(f"Rejected unauthenticated Socket.IO connection attempt: {sid}")
        return False  # Disconnect unauthenticated client

    claims = verify_jwt_token(token, expected_use="access")
    if not claims:
        logger.warning(f"Rejected invalid JWT Socket.IO connection attempt: {sid}")
        return False

    # Save authenticated session details
    session_data = {
        "user_id": claims.get("sub"),
        "role": claims.get("role"),
        "badge": claims.get("badge")
    }
    _active_sessions[sid] = session_data
    try:
        await sio.save_session(sid, session_data)
    except Exception:
        pass
    logger.info(f"Socket client connected: {sid} (User: {claims.get('sub')}, Role: {claims.get('role')})")
    return True

@sio.event
async def disconnect(sid):
    _active_sessions.pop(sid, None)
    logger.info(f"Socket client disconnected: {sid}")

@sio.event
async def join_case_room(sid, data):
    """Authorizes and joins a case telemetry room.
    Validates that the user is assigned to the case or has supervisory oversight.
    """
    session = _active_sessions.get(sid)
    if not session:
        try:
            session = await sio.get_session(sid)
        except Exception:
            session = None

    if not session:
        await sio.emit("error", {"message": "Unauthenticated session"}, room=sid)
        return

    case_id = str(data.get("case_id", "c1")).strip()
    user_id = session.get("user_id")
    role = session.get("role")

    # Authorization Check
    is_authorized = False
    if role == ForensicRole.SUPERVISORY_OFFICER:
        is_authorized = True
    else:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM cases WHERE id = ? AND lead_investigator_id = ?", (case_id, user_id))
            if cursor.fetchone():
                is_authorized = True
            else:
                cursor.execute("SELECT 1 FROM case_assignments WHERE case_id = ? AND user_id = ?", (case_id, user_id))
                if cursor.fetchone():
                    is_authorized = True

    if not is_authorized:
        logger.warning(f"Security Alert: User '{user_id}' denied joining room 'case_{case_id}' (Unauthorized case)")
        await sio.emit("room_join_error", {
            "case_id": case_id,
            "error": "Forbidden: You are not authorized to access this investigation case room."
        }, room=sid)
        return

    try:
        await sio.enter_room(sid, f"case_{case_id}")
    except (ValueError, KeyError) as e:
        logger.debug(f"Room enter handled without active socket transport: {e}")

    await sio.emit("room_joined", {"case_id": case_id, "status": "authorized_active"}, room=sid)
    logger.info(f"User '{user_id}' successfully joined room 'case_{case_id}'")

@sio.event
async def leave_case_room(sid, data):
    case_id = str(data.get("case_id", "c1")).strip()
    try:
        await sio.leave_room(sid, f"case_{case_id}")
    except (ValueError, KeyError) as e:
        logger.debug(f"Room leave handled without active socket transport: {e}")
    await sio.emit("room_left", {"case_id": case_id, "status": "left"}, room=sid)

async def emit_investigation_event(
    event_type: str,
    payload: Dict[str, Any],
    case_id: Optional[str] = None,
    severity: str = "info",
    actor_id: str = "SYSTEM_TELEMETRY"
) -> Dict[str, Any]:
    """Broadcasts investigation events to authorized rooms and records notifications in SQLite."""
    event_obj = {
        "event_id": f"evt-{int(time.time() * 1000)}",
        "event_type": event_type,
        "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "case_id": case_id,
        "actor_id": actor_id,
        "severity": severity,
        "payload": payload
    }

    # Store notification in SQLite
    if event_type in ["ALERT_CREATED", "RADAR_UPDATE", "EVIDENCE_ADDED", "SYSTEM_NOTIFICATION", "CASE_STAGE_UPDATED"]:
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO notifications (id, user_id, case_id, title, details, severity, is_read, timestamp)
                       VALUES (?, ?, ?, ?, ?, ?, 0, datetime('now'))""",
                    (
                        event_obj["event_id"],
                        actor_id,
                        case_id,
                        payload.get("title", f"Event: {event_type}"),
                        payload.get("details", payload.get("message", "Telemetry update received.")),
                        severity
                    )
                )
        except Exception as e:
            logger.error(f"Error persisting notification: {e}")

    try:
        if case_id:
            await sio.emit("investigation_event", event_obj, room=f"case_{case_id}")
            await sio.emit("case_event", event_obj, room=f"case_{case_id}")
        else:
            await sio.emit("investigation_event", event_obj)
    except Exception as e:
        logger.error(f"Socket emit error: {e}")

    return event_obj
