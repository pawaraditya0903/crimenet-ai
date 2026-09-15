"""
CrimeNet AI - Database Core Module
Supports PostgreSQL + PostGIS (Production / Enterprise) and SQLite (Local / Fallback)
"""
from backend.app.database.base import Base
from backend.app.database.connection import (
    engine,
    SessionLocal,
    get_db_session,
    get_engine,
    init_relational_schema,
    check_database_connection
)

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db_session",
    "get_engine",
    "init_relational_schema",
    "check_database_connection"
]
