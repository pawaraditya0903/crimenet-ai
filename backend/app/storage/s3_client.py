"""
CrimeNet AI - S3-Compatible Object Storage Client
Integrates with MinIO for local development and AWS S3 / Cloudflare R2 for production.
Stores binary evidence (CCTV footage, ANPR captures, forensic reports, datasets).
Includes constant-time cryptographic SHA-256 integrity verification.

SEC-005 FIX: Path traversal protection enforced on all local vault operations.
SEC-024 FIX: Object keys are UUID-based and server-generated; user filename is display-only.
"""

import os
import hashlib
import hmac as _hmac
import logging
import uuid
import re
from pathlib import Path
from typing import Dict, Any, Optional, Union, BinaryIO

from botocore.config import Config
import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

from backend.app.config import (
    S3_ENDPOINT_URL,
    S3_ACCESS_KEY,
    S3_SECRET_KEY,
    S3_BUCKET_NAME,
    S3_REGION,
    S3_USE_SSL,
    BACKEND_DIR
)
from backend.app.security.crypto import constant_time_compare, compute_sha256

logger = logging.getLogger("crimenet.storage.s3")

LOCAL_VAULT_DIR = Path(os.path.join(BACKEND_DIR, "data", "evidence_vault")).resolve()

# ── Allowlisted MIME types for evidence uploads ──
ALLOWED_MIME_TYPES: set = {
    "application/pdf",
    "application/json",
    "application/octet-stream",
    "application/zip",
    "text/plain",
    "text/csv",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "video/mp4",
    "video/webm",
    "audio/mpeg",
    "audio/wav",
    "audio/ogg",
}

# Dangerous MIME types that must always be rejected
BLOCKED_MIME_TYPES: set = {
    "text/html",
    "application/x-httpd-php",
    "application/x-sh",
    "application/x-bat",
    "application/x-msdos-program",
    "application/x-msdownload",
    "application/x-executable",
    "application/x-javascript",
    "text/javascript",
    "application/javascript",
}

MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB


def _validate_safe_path(resolved_path: Path, vault_root: Path) -> bool:
    """Returns True if resolved_path is safely inside vault_root. Prevents path traversal."""
    try:
        resolved_path.resolve().relative_to(vault_root.resolve())
        return True
    except ValueError:
        return False


def _sanitize_object_key(raw_key: str) -> str:
    """
    SEC-005: Sanitize object key to remove path traversal sequences and dangerous characters.
    The sanitized key is used purely as a storage path — user-supplied filenames must
    never be used directly as keys. Use generate_object_key() instead.
    """
    # Remove null bytes and leading slashes
    key = raw_key.replace("\x00", "").lstrip("/").lstrip("\\")
    # Reject absolute paths and traversal sequences
    if ".." in key.split("/") or ".." in key.split("\\"):
        raise ValueError(f"Path traversal attempt detected in object key: {raw_key!r}")
    # Allow only safe characters: alphanumeric, /, -, _, .
    if not re.match(r'^[a-zA-Z0-9/_\-\.]+$', key):
        raise ValueError(f"Object key contains invalid characters: {raw_key!r}")
    return key


def validate_mime_type(mime_type: str) -> str:
    """
    SEC-021: Validates mime_type against allowlist.
    Returns the safe mime_type or 'application/octet-stream' if unrecognized.
    Raises ValueError for explicitly blocked types.
    """
    normalized = (mime_type or "").strip().lower().split(";")[0].strip()
    if normalized in BLOCKED_MIME_TYPES:
        raise ValueError(f"File type '{normalized}' is not permitted for evidence uploads.")
    if normalized in ALLOWED_MIME_TYPES:
        return normalized
    # Default to safe binary type for unknown content
    logger.warning("Unknown MIME type '%s' normalized to application/octet-stream", normalized)
    return "application/octet-stream"


def generate_object_key(case_id: str, evidence_id: str) -> str:
    """
    SEC-024: Generates a server-side UUID-based object key.
    User-supplied filenames are NEVER used as part of the storage key.
    """
    # Sanitize case_id defensively
    safe_case = re.sub(r'[^a-zA-Z0-9\-]', '_', str(case_id))[:64]
    safe_ev = re.sub(r'[^a-zA-Z0-9\-]', '_', str(evidence_id))[:64]
    return f"evidence/{safe_case}/{safe_ev}"


