"""Initial PostgreSQL + PostGIS Schema Migration for CrimeNet AI

Revision ID: 2026_09_15_0001
Revises: 
Create Date: 2026-09-15 03:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '2026_09_15_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Enable PostGIS Extension if running on PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # 2. Users Table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('username', sa.String(length=128), unique=True, nullable=False),
        sa.Column('email', sa.String(length=256), unique=True, nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('salt', sa.String(length=128), nullable=False),
        sa.Column('role', sa.String(length=64), nullable=False),
        sa.Column('badge', sa.String(length=256), nullable=True),
        sa.Column('failed_attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('lockout_until', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('created_at', sa.String(length=64), nullable=False)
    )
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_email', 'users', ['email'])

    # 3. Refresh Tokens Table
    op.create_table(
        'refresh_tokens',
        sa.Column('token_hash', sa.String(length=128), primary_key=True),
        sa.Column('user_id', sa.String(length=64), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expires_at', sa.Float(), nullable=False),
        sa.Column('revoked', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.String(length=64), nullable=False)
    )
    op.create_index('idx_refresh_tokens_user', 'refresh_tokens', ['user_id'])

    # 4. Investigation Cases Table
    op.create_table(
        'cases',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('stage', sa.String(length=64), server_default='evidence', nullable=False),
        sa.Column('priority', sa.String(length=32), server_default='high', nullable=False),
        sa.Column('lead_investigator_id', sa.String(length=64), nullable=True),
        sa.Column('squad', sa.String(length=128), nullable=False),
        sa.Column('suspects', sa.Text(), nullable=True),
        sa.Column('created_at', sa.String(length=64), nullable=False),
        sa.Column('updated_at', sa.String(length=64), nullable=False)
    )

    # 5. Case Assignments Table
    op.create_table(
        'case_assignments',
        sa.Column('case_id', sa.String(length=64), sa.ForeignKey('cases.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('user_id', sa.String(length=64), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('assigned_at', sa.String(length=64), nullable=False)
    )

    # 6. Suspects Table
    op.create_table(
        'suspects',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('case_id', sa.String(length=64), sa.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('aliases', sa.Text(), nullable=True),
        sa.Column('risk_score', sa.Float(), server_default='50.0', nullable=False),
        sa.Column('role', sa.String(length=128), nullable=True),
        sa.Column('city', sa.String(length=128), nullable=True),
        sa.Column('phone', sa.String(length=64), nullable=True),
        sa.Column('dossier', sa.Text(), nullable=True),
        sa.Column('created_at', sa.String(length=64), nullable=False)
    )
    op.create_index('idx_suspects_case', 'suspects', ['case_id'])

    # 7. Evidence Items Table (with S3 object key and SHA-256 integrity metadata)
    op.create_table(
        'evidence_items',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('case_id', sa.String(length=64), sa.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_type', sa.String(length=64), nullable=False),
        sa.Column('filename', sa.String(length=256), nullable=False),
        sa.Column('mime_type', sa.String(length=128), server_default='application/octet-stream', nullable=False),
        sa.Column('file_size', sa.Integer(), server_default='0', nullable=False),
        sa.Column('collector_id', sa.String(length=64), nullable=False),
        sa.Column('ingested_at', sa.String(length=64), nullable=False),
        sa.Column('sha256_hash', sa.String(length=64), nullable=False),
        sa.Column('classification', sa.String(length=64), server_default='RESTRICTED_SYNTHETIC_DEMO', nullable=False),
        sa.Column('integrity_status', sa.String(length=64), server_default='VERIFIED_INTACT', nullable=False),
        sa.Column('object_key', sa.String(length=512), nullable=True),
        sa.Column('storage_provider', sa.String(length=32), server_default='minio', nullable=False),
        sa.Column('storage_metadata_json', sa.Text(), nullable=True)
    )
    op.create_index('idx_evidence_case', 'evidence_items', ['case_id'])
    op.create_index('idx_evidence_hash', 'evidence_items', ['sha256_hash'])

    # 8. Cell Towers Table
    op.create_table(
        'cell_towers',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('tower_id', sa.String(length=64), unique=True, nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('city', sa.String(length=128), nullable=True),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lng', sa.Float(), nullable=False),
        sa.Column('coverage_radius_meters', sa.Float(), server_default='1500.0', nullable=False),
        sa.Column('created_at', sa.String(length=64), nullable=False)
    )

    # 9. Telecom CDR Records Table
    op.create_table(
        'cdr_records',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('call_id', sa.String(length=64), unique=True, nullable=False),
        sa.Column('caller', sa.String(length=64), nullable=False),
        sa.Column('receiver', sa.String(length=64), nullable=False),
        sa.Column('timestamp', sa.String(length=64), nullable=False),
        sa.Column('duration_sec', sa.Integer(), server_default='0', nullable=False),
        sa.Column('tower_id', sa.String(length=64), nullable=True),
        sa.Column('tower_name', sa.String(length=256), nullable=True),
        sa.Column('imei', sa.String(length=32), nullable=True),
        sa.Column('imsi', sa.String(length=32), nullable=True),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lng', sa.Float(), nullable=True),
        sa.Column('call_type', sa.String(length=64), server_default='OUTBOUND_VOICE', nullable=False),
        sa.Column('created_at', sa.String(length=64), nullable=False)
    )
    op.create_index('idx_cdr_caller', 'cdr_records', ['caller'])
    op.create_index('idx_cdr_receiver', 'cdr_records', ['receiver'])
    op.create_index('idx_cdr_timestamp', 'cdr_records', ['timestamp'])

    # 10. ANPR Cameras Table
    op.create_table(
        'anpr_cameras',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('camera_id', sa.String(length=64), unique=True, nullable=False),
        sa.Column('location_name', sa.String(length=256), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lng', sa.Float(), nullable=False),
        sa.Column('created_at', sa.String(length=64), nullable=False)
    )

    # 11. ANPR Records Table
    op.create_table(
        'anpr_records',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('detection_id', sa.String(length=64), unique=True, nullable=False),
        sa.Column('plate_number', sa.String(length=32), nullable=False),
        sa.Column('camera_id', sa.String(length=64), nullable=False),
        sa.Column('location_name', sa.String(length=256), nullable=True),
        sa.Column('timestamp', sa.String(length=64), nullable=False),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lng', sa.Float(), nullable=True),
        sa.Column('vehicle_model', sa.String(length=128), nullable=True),
        sa.Column('speed_kmh', sa.Float(), nullable=True),
        sa.Column('registered_owner', sa.String(length=256), nullable=True),
        sa.Column('owner_phone', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.String(length=64), nullable=False)
    )
    op.create_index('idx_anpr_plate', 'anpr_records', ['plate_number'])
    op.create_index('idx_anpr_timestamp', 'anpr_records', ['timestamp'])

    # 12. Banking Records Table
    op.create_table(
        'banking_records',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('txn_id', sa.String(length=64), unique=True, nullable=False),
        sa.Column('from_account', sa.String(length=64), nullable=False),
        sa.Column('from_name', sa.String(length=256), nullable=True),
        sa.Column('to_account', sa.String(length=64), nullable=False),
        sa.Column('to_name', sa.String(length=256), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=16), server_default='INR', nullable=False),
        sa.Column('timestamp', sa.String(length=64), nullable=False),
        sa.Column('bank_name', sa.String(length=128), nullable=True),
        sa.Column('txn_type', sa.String(length=64), server_default='NEFT', nullable=False),
        sa.Column('narration', sa.Text(), nullable=True),
        sa.Column('linked_phone', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.String(length=64), nullable=False)
    )
    op.create_index('idx_bank_from', 'banking_records', ['from_account'])
    op.create_index('idx_bank_to', 'banking_records', ['to_account'])

    # 13. Digital Wallet Records Table
    op.create_table(
        'wallet_records',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('wallet_id', sa.String(length=64), unique=True, nullable=False),
        sa.Column('sender_wallet', sa.String(length=128), nullable=False),
        sa.Column('receiver_wallet', sa.String(length=128), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=16), server_default='USDT', nullable=False),
        sa.Column('platform', sa.String(length=64), server_default='TRON_TRC20', nullable=False),
        sa.Column('timestamp', sa.String(length=64), nullable=False),
        sa.Column('sender_phone', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.String(length=64), nullable=False)
    )

    # 14. Police FIR Records Table
    op.create_table(
        'fir_records',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('fir_no', sa.String(length=64), unique=True, nullable=False),
        sa.Column('police_station', sa.String(length=256), nullable=False),
        sa.Column('date', sa.String(length=32), nullable=False),
        sa.Column('ipc_sections', sa.String(length=256), nullable=True),
        sa.Column('complainant', sa.String(length=256), nullable=True),
        sa.Column('accused_name', sa.String(length=256), nullable=True),
        sa.Column('accused_role', sa.String(length=128), nullable=True),
        sa.Column('suspect_phone', sa.String(length=64), nullable=True),
        sa.Column('suspect_vehicle', sa.String(length=32), nullable=True),
        sa.Column('suspect_account', sa.String(length=64), nullable=True),
        sa.Column('incident_type', sa.String(length=128), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lng', sa.Float(), nullable=True),
        sa.Column('created_at', sa.String(length=64), nullable=False)
    )

    # 15. Graph Entities Table
    op.create_table(
        'graph_entities',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('name', sa.String(length=256), unique=True, nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('tier', sa.String(length=64), server_default='general', nullable=False),
        sa.Column('category', sa.String(length=64), server_default='general', nullable=False),
        sa.Column('risk_score', sa.Float(), server_default='50.0', nullable=False),
        sa.Column('city', sa.String(length=128), nullable=True),
        sa.Column('phone', sa.String(length=64), nullable=True),
        sa.Column('dossier', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True)
    )
    op.create_index('idx_graph_entities_name', 'graph_entities', ['name'])

    # 16. Graph Relationships Table
    op.create_table(
        'graph_relationships',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('source', sa.String(length=256), nullable=False),
        sa.Column('target', sa.String(length=256), nullable=False),
        sa.Column('label', sa.String(length=128), nullable=False),
        sa.Column('type', sa.String(length=64), server_default='DIRECT_LINK', nullable=False),
        sa.Column('confidence', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('weight', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=True)
    )
    op.create_index('idx_rel_src', 'graph_relationships', ['source'])
    op.create_index('idx_rel_tgt', 'graph_relationships', ['target'])

    # 17. Anomaly Alerts Table
    op.create_table(
        'alerts',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('case_id', sa.String(length=64), sa.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_id', sa.String(length=64), nullable=False),
        sa.Column('entity_name', sa.String(length=256), nullable=False),
        sa.Column('anomaly_type', sa.String(length=128), nullable=False),
        sa.Column('anomaly_score', sa.Float(), nullable=False),
        sa.Column('severity', sa.String(length=32), nullable=False),
        sa.Column('algorithm', sa.String(length=128), nullable=False),
        sa.Column('confidence_level', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=64), server_default='PENDING_REVIEW', nullable=False),
        sa.Column('feature_breakdown_json', sa.Text(), nullable=True),
        sa.Column('plain_english_explanation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.String(length=64), nullable=False)
    )
    op.create_index('idx_alerts_case', 'alerts', ['case_id'])

    # 18. Alert Reviews Table
    op.create_table(
        'alert_reviews',
        sa.Column('alert_id', sa.String(length=64), sa.ForeignKey('alerts.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('decision', sa.String(length=64), nullable=False),
        sa.Column('investigator_id', sa.String(length=64), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('supervisor_status', sa.String(length=64), server_default='NOT_ESCALATED', nullable=False),
        sa.Column('supervisor_comments', sa.Text(), nullable=True),
        sa.Column('reviewed_at', sa.String(length=64), nullable=False),
        sa.Column('updated_at', sa.String(length=64), nullable=True)
    )

    # 19. Audit Chain Table
    op.create_table(
        'audit_chain',
        sa.Column('event_id', sa.String(length=64), primary_key=True),
        sa.Column('timestamp', sa.String(length=64), nullable=False),
        sa.Column('actor_id', sa.String(length=64), nullable=False),
        sa.Column('role', sa.String(length=64), nullable=False),
        sa.Column('action', sa.String(length=128), nullable=False),
        sa.Column('resource', sa.String(length=256), nullable=False),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('correlation_id', sa.String(length=128), nullable=True),
        sa.Column('event_payload_json', sa.Text(), nullable=False),
        sa.Column('previous_hash', sa.String(length=64), nullable=False),
        sa.Column('current_hash', sa.String(length=64), nullable=False)
    )
    op.create_index('idx_audit_time', 'audit_chain', ['timestamp'])
    op.create_index('idx_audit_current_hash', 'audit_chain', ['current_hash'])

    # 20. Intruder Logs Table
    op.create_table(
        'intruder_logs',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('timestamp', sa.String(length=64), nullable=False),
        sa.Column('ip', sa.String(length=64), nullable=True),
        sa.Column('device', sa.String(length=256), nullable=True),
        sa.Column('action', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('badge', sa.String(length=128), nullable=True),
        sa.Column('photo', sa.Text(), nullable=True),
        sa.Column('epoch', sa.Float(), nullable=False)
    )

    # 21. Conversations & Chat Messages Tables
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('case_id', sa.String(length=64), sa.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('created_at', sa.String(length=64), nullable=False),
        sa.Column('updated_at', sa.String(length=64), nullable=False)
    )

    op.create_table(
        'chat_messages',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('conversation_id', sa.String(length=64), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('case_id', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('intent', sa.String(length=64), nullable=True),
        sa.Column('citations', sa.Text(), nullable=True),
        sa.Column('tool_calls', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.String(length=64), nullable=False)
    )

    # 22. Notifications & System Settings Tables
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('case_id', sa.String(length=64), nullable=True),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('details', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=32), server_default='info', nullable=False),
        sa.Column('is_read', sa.Integer(), server_default='0', nullable=False),
        sa.Column('timestamp', sa.String(length=64), nullable=False)
    )

    op.create_table(
        'system_settings',
        sa.Column('key', sa.String(length=128), primary_key=True),
        sa.Column('value', sa.Text(), nullable=False)
    )

    # Add PostGIS geometry columns if PostgreSQL dialect
    if bind.dialect.name == "postgresql":
        op.execute("SELECT AddGeometryColumn('cell_towers', 'geom', 4326, 'POINT', 2);")
        op.execute("SELECT AddGeometryColumn('cdr_records', 'geom', 4326, 'POINT', 2);")
        op.execute("SELECT AddGeometryColumn('anpr_cameras', 'geom', 4326, 'POINT', 2);")
        op.execute("SELECT AddGeometryColumn('anpr_records', 'geom', 4326, 'POINT', 2);")
        op.execute("SELECT AddGeometryColumn('fir_records', 'geom', 4326, 'POINT', 2);")

        op.execute("CREATE INDEX IF NOT EXISTS idx_cell_towers_geom ON cell_towers USING GIST (geom);")
        op.execute("CREATE INDEX IF NOT EXISTS idx_cdr_records_geom ON cdr_records USING GIST (geom);")
        op.execute("CREATE INDEX IF NOT EXISTS idx_anpr_records_geom ON anpr_records USING GIST (geom);")

def downgrade() -> None:
    tables = [
        'system_settings', 'notifications', 'chat_messages', 'conversations',
        'intruder_logs', 'audit_chain', 'alert_reviews', 'alerts',
        'graph_relationships', 'graph_entities', 'fir_records', 'wallet_records',
        'banking_records', 'anpr_records', 'anpr_cameras', 'cdr_records',
        'cell_towers', 'evidence_items', 'suspects', 'case_assignments',
        'cases', 'refresh_tokens', 'users'
    ]
    for table in tables:
        op.drop_table(table)
