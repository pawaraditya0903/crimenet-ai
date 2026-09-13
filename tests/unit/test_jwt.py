import time
import pytest
from backend.app.security.jwt import create_jwt_token, verify_jwt_token

def test_jwt_issuance_and_verification():
    claims = {"sub": "usr-test-01", "role": "LEAD_INVESTIGATOR", "badge": "Special Agent"}
    token = create_jwt_token(claims, expires_in_seconds=300)
    
    verified = verify_jwt_token(token, expected_use="access")
    assert verified is not None
    assert verified["sub"] == "usr-test-01"
    assert verified["role"] == "LEAD_INVESTIGATOR"

def test_jwt_expiration():
    claims = {"sub": "usr-expired", "role": "FORENSIC_ANALYST"}
    # Token expired 10 seconds ago
    token = create_jwt_token(claims, expires_in_seconds=-10)
    
    assert verify_jwt_token(token) is None

def test_jwt_tampered_signature():
    claims = {"sub": "usr-legit", "role": "FORENSIC_ANALYST"}
    token = create_jwt_token(claims, expires_in_seconds=300)
    parts = token.split(".")
    
    # Tamper payload
    tampered_token = f"{parts[0]}.eyJuYW1lIjoiSGFja2VyIn0.{parts[2]}"
    assert verify_jwt_token(tampered_token) is None