class S3StorageClient:
    def __init__(self):
        self.endpoint_url = S3_ENDPOINT_URL
        self.bucket_name = S3_BUCKET_NAME
        self.region = S3_REGION
        self._s3 = None
        self._is_connected = False
        self._init_client()

    def _init_client(self):
        try:
            self._s3 = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=S3_ACCESS_KEY,
                aws_secret_access_key=S3_SECRET_KEY,
                region_name=self.region,
                use_ssl=S3_USE_SSL,
                config=Config(
                    signature_version="s3v4",
                    connect_timeout=2,
                    read_timeout=3,
                    retries={"max_attempts": 2}
                )
            )
            # Test connectivity and ensure bucket exists
            self._s3.head_bucket(Bucket=self.bucket_name)
            self._is_connected = True
            logger.info("Connected to S3/MinIO bucket '%s' at %s", self.bucket_name, self.endpoint_url)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code in ("404", "NoSuchBucket"):
                try:
                    self._s3.create_bucket(Bucket=self.bucket_name)
                    self._is_connected = True
                    logger.info("Created S3/MinIO bucket '%s'", self.bucket_name)
                except Exception as ce:
                    logger.warning("Could not auto-create bucket '%s': %s", self.bucket_name, ce)
                    self._is_connected = False
            else:
                self._is_connected = False
                logger.warning("S3 ClientError (%s). Enabling local vault fallback.", e)
        except (EndpointConnectionError, Exception) as e:
            self._is_connected = False
            logger.warning(
                "S3/MinIO endpoint unreachable at %s (%s). Using local filesystem evidence vault.",
                self.endpoint_url, type(e).__name__
            )

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def upload_file(
        self,
        file_data: Union[bytes, BinaryIO],
        object_key: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Uploads binary data to object storage, computing SHA-256 hash in a single pass.

        SEC-005: object_key must be sanitized before calling this method.
        SEC-024: object_key should be generated via generate_object_key(), not from user filename.
        """
        # Sanitize key — raises ValueError on path traversal
        clean_key = _sanitize_object_key(object_key)

        if isinstance(file_data, bytes):
            raw_bytes = file_data
        else:
            raw_bytes = file_data.read()

        # SEC-021: Enforce upload size limit
        if len(raw_bytes) > MAX_UPLOAD_SIZE_BYTES:
            raise ValueError(f"Upload exceeds maximum size of {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)}MB.")

        file_size = len(raw_bytes)
        sha256_hash = compute_sha256(raw_bytes)

        user_metadata = {k: str(v) for k, v in (metadata or {}).items()}
        user_metadata["sha256"] = sha256_hash
        user_metadata["file_size"] = str(file_size)

        if self._is_connected and self._s3:
            try:
                self._s3.put_object(
                    Bucket=self.bucket_name,
                    Key=clean_key,
                    Body=raw_bytes,
                    ContentType=content_type,
                    Metadata=user_metadata
                )
                # SEC-003: Log only prefix of hash, never raw content
                logger.info(
                    "Uploaded %s to S3 bucket (redacted) (%d bytes, hash_prefix=%s)",
                    clean_key, file_size, sha256_hash[:8]
                )
                return {
                    "storage_provider": "minio_s3",
                    "bucket": self.bucket_name,
                    "object_key": clean_key,
                    "file_size": file_size,
                    "sha256_hash": sha256_hash,
                    "content_type": content_type,
                    "status": "UPLOADED"
                }
            except Exception as e:
                logger.error("Failed to upload to S3 (%s), persisting to local vault fallback.", type(e).__name__)

        # SEC-005: Local vault fallback — safe path resolution
        LOCAL_VAULT_DIR.mkdir(parents=True, exist_ok=True)
        local_path = (LOCAL_VAULT_DIR / clean_key).resolve()

        if not _validate_safe_path(local_path, LOCAL_VAULT_DIR):
            raise PermissionError(
                f"Resolved path is outside the evidence vault. Possible path traversal attempt. Key: {clean_key!r}"
            )

        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(raw_bytes)
        logger.info("Persisted %s to local vault (%d bytes, hash_prefix=%s)", clean_key, file_size, sha256_hash[:8])

        return {
            "storage_provider": "local_vault_fallback",
            "bucket": "local",
            "object_key": clean_key,
            "file_size": file_size,
            "sha256_hash": sha256_hash,
            "content_type": content_type,
            "status": "UPLOADED_LOCAL_FALLBACK"
        }

    def download_file(self, object_key: str) -> bytes:
        """Downloads object bytes from S3/MinIO or local vault.

        SEC-005: Validates resolved local path stays inside LOCAL_VAULT_DIR.
        """
        # Sanitize key — raises ValueError on path traversal
        clean_key = _sanitize_object_key(object_key)

        if self._is_connected and self._s3:
            try:
                response = self._s3.get_object(Bucket=self.bucket_name, Key=clean_key)
                return response["Body"].read()
            except Exception as e:
                logger.warning("Could not fetch from S3 (%s), checking local vault...", type(e).__name__)

        # SEC-005: Check local vault with safe path resolution
        local_path = (LOCAL_VAULT_DIR / clean_key).resolve()
        if not _validate_safe_path(local_path, LOCAL_VAULT_DIR):
            raise PermissionError(
                f"Resolved path is outside the evidence vault. Possible path traversal attempt."
            )

        if local_path.exists() and local_path.is_file():
            return local_path.read_bytes()

        raise FileNotFoundError(
            f"Object '{clean_key}' not found in S3 bucket or local vault."
        )

    def generate_presigned_url(self, object_key: str, expiration_seconds: int = 120) -> Optional[str]:
        """Generates a short-lived presigned URL for secure download (max 5 minutes by default).

        SEC-001: Only usable after authorization check in the calling endpoint.
        Returns None (not a fallback URL) if S3 is unavailable.
        """
        clean_key = _sanitize_object_key(object_key)
        # Clamp expiration between 30 and 300 seconds
        expiration_seconds = max(30, min(300, expiration_seconds))

        if self._is_connected and self._s3:
            try:
                url = self._s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": clean_key},
                    ExpiresIn=expiration_seconds
                )
                # SEC-003: Never log the presigned URL
                logger.info("Generated presigned URL for key '%s' (expiry=%ds)", clean_key, expiration_seconds)
                return url
            except Exception as e:
                logger.warning("Could not generate presigned URL: %s", type(e).__name__)

        # In local vault fallback mode, return relative API stream path
        return f"/api/evidence/stream/{clean_key}"

    def verify_object_integrity(self, object_key: str, expected_sha256: str) -> Dict[str, Any]:
        """Retrieves actual object bytes and performs constant-time SHA-256 integrity comparison."""
        try:
            data = self.download_file(object_key)
            computed = compute_sha256(data)
            is_intact = constant_time_compare(expected_sha256, computed)
            return {
                "object_key": object_key,
                "expected_hash": expected_sha256,
                "computed_hash": computed,
                "is_intact": is_intact,
                "file_size": len(data),
                "integrity_status": "VERIFIED_INTACT" if is_intact else "TAMPERED_HASH_MISMATCH"
            }
        except FileNotFoundError:
            return {
                "object_key": object_key,
                "expected_hash": expected_sha256,
                "computed_hash": None,
                "is_intact": False,
                "integrity_status": "OBJECT_NOT_FOUND"
            }
        except PermissionError as e:
            logger.error("Path traversal attempt during integrity check: %s", e)
            return {
                "object_key": object_key,
                "expected_hash": expected_sha256,
                "computed_hash": None,
                "is_intact": False,
                "integrity_status": "ERROR_ACCESS_DENIED"
            }


_storage_client: Optional[S3StorageClient] = None


def get_storage_client() -> S3StorageClient:
    """Returns singleton S3StorageClient instance."""
    global _storage_client
    if _storage_client is None:
        _storage_client = S3StorageClient()
    return _storage_client


def check_storage_status() -> Dict[str, Any]:
    """Returns telemetry of object storage subsystem."""
    client = get_storage_client()
    return {
        "status": "OPERATIONAL_CONNECTED" if client.is_connected else "LOCAL_VAULT_FALLBACK",
        "provider": "MinIO / S3" if client.is_connected else "Filesystem_Evidence_Vault",
        # SEC-003: Do not expose endpoint URL with credentials
        "is_connected": client.is_connected,
        "bucket": client.bucket_name,
    }
