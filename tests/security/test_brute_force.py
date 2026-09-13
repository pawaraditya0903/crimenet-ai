import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.security.rate_limit import reset_failed_logins

client = TestClient(app)

def test_brute_force_login_lockout():
    attacker_ip = "192.168.1.105"
    target_user = "brute_force_target"
    reset_failed_logins(f"{target_user}@{attacker_ip}")

    # 4 Failed login attempts return 401
    for _ in range(4):
        res = client.post("/api/auth/token", json={
            "username": target_user,
            "password": "WrongPassword!"
        }, headers={"X-Forwarded-For": attacker_ip})
        assert res.status_code == 401

    # 5th failed attempt triggers lockout (429)
    fifth_res = client.post("/api/auth/token", json={
        "username": target_user,
        "password": "WrongPassword!"
    }, headers={"X-Forwarded-For": attacker_ip})
    assert fifth_res.status_code == 429
    assert "locked" in fifth_res.json()["detail"].lower()

    # Subsequent attempt within cooldown window is immediately blocked with 429
    locked_res = client.post("/api/auth/token", json={
        "username": target_user,
        "password": "EvenCorrectPasswordNowFails"
    }, headers={"X-Forwarded-For": attacker_ip})
    assert locked_res.status_code == 429
