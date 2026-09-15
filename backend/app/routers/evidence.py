from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form, Response
from typing import Optional, List
from backend.app.schemas.evidence import EvidenceItemResponse, EvidenceVerifyResponse
from backend.app.security.rbac import require_authenticated_user
from backend.app.forensics.evidence_vault import EVIDENCE_DISCLAIMER
from backend.app.services.evidence_service import EvidenceService
from backend.app.storage.s3_client import get_storage_client
from backend.app.database.connection import db_session_context
from backend.app.models.pg_models import EvidenceItem

router = APIRouter(prefix="/api/evidence", tags=["Digital Evidence"])

@router.get("/items")
async def list_evidence_items(case_id: Optional[str] = None, claims: dict = Depends(require_authenticated_user)):
    """Returns digital evidence items registered in the chain of custody ledger."""
    with db_session_context() as session:
        query = session.query(EvidenceItem)
        if case_id:
            query = query.filter(EvidenceItem.case_id == case_id)
        items = query.all()
        rows = [
            {
                "id": i.id,
                "case_id": i.case_id,
                "source_type": i.source_type,
                "filename": i.filename,
                "mime_type": i.mime_type,
                "file_size": i.file_size,
                "collector_id": i.collector_id,
                "ingested_at": i.ingested_at,
                "sha256_hash": i.sha256_hash,
                "classification": i.classification,
                "integrity_status": i.integrity_status,
                "object_key": i.object_key,
                "storage_provider": i.storage_provider
            }
            for i in items
        ]

    return {
        "total_items": len(rows),
        "evidence_items": rows,
        "chain_of_custody_statement": EVIDENCE_DISCLAIMER
    }

@router.post("/upload")
async def upload_evidence_artifact(
    file: UploadFile = File(...),
    case_id: str = Form("c1"),
    source_type: str = Form("FORENSIC_EXAMINATION_EXPORT"),
    classification: str = Form("RESTRICTED_SYNTHETIC_DEMO"),
    claims: dict = Depends(require_authenticated_user)
):
    """Securely uploads an evidence binary object to S3/MinIO,
    computes bit-level SHA-256 hash, stores relational metadata in PostgreSQL,
    and anchors the hash to the Merkle audit chain.
    """
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded evidence file is empty.")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds maximum evidence upload limit (50MB).")

    collector_id = claims.get("sub") or claims.get("user_id") or "FORENSIC_OFFICER"
    mime_type = file.content_type or "application/octet-stream"

    res = EvidenceService.register_evidence(
        case_id=case_id,
        source_type=source_type,
        filename=file.filename or "evidence.bin",
        file_bytes=content,
        collector_id=collector_id,
        mime_type=mime_type,
        classification=classification
    )
    return res

@router.get("/verify/{evidence_id}")
async def verify_evidence_endpoint(evidence_id: str, claims: dict = Depends(require_authenticated_user)):
    """Verifies evidence file integrity against recorded SHA-256 hash using
    constant-time bit-level comparison against actual object storage bytes.
    """
    res = EvidenceService.verify_evidence(evidence_id)
    if res.get("error") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail=f"Evidence item '{evidence_id}' not found.")

    return {
        "evidence_id": res["evidence_id"],
        "filename": res["filename"],
        "expected_hash": res["expected_hash"],
        "computed_hash": res.get("computed_hash"),
        "integrity_status": res["integrity_status"],
        "verification_result": "MATCH" if res.get("is_intact") else "TAMPERED",
        "storage_provider": res.get("storage_provider"),
        "disclaimer": EVIDENCE_DISCLAIMER
    }

@router.get("/download/{evidence_id}")
async def download_evidence_endpoint(evidence_id: str, claims: dict = Depends(require_authenticated_user)):
    """Downloads evidence object binary bytes from S3/MinIO object storage."""
    with db_session_context() as session:
        item = session.query(EvidenceItem).filter(EvidenceItem.id == evidence_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Evidence item '{evidence_id}' not found.")
        object_key = item.object_key or f"evidence/{item.case_id}/{item.id}_{item.filename}"
        filename = item.filename
        mime = item.mime_type

    storage = get_storage_client()
    try:
        data = storage.download_file(object_key)
        return Response(
            content=data,
            media_type=mime,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve evidence file from storage: {e}")

@router.get("/merkle-root")
async def get_merkle_evidence_root():
    """Constructs a genuine Binary Merkle Tree across all stored evidence SHA-256 hashes
    and returns the Merkle Root hash and tree depth.
    """
    return EvidenceService.get_merkle_root()
