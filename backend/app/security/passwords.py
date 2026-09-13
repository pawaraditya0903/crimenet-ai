import os
import re
import hmac
import hashlib
from typing import Optional, Tuple
from backend.app.config import PBKDF2_ITERATIONS

def hash_password(password: str, salt: Optional[bytes] = None, iterations: int = PBKDF2_ITERATIONS) -> Tuple[str, str]:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a 16-byte cryptographically random salt.
    Returns (formatted_hash, salt_hex).
    """
    if not password:
        raise ValueError("Password cannot be empty")
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.strip().encode('utf-8'), salt, iterations)
    salt_hex = salt.hex()
    dk_hex = dk.hex()
    formatted = f"pbkdf2:sha256:{iterations}${salt_hex}${dk_hex}"
    return formatted, salt_hex

def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verifies a plain password against stored hash using constant-time comparison."""
    if not plain_password or not stored_hash:
        return False
    
    plain_bytes = plain_password.strip().encode('utf-8')
    
    if stored_hash.startswith("pbkdf2:sha256:"):
        try:
            parts = stored_hash.split("$")
            if len(parts) != 3:
                return False
            header = parts[0]
            iters = int(header.split(":")[-1])
            salt = bytes.fromhex(parts[1])
            expected_hex = parts[2]
            computed = hashlib.pbkdf2_hmac('sha256', plain_bytes, salt, iters).hex()
            return hmac.compare_digest(computed, expected_hex)
        except Exception:
            return False
            
    # Legacy unsalted SHA-256 fallback for migration
    computed_legacy = hashlib.sha256(plain_bytes).hexdigest()
    return hmac.compare_digest(computed_legacy, stored_hash)

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Validates strong password policy:
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    - At least 1 special character
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
    if not re.search(r'[@$!%*#?&_\-\.]', password):
        return False, "Password must contain at least one special character (@$!%*#?&_-.)."
    return True, "Password meets complexity requirements."
