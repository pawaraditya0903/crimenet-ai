import pytest
import time
import json
import base64
import hmac
import hashlib
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.security.jwt import b64url_encode, create_jwt_token

client = TestClient(app)

def test_reject_none_algorithm_jwt():
    header = {"alg": "none", "typ": "JWT"}
    payload = {"sub": "attacker", "role": "SUPERVISORY_OFFICER", "exp": int(time.time()) + 3600}
    token = f"{b64url_encode(json.dumps(header).encode())}.{b64url_encode(json.dumps(payload).encode())}."
    
    res = client.get("/api/auth/verify-token", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401

def test_reject_forged_signature_jwt():
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": "attacker", "role": "SUPERVISORY_OFFICER", "exp": int(time.time()) + 3600}
    header_b64 = b64url_encode(json.dumps(header).encode())
    payload_b64 = b64url_encode(json.dumps(payload).encode())
    # Signed with wrong key
    wrong_sig = b64url_encode(hmac.new(b"WRONG_ATTACKER_SECRET", f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).digest())
    token = f"{header_b64}.{payload_b64}.{wrong_sig}"

    res = client.get("/api/auth/verify-token", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401

def test_reject_expired_jwt():
    claims = {"sub": "usr-test", "role": "FORENSIC_ANALYST"}
    expired_token = create_jwt_token(claims, expires_in_seconds=-60)
    
    res = client.get("/api/auth/verify-token", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401

def test_reject_missing_jwt():
    res = client.get("/api/auth/verify-token")
    assert res.status_code == 401
