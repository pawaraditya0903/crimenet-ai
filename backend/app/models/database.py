import sqlite3
import os
import json
import logging
from contextlib import contextmanager
from typing import Generator
from backend.app.config import DATABASE_PATH

logger = logging.getLogger("crimenet.db")

def get_connection(db_path: str = DATABASE_PATH) -> sqlite3.Connection:
    """Returns an optimized SQLite connection with foreign keys and WAL mode enabled."""
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    return conn

@contextmanager
def get_db(db_path: str = DATABASE_PATH) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for SQLite operations with automatic commit and rollback."""
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction error: {e}")
        raise
    finally:
        conn.close()

def init_db(db_path: str = DATABASE_PATH):
    """Initializes the relational SQLite schema and indexes."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    with get_db(db_path) as conn:
        cursor = conn.cursor()

        # 1. Users Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL,
            badge TEXT,
            failed_attempts INTEGER DEFAULT 0,
            lockout_until REAL DEFAULT 0,
            created_at TEXT NOT NULL
        );''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);')

        # 2. Refresh Tokens Table (Rotation & Revocation)
        cursor.execute('''CREATE TABLE IF NOT EXISTS refresh_tokens (
            token_hash TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            expires_at REAL NOT NULL,
            revoked INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id);')

        # 3. Investigation Cases Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            stage TEXT NOT NULL DEFAULT 'evidence',
            priority TEXT NOT NULL DEFAULT 'high',
            lead_investigator_id TEXT,
            squad TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );''')
        # Migrate columns if existing legacy table
        cursor.execute("PRAGMA table_info(cases)")
        case_cols = [r[1] for r in cursor.fetchall()]
        if "lead_investigator_id" not in case_cols:
            cursor.execute("ALTER TABLE cases ADD COLUMN lead_investigator_id TEXT")
        if "updated_at" not in case_cols:
            cursor.execute("ALTER TABLE cases ADD COLUMN updated_at TEXT DEFAULT (datetime('now'))")

        # 4. Case Assignments (RBAC & IDOR Prevention)
        cursor.execute('''CREATE TABLE IF NOT EXISTS case_assignments (
            case_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            assigned_at TEXT NOT NULL,
            PRIMARY KEY (case_id, user_id),
            FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );''')

        # 5. Suspects Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS suspects (
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            name TEXT NOT NULL,
            aliases TEXT,
            risk_score REAL DEFAULT 50.0,
            role TEXT,
            city TEXT,
            phone TEXT,
            dossier TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
        );''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_suspects_case ON suspects(case_id);')

        # 6. Evidence Items Table (Chain of Custody)
        cursor.execute('''CREATE TABLE IF NOT EXISTS evidence_items (
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            source_type TEXT NOT NULL,
            filename TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            collector_id TEXT NOT NULL,
            ingested_at TEXT NOT NULL,
            sha256_hash TEXT NOT NULL,
            classification TEXT NOT NULL DEFAULT 'RESTRICTED_SYNTHETIC_DEMO',
            integrity_status TEXT NOT NULL DEFAULT 'VERIFIED_INTACT',
            FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
        );''')
        cursor.execute("PRAGMA table_info(evidence_items)")
        ev_cols = [r[1] for r in cursor.fetchall()]
        if "mime_type" not in ev_cols:
            cursor.execute("ALTER TABLE evidence_items ADD COLUMN mime_type TEXT DEFAULT 'application/octet-stream'")
        if "file_size" not in ev_cols:
            cursor.execute("ALTER TABLE evidence_items ADD COLUMN file_size INTEGER DEFAULT 0")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_evidence_case ON evidence_items(case_id);')

        # 7. Graph Entities Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS graph_entities (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            tier TEXT NOT NULL DEFAULT 'general',
            category TEXT NOT NULL DEFAULT 'general',
            risk_score REAL DEFAULT 50.0,
            city TEXT,
            phone TEXT,
            dossier TEXT,
            metadata_json TEXT
        );''')

        # 8. Graph Relationships Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS graph_relationships (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            target TEXT NOT NULL,
            label TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'DIRECT_LINK',
            confidence REAL DEFAULT 1.0,
            weight REAL DEFAULT 1.0,
            metadata_json TEXT
        );''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rel_src ON graph_relationships(source);')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rel_tgt ON graph_relationships(target);')

        # 9. Anomaly Alerts Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            entity_name TEXT NOT NULL,
            anomaly_type TEXT NOT NULL,
            anomaly_score REAL NOT NULL,
            severity TEXT NOT NULL,
            algorithm TEXT NOT NULL,
            confidence_level TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING_REVIEW',
            feature_breakdown_json TEXT,
            plain_english_explanation TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
        );''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_case ON alerts(case_id);')

        # 10. Alert Human Reviews & Supervisor Escalations
        cursor.execute('''CREATE TABLE IF NOT EXISTS alert_reviews (
            alert_id TEXT PRIMARY KEY,
            decision TEXT NOT NULL,
            investigator_id TEXT NOT NULL,
            note TEXT,
            supervisor_status TEXT DEFAULT 'NOT_ESCALATED',
            supervisor_comments TEXT,
            reviewed_at TEXT NOT NULL,
            FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE
        );''')
        cursor.execute("PRAGMA table_info(alert_reviews)")
        ar_cols = [r[1] for r in cursor.fetchall()]
        if "reviewed_at" not in ar_cols:
            cursor.execute("ALTER TABLE alert_reviews ADD COLUMN reviewed_at TEXT DEFAULT (datetime('now'))")

        # 11. Hash-Linked Tamper-Evident Audit Chain
        cursor.execute('''CREATE TABLE IF NOT EXISTS audit_chain (
            event_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            actor_id TEXT NOT NULL,
            role TEXT NOT NULL,
            action TEXT NOT NULL,
            resource TEXT NOT NULL,
            ip_address TEXT,
            correlation_id TEXT,
            event_payload_json TEXT NOT NULL,
            previous_hash TEXT NOT NULL,
            current_hash TEXT NOT NULL
        );''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_chain(timestamp);')

        # 12. Conversations & Copilot Chat
        cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
        );''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            case_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            intent TEXT,
            citations_json TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        );''')

        # 13. System Notifications Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            case_id TEXT,
            title TEXT NOT NULL,
            details TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'info',
            is_read INTEGER DEFAULT 0,
            timestamp TEXT NOT NULL
        );''')

        # 14. Intruder / Security Event Logs
        cursor.execute('''CREATE TABLE IF NOT EXISTS intruder_logs (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            ip TEXT,
            device TEXT,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            badge TEXT,
            photo TEXT,
            epoch REAL NOT NULL
        );''')

        # 15. System Settings Key-Value Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );''')

    logger.info("Relational database schema verified and initialized.")
