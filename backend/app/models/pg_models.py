"""
CrimeNet AI - Relational Models for PostgreSQL + PostGIS (with SQLite fallback)
Implements all entities, constraints, foreign keys, timestamps, indexes,
and PostGIS spatial coordinate representations.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
    CheckConstraint,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
from geoalchemy2 import Geometry

from backend.app.database.base import Base

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

class SafePointGeometry(TypeDecorator):
    """Dialect-adaptive geometry type:
    Uses PostGIS Geometry('POINT', srid=4326) on PostgreSQL,
    and falls back to standard Text representation on SQLite.
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Geometry(geometry_type="POINT", srid=4326, spatial_index=True))
        return dialect.type_descriptor(Text())

# ── 1. USERS & ACCESS CONTROL ──
class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True)
    username = Column(String(128), unique=True, nullable=False, index=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    salt = Column(String(128), nullable=False)
    role = Column(String(64), nullable=False)
    badge = Column(String(256), nullable=True)
    failed_attempts = Column(Integer, default=0, nullable=False)
    lockout_until = Column(Float, default=0.0, nullable=False)
    created_at = Column(String(64), default=utc_now_iso, nullable=False)

    tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    case_assignments = relationship("CaseAssignment", back_populates="user", cascade="all, delete-orphan")

# ── 2. REFRESH TOKENS (ROTATION & REVOCATION) ──
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token_hash = Column(String(128), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(Float, nullable=False)
    revoked = Column(Integer, default=0, nullable=False)
    created_at = Column(String(64), default=utc_now_iso, nullable=False)

    user = relationship("User", back_populates="tokens")

# ── 3. INVESTIGATION CASES ──
class Case(Base):
    __tablename__ = "cases"

    id = Column(String(64), primary_key=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    stage = Column(String(64), default="evidence", nullable=False)
    priority = Column(String(32), default="high", nullable=False)
    lead_investigator_id = Column(String(64), nullable=True)
    squad = Column(String(128), nullable=False)
    suspects = Column(Text, nullable=True)  # Legacy string representation
    created_at = Column(String(64), default=utc_now_iso, nullable=False)
    updated_at = Column(String(64), default=utc_now_iso, nullable=False)

    suspect_records = relationship("Suspect", back_populates="case", cascade="all, delete-orphan")
    evidence_records = relationship("EvidenceItem", back_populates="case", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="case", cascade="all, delete-orphan")
    assignments = relationship("CaseAssignment", back_populates="case", cascade="all, delete-orphan")

# ── 4. CASE ASSIGNMENTS (RBAC & IDOR PREVENTION) ──
class CaseAssignment(Base):
    __tablename__ = "case_assignments"

    case_id = Column(String(64), ForeignKey("cases.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = Column(String(64), default=utc_now_iso, nullable=False)

    case = relationship("Case", back_populates="assignments")
    user = relationship("User", back_populates="case_assignments")

# ── 5. SUSPECTS ──
class Suspect(Base):
    __tablename__ = "suspects"

    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(256), nullable=False, index=True)
    aliases = Column(Text, nullable=True)
    risk_score = Column(Float, default=50.0, nullable=False)
    role = Column(String(128), nullable=True)
    city = Column(String(128), nullable=True)
    phone = Column(String(64), nullable=True)
    dossier = Column(Text, nullable=True)
    created_at = Column(String(64), default=utc_now_iso, nullable=False)

    case = relationship("Case", back_populates="suspect_records")

# ── 6. EVIDENCE ITEMS (CHAIN OF CUSTODY & S3 METADATA) ──
class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = Column(String(64), nullable=False)
    filename = Column(String(256), nullable=False)
    mime_type = Column(String(128), default="application/octet-stream", nullable=False)
    file_size = Column(Integer, default=0, nullable=False)
    collector_id = Column(String(64), nullable=False)
    ingested_at = Column(String(64), default=utc_now_iso, nullable=False)
    sha256_hash = Column(String(64), nullable=False, index=True)
    classification = Column(String(64), default="RESTRICTED_SYNTHETIC_DEMO", nullable=False)
    integrity_status = Column(String(64), default="VERIFIED_INTACT", nullable=False)
    
    # S3 / MinIO Object Storage Location
    object_key = Column(String(512), nullable=True, index=True)
    storage_provider = Column(String(32), default="minio", nullable=False)
    storage_metadata_json = Column(Text, nullable=True)

    case = relationship("Case", back_populates="evidence_records")

# ── 7. CELL TOWERS (POSTGIS GEOMETRY) ──
class CellTower(Base):
    __tablename__ = "cell_towers"

    id = Column(String(64), primary_key=True)
    tower_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(256), nullable=False)
    city = Column(String(128), nullable=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    geom = Column(SafePointGeometry, nullable=True)
    coverage_radius_meters = Column(Float, default=1500.0, nullable=False)
    created_at = Column(String(64), default=utc_now_iso, nullable=False)

# ── 8. TELECOM CDR RECORDS (POSTGIS SPATIOTEMPORAL) ──
class TelecomRecord(Base):
    __tablename__ = "cdr_records"

    id = Column(String(64), primary_key=True)
    call_id = Column(String(64), unique=True, nullable=False, index=True)
    caller = Column(String(64), nullable=False, index=True)
    receiver = Column(String(64), nullable=False, index=True)
    timestamp = Column(String(64), nullable=False, index=True)
    duration_sec = Column(Integer, default=0, nullable=False)
    tower_id = Column(String(64), nullable=True, index=True)
    tower_name = Column(String(256), nullable=True)
    imei = Column(String(32), nullable=True, index=True)
    imsi = Column(String(32), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    geom = Column(SafePointGeometry, nullable=True)
    call_type = Column(String(64), default="OUTBOUND_VOICE", nullable=False)
    created_at = Column(String(64), default=utc_now_iso, nullable=False)

# ── 9. ANPR CAMERAS (POSTGIS GEOMETRY) ──
class ANPRCamera(Base):
    __tablename__ = "anpr_cameras"

    id = Column(String(64), primary_key=True)
    camera_id = Column(String(64), unique=True, nullable=False, index=True)
    location_name = Column(String(256), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    geom = Column(SafePointGeometry, nullable=True)
    created_at = Column(String(64), default=utc_now_iso, nullable=False)

# ── 10. ANPR SIGHTING RECORDS (POSTGIS SPATIOTEMPORAL) ──
class ANPRRecord(Base):
    __tablename__ = "anpr_records"

    id = Column(String(64), primary_key=True)
    detection_id = Column(String(64), unique=True, nullable=False, index=True)
    plate_number = Column(String(32), nullable=False, index=True)
    camera_id = Column(String(64), nullable=False, index=True)
    location_name = Column(String(256), nullable=True)
    timestamp = Column(String(64), nullable=False, index=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    geom = Column(SafePointGeometry, nullable=True)
    vehicle_model = Column(String(128), nullable=True)
    speed_kmh = Column(Float, nullable=True)
    registered_owner = Column(String(256), nullable=True)
    owner_phone = Column(String(64), nullable=True)
    created_at = Column(String(64), default=utc_now_iso, nullable=False)

# ── 11. BANKING TRANSACTIONS ──
class BankingRecord(Base):
    __tablename__ = "banking_records"

    id = Column(String(64), primary_key=True)
    txn_id = Column(String(64), unique=True, nullable=False, index=True)
    from_account = Column(String(64), nullable=False, index=True)
    from_name = Column(String(256), nullable=True)
    to_account = Column(String(64), nullable=False, index=True)
    to_name = Column(String(256), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(16), default="INR", nullable=False)
    timestamp = Column(String(64), nullable=False, index=True)
    bank_name = Column(String(128), nullable=True)
    txn_type = Column(String(64), default="NEFT", nullable=False)
    narration = Column(Text, nullable=True)
    linked_phone = Column(String(64), nullable=True)
    created_at = Column(String(64), default=utc_now_iso, nullable=False)

# ── 12. DIGITAL WALLET & USDT HAWALA TRANSACTIONS ──
class WalletRecord(Base):
    __tablename__ = "wallet_records"

    id = Column(String(64), primary_key=True)
    wallet_id = Column(String(64), unique=True, nullable=False, index=True)
    sender_wallet = Column(String(128), nullable=False, index=True)
    receiver_wallet = Column(String(128), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(16), default="USDT", nullable=False)
    platform = Column(String(64), default="TRON_TRC20", nullable=False)
    timestamp = Column(String(64), nullable=False, index=True)
    sender_phone = Column(String(64), nullable=True)
    created_at = Column(String(64), default=utc_now_iso, nullable=False)

# ── 13. POLICE FIRST INFORMATION REPORTS (FIR) ──
class FIRRecord(Base):
    __tablename__ = "fir_records"

    id = Column(String(64), primary_key=True)
    fir_no = Column(String(64), unique=True, nullable=False, index=True)
    police_station = Column(String(256), nullable=False)
    date = Column(String(32), nullable=False)
    ipc_sections = Column(String(256), nullable=True)
    complainant = Column(String(256), nullable=True)
    accused_name = Column(String(256), nullable=True, index=True)
    accused_role = Column(String(128), nullable=True)
    suspect_phone = Column(String(64), nullable=True)
    suspect_vehicle = Column(String(32), nullable=True)
    suspect_account = Column(String(64), nullable=True)
    incident_type = Column(String(128), nullable=True)
    summary = Column(Text, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    geom = Column(SafePointGeometry, nullable=True)
    created_at = Column(String(64), default=utc_now_iso, nullable=False)

# ── 14. GRAPH ENTITIES (PERSISTENCE & NEO4J PROJECTION) ──
class GraphEntity(Base):
    __tablename__ = "graph_entities"

    id = Column(String(64), primary_key=True)
    name = Column(String(256), unique=True, nullable=False, index=True)
    type = Column(String(64), nullable=False, index=True)
    tier = Column(String(64), default="general", nullable=False)
    category = Column(String(64), default="general", nullable=False)
    risk_score = Column(Float, default=50.0, nullable=False)
    city = Column(String(128), nullable=True)
    phone = Column(String(64), nullable=True)
    dossier = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)

# ── 15. GRAPH RELATIONSHIPS (PERSISTENCE & NEO4J PROJECTION) ──
class GraphRelationship(Base):
    __tablename__ = "graph_relationships"

    id = Column(String(64), primary_key=True)
    source = Column(String(256), nullable=False, index=True)
    target = Column(String(256), nullable=False, index=True)
    label = Column(String(128), nullable=False, index=True)
    type = Column(String(64), default="DIRECT_LINK", nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    weight = Column(Float, default=1.0, nullable=False)
    metadata_json = Column(Text, nullable=True)

# ── 16. ANOMALY ALERTS ──
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_id = Column(String(64), nullable=False, index=True)
    entity_name = Column(String(256), nullable=False, index=True)
    anomaly_type = Column(String(128), nullable=False)
    anomaly_score = Column(Float, nullable=False)
    severity = Column(String(32), nullable=False)
    algorithm = Column(String(128), nullable=False)
    confidence_level = Column(String(64), nullable=False)
    status = Column(String(64), default="PENDING_REVIEW", nullable=False)
    feature_breakdown_json = Column(Text, nullable=True)
    plain_english_explanation = Column(Text, nullable=True)
    created_at = Column(String(64), default=utc_now_iso, nullable=False)

    case = relationship("Case", back_populates="alerts")
    review = relationship("AlertReview", back_populates="alert", uselist=False, cascade="all, delete-orphan")

# ── 17. ALERT REVIEWS & HUMAN SUPERVISORY ADJUDICATIONS ──
class AlertReview(Base):
    __tablename__ = "alert_reviews"

    alert_id = Column(String(64), ForeignKey("alerts.id", ondelete="CASCADE"), primary_key=True)
    decision = Column(String(64), nullable=False)
    investigator_id = Column(String(64), nullable=False)
    note = Column(Text, nullable=True)
    supervisor_status = Column(String(64), default="NOT_ESCALATED", nullable=False)
    supervisor_comments = Column(Text, nullable=True)
    reviewed_at = Column(String(64), default=utc_now_iso, nullable=False)
    updated_at = Column(String(64), default=utc_now_iso, nullable=True)

    alert = relationship("Alert", back_populates="review")

# ── 18. TAMPER-EVIDENT MERKLE AUDIT CHAIN ──
class AuditChainBlock(Base):
    __tablename__ = "audit_chain"

    event_id = Column(String(64), primary_key=True)
    timestamp = Column(String(64), nullable=False, index=True)
    actor_id = Column(String(64), nullable=False)
    role = Column(String(64), nullable=False)
    action = Column(String(128), nullable=False)
    resource = Column(String(256), nullable=False)
    ip_address = Column(String(64), nullable=True)
    correlation_id = Column(String(128), nullable=True)
    event_payload_json = Column(Text, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False, index=True)

# ── 19. PHYSICAL / INTRUDER SECURITY EVENT LOGS ──
class IntruderLog(Base):
    __tablename__ = "intruder_logs"

    id = Column(String(64), primary_key=True)
    timestamp = Column(String(64), nullable=False)
    ip = Column(String(64), nullable=True)
    device = Column(String(256), nullable=True)
    action = Column(String(128), nullable=False)
    status = Column(String(64), nullable=False)
    badge = Column(String(128), nullable=True)
    photo = Column(Text, nullable=True)
    epoch = Column(Float, nullable=False, index=True)

# ── 20. CONVERSATIONS & COPILOT CHAT MESSAGES ──
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(64), nullable=False)
    title = Column(String(256), nullable=False)
    created_at = Column(String(64), default=utc_now_iso, nullable=False)
    updated_at = Column(String(64), default=utc_now_iso, nullable=False)

    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(64), primary_key=True)
    conversation_id = Column(String(64), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(String(64), nullable=False)
    user_id = Column(String(64), nullable=False)
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    intent = Column(String(64), nullable=True)
    citations = Column(Text, nullable=True)
    tool_calls = Column(Text, nullable=True)
    timestamp = Column(String(64), default=utc_now_iso, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

# ── 21. NOTIFICATIONS ──
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False, index=True)
    case_id = Column(String(64), nullable=True)
    title = Column(String(256), nullable=False)
    details = Column(Text, nullable=False)
    severity = Column(String(32), default="info", nullable=False)
    is_read = Column(Integer, default=0, nullable=False)
    timestamp = Column(String(64), default=utc_now_iso, nullable=False)

# ── 22. SYSTEM SETTINGS ──
class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(128), primary_key=True)
    value = Column(Text, nullable=False)
