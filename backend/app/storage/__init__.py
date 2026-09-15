"""
CrimeNet AI - Object Storage Module
Supports MinIO (Local) and S3 / Cloudflare R2 (Production)
"""
from backend.app.storage.s3_client import (
    S3StorageClient,
    get_storage_client,
    check_storage_status
)

__all__ = ["S3StorageClient", "get_storage_client", "check_storage_status"]
