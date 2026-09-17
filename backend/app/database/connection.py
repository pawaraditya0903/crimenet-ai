import os
import logging
from typing import Generator, Optional, Dict, Any
from contextlib import contextmanager

from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool, StaticPool

from backend.app.config import (
    DATABASE_URL,
    DATABASE_PATH,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB
)
from backend.app.database.base import Base

logger = logging.getLogger("crimenet.database.connection")

_engine: Optional[Engine] = None
_SessionFactory: Optional[sessionmaker] = None
_DIALECT: str = "sqlite"

def resolve_database_url() -> str:
    """Resolves the database URL prioritizing explicit DATABASE_URL env var,
    attempting PostgreSQL if configured, or falling back to SQLite in dev mode only.

    SEC-017 FIX: In production/enterprise mode, fails fast if PostgreSQL is unavailable.
    SQLite fallback is only permitted when CRIMENET_ENV=development.
    """
    from backend.app.config import IS_PRODUCTION
    global _DIALECT
    explicit_url = DATABASE_URL.strip() if DATABASE_URL else ""
    if explicit_url:
        if "postgres" in explicit_url:
            _DIALECT = "postgresql"
        elif "sqlite" in explicit_url:
            if IS_PRODUCTION:
                logger.critical("FATAL: SQLite database URL detected in production mode. PostgreSQL is required.")
                raise RuntimeError("FATAL: SQLite is not permitted as the database backend in production mode.")
            _DIALECT = "sqlite"
        else:
            _DIALECT = "sqlite"
        return explicit_url

    # Check if PostgreSQL environment indicates intention to use PostgreSQL
    if POSTGRES_USER and POSTGRES_PASSWORD:
        pg_url = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

        # Quick connectivity probe to PostgreSQL
        try:
            temp_engine = create_engine(pg_url, connect_args={"connect_timeout": 2}, pool_pre_ping=True)
            with temp_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to primary PostgreSQL instance at %s:%s/%s", POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB)
            _DIALECT = "postgresql"
            return pg_url
        except Exception as e:
            if IS_PRODUCTION:
                logger.critical(
                    "FATAL: PostgreSQL unreachable at %s:%s in production mode. "
                    "SQLite fallback is prohibited. Startup aborted. Error: %s",
                    POSTGRES_HOST, POSTGRES_PORT, type(e).__name__
                )
                raise RuntimeError(
                    f"FATAL: PostgreSQL is required in production mode but is unreachable at {POSTGRES_HOST}:{POSTGRES_PORT}."
                )
            logger.warning(
                "PostgreSQL unreachable at %s:%s (%s). "
                "Falling back to SQLite at %s (development mode only).",
                POSTGRES_HOST, POSTGRES_PORT, type(e).__name__, DATABASE_PATH
            )

    if IS_PRODUCTION:
        logger.critical("FATAL: PostgreSQL credentials not configured in production mode. Startup aborted.")
        raise RuntimeError("FATAL: POSTGRES_USER and POSTGRES_PASSWORD must be set in production mode.")

    # Development fallback only
    _DIALECT = "sqlite"
    os.makedirs(os.path.dirname(os.path.abspath(DATABASE_PATH)), exist_ok=True)
    return f"sqlite:///{os.path.abspath(DATABASE_PATH)}"


def get_engine() -> Engine:
    """Returns singleton SQLAlchemy Engine with configured connection pooling."""
    global _engine
    if _engine is None:
        db_url = resolve_database_url()
        if "postgresql" in db_url:
            _engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_pre_ping=True,
                echo=False
            )
        else:
            # SQLite setup with foreign keys and WAL mode
            _engine = create_engine(
                db_url,
                connect_args={"check_same_thread": False, "timeout": 15},
                pool_pre_ping=True,
                echo=False
            )

            @event.listens_for(_engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()

        logger.info("Initialized database engine with dialect: %s", _DIALECT)
    return _engine

def get_session_factory() -> sessionmaker:
    """Returns singleton sessionmaker bound to active engine."""
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine()
        )
    return _SessionFactory

# Scoped session for thread-safe operations
SessionLocal = scoped_session(lambda: get_session_factory()())

def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency for obtaining a database session."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error("Database session transaction error: %s", e)
        raise
    finally:
        session.close()

@contextmanager
def db_session_context() -> Generator[Session, None, None]:
    """Context manager for standalone scripts and background tasks."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error("Database context transaction error: %s", e)
        raise
    finally:
        session.close()

def init_relational_schema():
    """Initializes schema, enables PostGIS extension (if PostgreSQL), and creates all tables."""
    engine = get_engine()
    with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                logger.info("PostGIS extension enabled on PostgreSQL.")
            except Exception as e:
                logger.warning("Could not enable PostGIS extension (may already exist or insufficient privileges): %s", e)
        
        # Import models so Base metadata is populated
        from backend.app.models import pg_models  # noqa
        Base.metadata.create_all(bind=conn)

        # In SQLite fallback mode, dynamically verify and add any missing columns in legacy tables
        if engine.dialect.name == "sqlite":
            try:
                res = conn.execute(text("PRAGMA table_info(evidence_items)"))
                cols = [r[1] for r in res.fetchall()]
                if cols:
                    if "object_key" not in cols:
                        conn.execute(text("ALTER TABLE evidence_items ADD COLUMN object_key TEXT"))
                    if "storage_provider" not in cols:
                        conn.execute(text("ALTER TABLE evidence_items ADD COLUMN storage_provider TEXT DEFAULT 's3'"))
                    if "storage_metadata_json" not in cols:
                        conn.execute(text("ALTER TABLE evidence_items ADD COLUMN storage_metadata_json TEXT"))
            except Exception as se:
                logger.warning("SQLite evidence_items column migration check: %s", se)

        logger.info("Relational schema verified and tables created.")

def check_database_connection() -> Dict[str, Any]:
    """Inspects database health, latency, active dialect, and PostGIS availability."""
    engine = get_engine()
    status: Dict[str, Any] = {
        "status": "HEALTHY",
        "dialect": engine.dialect.name,
        "is_postgresql": engine.dialect.name == "postgresql",
        "postgis_enabled": False,
        "table_count": 0
    }
    try:
        with engine.connect() as conn:
            # Latency ping
            conn.execute(text("SELECT 1"))
            
            # Check PostGIS
            if engine.dialect.name == "postgresql":
                try:
                    res = conn.execute(text("SELECT PostGIS_Version()")).scalar()
                    status["postgis_enabled"] = True
                    status["postgis_version"] = str(res)
                except Exception:
                    status["postgis_enabled"] = False

            # Inspect tables count
            if engine.dialect.name == "postgresql":
                table_cnt = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")).scalar()
            else:
                table_cnt = conn.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")).scalar()
            status["table_count"] = int(table_cnt or 0)
    except Exception as e:
        status["status"] = "DEGRADED"
        status["error"] = str(e)
        logger.error("Database health check failed: %s", e)
    status["is_healthy"] = (status["status"] == "HEALTHY")
    return status

check_database_health = check_database_connection

# Initialize module-level engine reference for convenience
engine = get_engine()
