import os
import base64
import hmac
import hashlib
import logging
from typing import Union
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from backend.app.config import PII_KEY_BYTES

logger = logging.getLogger("crimenet.crypto")

def encrypt_pii(plaintext: str) -> str:
    """NIST SP 800-38D compliant envelope encryption using AES-256-GCM.
    Generates a unique 96-bit (12-byte) cryptographic nonce per operation.
    Output format: enc:v1:<nonce_b64>:<ciphertext_and_tag_b64>
    """
    if not plaintext:
        return ""
    try:
        aesgcm = AESGCM(PII_KEY_BYTES)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        nonce_b64 = base64.b64encode(nonce).decode('ascii')
        ct_b64 = base64.b64encode(ciphertext).decode('ascii')
        return f"enc:v1:{nonce_b64}:{ct_b64}"
    except Exception as e:
        logger.error(f"PII Encryption failure: {e}")
        raise RuntimeError("Cryptographic operation failed during PII encryption.")

def decrypt_pii(ciphertext_str: str) -> str:
    """Decrypts AES-256-GCM envelope-encrypted PII.
    Validates authenticated tag; raises an error or returns plaintext safely.
    """
    if not ciphertext_str or not ciphertext_str.startswith("enc:v1:"):
        return ciphertext_str
    try:
        parts = ciphertext_str.split(":", 3)
        if len(parts) != 4:
            return ciphertext_str
        nonce = base64.b64decode(parts[2])
        ct_and_tag = base64.b64decode(parts[3])
        aesgcm = AESGCM(PII_KEY_BYTES)
        decrypted_bytes = aesgcm.decrypt(nonce, ct_and_tag, None)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"PII Decryption failure or tag mismatch: {e}")
        raise ValueError("Decryption failed: Ciphertext corrupted or key mismatch.")

def compute_sha256(data: Union[bytes, str]) -> str:
    """Computes standard SHA-256 hex digest."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def constant_time_compare(val1: str, val2: str) -> bool:
    """Performs constant-time comparison to prevent timing side-channel attacks."""
    if not isinstance(val1, str) or not isinstance(val2, str):
        return False
    return hmac.compare_digest(val1.encode('utf-8'), val2.encode('utf-8'))
