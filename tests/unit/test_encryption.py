import pytest
from backend.app.security.crypto import encrypt_pii, decrypt_pii

def test_aes_256_gcm_encryption_roundtrip():
    plaintext = "+91-9876543210 (Target MSISDN / Bank Account #8912)"
    ciphertext = encrypt_pii(plaintext)
    
    assert ciphertext.startswith("enc:v1:")
    assert ciphertext != plaintext
    
    decrypted = decrypt_pii(ciphertext)
    assert decrypted == plaintext

def test_aes_256_gcm_unique_nonce_per_operation():
    plaintext = "CONFIDENTIAL_OPERATIVE_IDENTITY"
    ct1 = encrypt_pii(plaintext)
    ct2 = encrypt_pii(plaintext)
    
    # Same plaintext encrypted twice must yield different ciphertexts due to fresh 96-bit nonces
    assert ct1 != ct2
    assert decrypt_pii(ct1) == plaintext
    assert decrypt_pii(ct2) == plaintext

def test_aes_256_gcm_tampered_ciphertext_detection():
    plaintext = "SECRET_INVESTIGATOR_NOTES"
    ct = encrypt_pii(plaintext)
    parts = ct.split(":")
    
    # Corrupt last character of ciphertext
    corrupted_ct_b64 = parts[3][:-1] + ("A" if parts[3][-1] != "A" else "B")
    tampered_ct = f"{parts[0]}:{parts[1]}:{parts[2]}:{corrupted_ct_b64}"
    
    with pytest.raises(ValueError):
        decrypt_pii(tampered_ct)
