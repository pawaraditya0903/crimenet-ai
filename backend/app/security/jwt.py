import time
import json
import base64
import hmac
import hashlib
import secrets
import logging
from typing import Optional, Dict, Any, Tuple
from backend.app.config import (
    JWT_SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_SECONDS,
    REFRESH_TOKEN_EXPIRE_SECONDS,
)
from backend.app.models.database import get_db

logger = logging.getLogger("crimenet.jwt")

def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def b64url_decode(s: str) -> bytes:
    padding = 4 - (len(s) % 4)
    if padding != 4:
        s += '=' * padding
    return base64.urlsafe_b64decode(s.encode('utf-8'))

def create_jwt_token(payload: dict, expires_in_seconds: int = ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
    """Generates a secure HMAC-SHA256 JWT with an expiration timestamp and unique token ID (jti)."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload_copy = dict(payload)
    now = int(time.time())
    payload_copy["iat"] = now
    payload_copy["exp"] = now + expires_in_seconds
    if "jti" not in payload_copy:
        payload_copy["jti"] = secrets.token_hex(16)
    
    header_b64 = b64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    payload_b64 = b64url_encode(json.dumps(payload_copy, separators=(',', ':')).encode('utf-8'))
    message = f"{header_b64}.{payload_b64}".encode('utf-8')
    sig = hmac.new(JWT_SECRET_KEY.encode('utf-8'), message, hashlib.sha256).digest()
    sig_b64 = b64url_encode(sig)
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def _ensure_user_exists(cursor, user_id: str, role: str = "FORENSIC_ANALYST", badge: str = "Officer") -> str:
    cursor.execute("SELECT id FROM users WHERE id = ? OR username = ?", (user_id, user_id))
    row = cursor.fetchone()
    if row:
        return row[0] if isinstance(row, (tuple, list)) else row["id"]
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, username, email, password_hash, salt, role, badge, created_at) VALUES (?, ?, ?, 'default_hash', 'default_salt', ?, ?, datetime('now'))",
        (user_id, user_id, f"{user_id}@crimenet.ai", role, badge)
    )
    return user_id

def create_refresh_token(payload: dict, expires_in_seconds: int = REFRESH_TOKEN_EXPIRE_SECONDS) -> str:
    """Generates a refresh token with token_use='refresh' and persists it for rotation."""
    payload_copy = dict(payload)
    payload_copy["token_use"] = "refresh"
    token = create_jwt_token(payload_copy, expires_in_seconds=expires_in_seconds)
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    expires_at = time.time() + expires_in_seconds
    user_id = str(payload_copy.get("sub", "user"))
    role = str(payload_copy.get("role", "FORENSIC_ANALYST"))
    badge = str(payload_copy.get("badge", "Officer"))
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            db_user_id = _ensure_user_exists(cursor, user_id, role, badge)
            cursor.execute(
                "INSERT INTO refresh_tokens (token_hash, user_id, expires_at, revoked, created_at) VALUES (?, ?, ?, 0, datetime('now'))",
                (token_hash, db_user_id, expires_at)
            )
    except Exception as e:
        logger.error(f"Error persisting refresh token: {e}")
    return token

def verify_jwt_token(token: str, expected_use: Optional[str] = None) -> Optional[dict]:
    """Validates JWT signature, structure, and expiration in constant time."""
    if not token or not isinstance(token, str):
        return None
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        
        # Verify header specifies HS256 to reject 'none' algorithm attacks
        header = json.loads(b64url_decode(header_b64).decode('utf-8'))
        if header.get("alg") != "HS256" or header.get("typ") != "JWT":
            return None
        
        message = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = hmac.new(JWT_SECRET_KEY.encode('utf-8'), message, hashlib.sha256).digest()
        actual_sig = b64url_decode(sig_b64)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        
        payload = json.loads(b64url_decode(payload_b64).decode('utf-8'))
        if payload.get("exp", 0) < time.time():
            return None  # Expired
            
        if expected_use and payload.get("token_use", "access") != expected_use:
            return None  # Mismatched token use
            
        return payload
    except Exception as e:
        logger.debug(f"JWT verification failure: {e}")
        return None

def issue_token_pair(user_id: str, role: str, badge: str) -> Tuple[str, str]:
    """Issues an access token and a persisted, rotatable refresh token."""
    claims = {
        "sub": user_id,
        "role": role,
        "badge": badge,
        "token_use": "access"
    }
    access_token = create_jwt_token(claims, expires_in_seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    
    refresh_claims = {
        "sub": user_id,
        "role": role,
        "badge": badge,
        "token_use": "refresh"
    }
    refresh_token = create_jwt_token(refresh_claims, expires_in_seconds=REFRESH_TOKEN_EXPIRE_SECONDS)
    
    # Store refresh token hash in SQLite for rotation and revocation
    token_hash = hashlib.sha256(refresh_token.encode('utf-8')).hexdigest()
    expires_at = time.time() + REFRESH_TOKEN_EXPIRE_SECONDS
    
    with get_db() as conn:
        cursor = conn.cursor()
        db_user_id = _ensure_user_exists(cursor, user_id, role, badge)
        cursor.execute(
            "INSERT INTO refresh_tokens (token_hash, user_id, expires_at, revoked, created_at) VALUES (?, ?, ?, 0, datetime('now'))",
            (token_hash, db_user_id, expires_at)
        )
        
    return access_token, refresh_token

def rotate_refresh_token(refresh_token: str) -> Optional[Tuple[str, str]]:
    """Rotates a refresh token: validates, revokes current, and issues a fresh pair."""
    payload = verify_jwt_token(refresh_token, expected_use="refresh")
    if not payload:
        return None
        
    token_hash = hashlib.sha256(refresh_token.encode('utf-8')).hexdigest()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT revoked, expires_at FROM refresh_tokens WHERE token_hash = ?", (token_hash,))
        row = cursor.fetchone()
        if not row or row["revoked"] == 1 or row["expires_at"] < time.time():
            return None
            
        # Revoke the used refresh token immediately (Token Rotation)
        cursor.execute("UPDATE refresh_tokens SET revoked = 1 WHERE token_hash = ?", (token_hash,))
        
    user_id = payload.get("sub")
    role = payload.get("role")
    badge = payload.get("badge", "Field Investigator")
    return issue_token_pair(user_id, role, badge)

def revoke_token(refresh_token: str) -> bool:
    """Revokes a refresh token on user logout."""
    token_hash = hashlib.sha256(refresh_token.encode('utf-8')).hexdigest()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE refresh_tokens SET revoked = 1 WHERE token_hash = ?", (token_hash,))
        return cursor.rowcount > 0
