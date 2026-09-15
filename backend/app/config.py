import os
import sys
import secrets
import logging
from typing import List
from dotenv import load_dotenv, find_dotenv

# Load environment variables
_env_path = find_dotenv()
if _env_path:
    load_dotenv(_env_path)
else:
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

logger = logging.getLogger("crimenet.config")

# Execution Environment
ENVIRONMENT = os.environ.get("CRIMENET_ENV", "development").strip().lower()
IS_PRODUCTION = ENVIRONMENT == "production"

# Base Paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(APP_DIR)
WORKSPACE_ROOT = os.path.dirname(BACKEND_DIR)

# Database Configuration (PostgreSQL / SQLite Dual-Engine)
DATABASE_PATH = os.environ.get("CRIMENET_DB_PATH", os.path.join(BACKEND_DIR, "crimenet.db"))
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.environ.get("POSTGRES_DB", "crimenet")

_default_pg_url = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Dedicated Graph Database (Neo4j) Configuration
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "crimenet_graph_pass")

# S3-Compatible Object Storage (MinIO / S3 / R2) Configuration
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL", os.environ.get("S3_ENDPOINT", "http://localhost:9000"))
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY", "minioadmin")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", os.environ.get("S3_BUCKET", "crimenet-evidence"))
S3_REGION = os.environ.get("S3_REGION", "us-east-1")
S3_USE_SSL = os.environ.get("S3_USE_SSL", "false").lower() in ("true", "1", "yes")

# Authentication & JWT Configuration
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "15")) * 60
REFRESH_TOKEN_EXPIRE_SECONDS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7")) * 86400
PBKDF2_ITERATIONS = int(os.environ.get("PBKDF2_ITERATIONS", "100000"))
MAX_LOGIN_ATTEMPTS = int(os.environ.get("MAX_LOGIN_ATTEMPTS", "5"))
LOCKOUT_DURATION_SECONDS = int(os.environ.get("LOCKOUT_DURATION_SECONDS", "900"))  # 15 minutes

# JWT Secret Resolution
_raw_jwt_secret = os.environ.get("CRIMENET_JWT_SECRET", "") or os.environ.get("JWT_SECRET_KEY", "")

# Predictable / insecure seeds that must NEVER be used in production
INSECURE_TEST_SEEDS = [
    "CRIMENET_DEFAULT_DEV_SECRET_KEY_REPLACE_IN_PRODUCTION",
    "secret",
    "changeme",
    "password"
]

if IS_PRODUCTION:
    if not _raw_jwt_secret or _raw_jwt_secret in INSECURE_TEST_SEEDS:
        logger.critical("FATAL: CRIMENET_JWT_SECRET must be set in production mode. Startup aborted.")
        raise RuntimeError("FATAL: Insecure or missing CRIMENET_JWT_SECRET in production mode.")
    JWT_SECRET_KEY = _raw_jwt_secret
else:
    if not _raw_jwt_secret:
        # Cryptographically secure random secret generated for the development session
        JWT_SECRET_KEY = secrets.token_hex(32)
        logger.warning("Development mode: ephemeral JWT_SECRET_KEY generated. Set CRIMENET_JWT_SECRET for persistence.")
    else:
        JWT_SECRET_KEY = _raw_jwt_secret

# PII Encryption Key Resolution (AES-256-GCM requires 32 bytes)
_raw_pii_key = os.environ.get("CRIMENET_PII_ENCRYPTION_KEY", "")

if IS_PRODUCTION:
    if not _raw_pii_key or len(_raw_pii_key) < 32:
        logger.critical("FATAL: CRIMENET_PII_ENCRYPTION_KEY (>= 32 bytes) must be set in production mode. Startup aborted.")
        raise RuntimeError("FATAL: Insecure or missing CRIMENET_PII_ENCRYPTION_KEY in production mode.")
    if len(_raw_pii_key) == 64:
        try:
            PII_KEY_BYTES = bytes.fromhex(_raw_pii_key)
        except ValueError:
            PII_KEY_BYTES = _raw_pii_key.encode("utf-8")[:32]
    else:
        PII_KEY_BYTES = _raw_pii_key.encode("utf-8")[:32]
else:
    if not _raw_pii_key:
        PII_KEY_BYTES = secrets.token_bytes(32)
        logger.warning("Development mode: ephemeral PII_KEY_BYTES generated. Set CRIMENET_PII_ENCRYPTION_KEY for persistence.")
    elif len(_raw_pii_key) == 64:
        try:
            PII_KEY_BYTES = bytes.fromhex(_raw_pii_key)
        except ValueError:
            PII_KEY_BYTES = _raw_pii_key.encode("utf-8")[:32]
    else:
        PII_KEY_BYTES = _raw_pii_key.encode("utf-8")[:32]

# CORS Allowed Origins
_cors_env = os.environ.get("CORS_ORIGINS", "")
if _cors_env:
    ALLOWED_ORIGINS: List[str] = [o.strip() for o in _cors_env.split(",") if o.strip()]
    if IS_PRODUCTION and "*" in ALLOWED_ORIGINS:
        logger.critical("FATAL: Wildcard CORS origin '*' is strictly prohibited in production mode.")
        raise RuntimeError("FATAL: Insecure CORS configuration in production mode.")
else:
    if IS_PRODUCTION:
        ALLOWED_ORIGINS = [
            "https://crimenet.ai",
            "https://crimenet-ai-two.vercel.app",
            "https://crimenet-ai.vercel.app"
        ]
    else:
        ALLOWED_ORIGINS = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            "https://crimenet-ai-two.vercel.app",
            "https://crimenet-ai.vercel.app"
        ]

# Maximum Request Body Size (10 MB)
MAX_REQUEST_SIZE_BYTES = 10 * 1024 * 1024
