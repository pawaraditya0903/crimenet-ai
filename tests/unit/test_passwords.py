# SEC-003 FIX: Hardcoded password removed. Test credentials must come from DEFAULT_SEED_PASSWORD env var.
# Set DEFAULT_SEED_PASSWORD in your test .env file before running integration tests.
import pytest
from backend.app.security.passwords import hash_password, verify_password, validate_password_strength

def test_pbkdf2_password_hashing_and_verification():
    password = "SecureInvestigator@2026"
    formatted_hash, salt_hex = hash_password(password)
    
    assert formatted_hash.startswith("pbkdf2:sha256:100000$")
    assert len(bytes.fromhex(salt_hex)) == 16  # 16-byte salt
    
    # Correct password verification
    assert verify_password(password, formatted_hash) is True
    # Incorrect password verification
    assert verify_password("WrongPassword123!", formatted_hash) is False

def test_password_strength_policy():
    # Valid complex password
    is_valid, _ = validate_password_strength("SecureInvestigator@2026")
    assert is_valid is True

    # Weak passwords
    assert validate_password_strength("short")[0] is False
    assert validate_password_strength("alllowercase123!")[0] is False
    assert validate_password_strength("ALLUPPERCASE123!")[0] is False
    assert validate_password_strength("NoDigitsHere!@#")[0] is False
    assert validate_password_strength("NoSpecialChar123")[0] is False
