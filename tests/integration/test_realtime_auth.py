import pytest
from backend.app.realtime.socket_manager import sio, connect, join_case_room
from backend.app.security.jwt import create_jwt_token
from backend.app.security.rbac import ForensicRole

@pytest.mark.asyncio
async def test_socket_connection_rejected_without_auth():
    # 1. Rejection on missing token
    accepted = await connect("mock-sid-1", {}, auth=None)
    assert accepted is False

@pytest.mark.asyncio
async def test_socket_connection_rejected_with_forged_token():
    # 2. Rejection on invalid token
    accepted = await connect("mock-sid-2", {}, auth={"token": "invalid.jwt.signature"})
    assert accepted is False

@pytest.mark.asyncio
async def test_socket_connection_accepted_with_valid_token():
    # 3. Acceptance on valid access token
    valid_token = create_jwt_token(
        {"sub": "usr-01", "role": ForensicRole.SUPERVISORY_OFFICER, "badge": "Chief", "token_use": "access"},
        expires_in_seconds=900
    )
    accepted = await connect("mock-sid-3", {}, auth={"token": valid_token})
    assert accepted is True
    from backend.app.realtime.socket_manager import _active_sessions
    session = _active_sessions.get("mock-sid-3")
    assert session is not None
    assert session["user_id"] == "usr-01"
    assert session["role"] == ForensicRole.SUPERVISORY_OFFICER

@pytest.mark.asyncio
async def test_socket_room_access_control():
    # Analyst (usr-03) assigned to c1, but NOT c2
    analyst_token = create_jwt_token(
        {"sub": "usr-03", "role": ForensicRole.FORENSIC_ANALYST, "badge": "Analyst", "token_use": "access"},
        expires_in_seconds=900
    )
    await connect("mock-sid-analyst", {}, auth={"token": analyst_token})

    # Unauthorized case room attempt (c2)
    emitted = []
    original_emit = sio.emit

    async def mock_emit(event, data, room=None):
        emitted.append((event, data, room))

    sio.emit = mock_emit
    try:
        # Join unauthorized room
        await join_case_room("mock-sid-analyst", {"case_id": "c2"})
        error_events = [e for e in emitted if e[0] == "room_join_error"]
        assert len(error_events) > 0
        assert "Forbidden" in error_events[0][1]["error"]

        # Join authorized room (c1)
        emitted.clear()
        await join_case_room("mock-sid-analyst", {"case_id": "c1"})
        joined_events = [e for e in emitted if e[0] == "room_joined"]
        assert len(joined_events) > 0
        assert joined_events[0][1]["status"] == "authorized_active"
    finally:
        sio.emit = original_emit
