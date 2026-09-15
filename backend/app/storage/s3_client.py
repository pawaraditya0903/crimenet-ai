"""
CrimeNet AI - S3-Compatible Object Storage Client
Integrates with MinIO for local development and AWS S3 / Cloudflare R2 for production.
Stores binary evidence (CCTV footage, ANPR captures, forensic reports, datasets).
Includes constant-time cryptographic SHA-256 integrity verification.
"""

import os
import io
import hashlib
import logging
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

LOCAL_VAULT_DIR = os.path.join(BACKEND_DIR, "data", "evidence_vault")

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
            logger.warning("S3/MinIO endpoint unreachable at %s (%s). Using local filesystem evidence vault.", self.endpoint_url, e)

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
        """Uploads binary data to object storage, computing SHA-256 hash in a single pass."""
        if isinstance(file_data, bytes):
            raw_bytes = file_data
        else:
            raw_bytes = file_data.read()

        file_size = len(raw_bytes)
        sha256_hash = compute_sha256(raw_bytes)
        clean_key = object_key.lstrip("/")

        user_metadata = metadata or {}
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
                logger.info("Uploaded %s to S3 bucket '%s' (%d bytes, hash=%s)", clean_key, self.bucket_name, file_size, sha256_hash[:12])
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
                logger.error("Failed to upload to S3 (%s), persisting to local vault fallback.", e)

        # Fallback to local file-backed vault
        local_path = os.path.join(LOCAL_VAULT_DIR, clean_key)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(raw_bytes)
        logger.info("Persisted %s to local vault (%d bytes, hash=%s)", clean_key, file_size, sha256_hash[:12])

        return {
            "storage_provider": "local_vault_fallback",
            "bucket": "local",
            "object_key": clean_key,
            "file_size": file_size,
            "sha256_hash": sha256_hash,
            "content_type": content_type,
            "local_path": local_path,
            "status": "UPLOADED_LOCAL_FALLBACK"
        }

    def download_file(self, object_key: str) -> bytes:
        """Downloads object bytes from S3/MinIO or local vault."""
        clean_key = object_key.lstrip("/")
        if self._is_connected and self._s3:
            try:
                response = self._s3.get_object(Bucket=self.bucket_name, Key=clean_key)
                return response["Body"].read()
            except Exception as e:
                logger.warning("Could not fetch %s from S3 (%s), checking local vault...", clean_key, e)

        # Check local vault
        local_path = os.path.join(LOCAL_VAULT_DIR, clean_key)
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                return f.read()

        raise FileNotFoundError(f"Object '{clean_key}' not found in S3 bucket '{self.bucket_name}' or local vault.")

    def generate_presigned_url(self, object_key: str, expiration_seconds: int = 3600) -> str:
        """Generates a temporary presigned URL for secure download."""
        clean_key = object_key.lstrip("/")
        if self._is_connected and self._s3:
            try:
                return self._s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": clean_key},
                    ExpiresIn=expiration_seconds
                )
            except Exception as e:
                logger.warning("Could not generate presigned URL: %s", e)

        # Return internal relative streaming path if S3 not connected
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
        "endpoint": client.endpoint_url if client.is_connected else LOCAL_VAULT_DIR,
        "bucket": client.bucket_name,
        "is_connected": client.is_connected
    }
