"""
CrimeNet AI - PostgreSQL / SQLAlchemy ORM Integration & CRUD Verification Tests
Tests core ORM entity mappings, foreign key cascading, transactional rollback atomicity,
and dual-mode database telemetry.
"""

import pytest
import uuid
import time
from backend.app.database.connection import db_session_context, check_database_health
from backend.app.models.pg_models import User, RefreshToken, Case, EvidenceItem
from backend.app.security.passwords import hash_password
from backend.app.security.crypto import compute_sha256

def test_database_health_telemetry():
    """Verify database connection health telemetry report."""
    health = check_database_health()
    assert "status" in health
    assert health["status"] in ("HEALTHY", "DEGRADED", "ONLINE")
    assert "dialect" in health
    assert health["dialect"] in ("postgresql", "sqlite")
    assert health["is_healthy"] is True

def test_user_and_token_cascade_crud():
    """Verify SQLAlchemy ORM User creation, relationship access, and token lifecycle."""
    test_id = f"usr_test_{uuid.uuid4().hex[:8]}"
    test_username = f"analyst_{uuid.uuid4().hex[:6]}"
    pass_hash, salt = hash_password("SecurePass@2026")
    
    with db_session_context() as session:
        user = User(
            id=test_id,
            username=test_username,
            email=f"{test_username}@crimenet.ai",
            password_hash=pass_hash,
            salt=salt,
            role="FORENSIC_ANALYST",
            badge=f"BADGE-{test_id[:6].upper()}"
        )
        session.add(user)
        session.flush()

        # Add a refresh token linked via foreign key
        tok_hash = compute_sha256(f"tok_{test_id}")
        refresh_tok = RefreshToken(
            token_hash=tok_hash,
            user_id=test_id,
            expires_at=time.time() + 86400,
            revoked=0
        )
        session.add(refresh_tok)
        session.flush()

    # Query back and verify in a new session
    with db_session_context() as session:
        queried_user = session.query(User).filter(User.id == test_id).first()
        assert queried_user is not None
        assert queried_user.username == test_username
        assert queried_user.role == "FORENSIC_ANALYST"
        assert len(queried_user.tokens) >= 1
        assert queried_user.tokens[0].token_hash == tok_hash

        # Update test user
        queried_user.failed_attempts = 1
        session.flush()

    # Verify update persisted
    with db_session_context() as session:
        u_updated = session.query(User).filter(User.id == test_id).first()
        assert u_updated.failed_attempts == 1

        # Delete user and verify cascade
        session.delete(u_updated)

    # Verify user and token deleted
    with db_session_context() as session:
        assert session.query(User).filter(User.id == test_id).first() is None
        assert session.query(RefreshToken).filter(RefreshToken.token_hash == tok_hash).first() is None

def test_case_and_evidence_crud():
    """Verify Case and EvidenceItem creation, custom attributes, and query retrieval."""
    case_id = f"c_{uuid.uuid4().hex[:6]}"
    ev_id = f"ev_{uuid.uuid4().hex[:6]}"
    dummy_hash = compute_sha256("test_evidence_content")

    with db_session_context() as session:
        case = Case(
            id=case_id,
            title="Operation Test Cascade",
            description="Integration verification for multi-tenant case evidence.",
            stage="evidence",
            priority="high",
            squad="Forensic Unit"
        )
        session.add(case)
        session.flush()

        ev = EvidenceItem(
            id=ev_id,
            case_id=case_id,
            source_type="DISK_IMAGE",
            filename="hdd_forensic.raw",
            mime_type="application/octet-stream",
            file_size=1048576,
            collector_id="usr-01",
            sha256_hash=dummy_hash,
            classification="CONFIDENTIAL",
            integrity_status="VERIFIED_INTACT",
            object_key=f"evidence/{case_id}/{ev_id}_hdd.raw",
            storage_provider="local_vault_fallback"
        )
        session.add(ev)
        session.flush()

    with db_session_context() as session:
        fetched_ev = session.query(EvidenceItem).filter(EvidenceItem.id == ev_id).first()
        assert fetched_ev is not None
        assert fetched_ev.case_id == case_id
        assert fetched_ev.sha256_hash == dummy_hash
        assert fetched_ev.storage_provider == "local_vault_fallback"
        assert fetched_ev.object_key.startswith("evidence/")

        # Clean up
        session.delete(fetched_ev)
        c = session.query(Case).filter(Case.id == case_id).first()
        if c:
            session.delete(c)

def test_database_session_rollback_on_error():
    """Verify that exceptions inside db_session_context trigger rollback with zero dirty writes."""
    transient_id = f"usr_transient_{uuid.uuid4().hex[:6]}"
    pass_hash, salt = hash_password("DummyPass@123")

    with pytest.raises(RuntimeError):
        with db_session_context() as session:
            user = User(
                id=transient_id,
                username="transient_user",
                email="transient@crimenet.ai",
                password_hash=pass_hash,
                salt=salt,
                role="FORENSIC_ANALYST",
                badge="BADGE-TR"
            )
            session.add(user)
            session.flush()
            # Force deliberate failure
            raise RuntimeError("Deliberate transaction failure to test rollback")

    # Assert transient record was NOT persisted
    with db_session_context() as session:
        assert session.query(User).filter(User.id == transient_id).first() is None
