"""
CrimeNet AI — Evidence Management Routes

Security fixes:
  SEC-007: MIME type validated against allowlist before serving.
  SEC-013: Case-level access check enforced on upload and download.
  SEC-022: Merkle-root endpoint requires authentication.
  SEC-024: Object keys are UUID-based and server-generated.
"""
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form, Response, Query
from typing import Optional, List
from backend.app.schemas.evidence import EvidenceItemResponse, EvidenceVerifyResponse
from backend.app.security.rbac import require_authenticated_user, require_case_access, ForensicRole, require_roles
from backend.app.forensics.evidence_vault import EVIDENCE_DISCLAIMER
from backend.app.services.evidence_service import EvidenceService
from backend.app.storage.s3_client import get_storage_client, validate_mime_type
from backend.app.database.connection import db_session_context
from backend.app.models.pg_models import EvidenceItem
from backend.app.models.database import get_db
from backend.app.audit.chain import append_audit_event

router = APIRouter(prefix="/api/evidence", tags=["Digital Evidence"])

# Allowed MIME types that can be served in-response (all others default to octet-stream)
_SAFE_SERVE_TYPES = {
    "application/pdf",
    "application/json",
    "application/octet-stream",
    "text/plain",
    "text/csv",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "video/mp4",
    "audio/mpeg",
}


def _verify_case_access(case_id: str, user_id: str, role: str) -> bool:
    """Returns True if user is permitted to access this case's evidence."""
    if role == ForensicRole.SUPERVISORY_OFFICER:
        return True
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM case_assignments WHERE case_id = ? AND user_id = ?",
            (case_id, user_id)
        )
        if cursor.fetchone():
            return True
        cursor.execute(
            "SELECT lead_investigator_id FROM cases WHERE id = ?",
            (case_id,)
        )
        row = cursor.fetchone()
        if row and row["lead_investigator_id"] == user_id:
            return True
    return False


@router.get("/items")
async def list_evidence_items(
    case_id: Optional[str] = Query(None, max_length=64),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    claims: dict = Depends(require_authenticated_user)
):
    """Returns digital evidence items registered in the chain of custody ledger."""
    user_id = claims.get("sub")
    role = claims.get("role")

    with db_session_context() as session:
        query = session.query(EvidenceItem)
        if case_id:
            # SEC-013: Enforce case access check when filtering by case
            if not _verify_case_access(case_id, user_id, role):
                raise HTTPException(
                    status_code=403,
                    detail=f"Access Denied: You are not assigned to case '{case_id}'."
                )
            query = query.filter(EvidenceItem.case_id == case_id)
        elif role != ForensicRole.SUPERVISORY_OFFICER:
            # Non-supervisors without a case filter: only return evidence for their assigned cases
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT case_id FROM case_assignments WHERE user_id = ?",
                    (user_id,)
                )
                assigned_case_ids = [r["case_id"] for r in cursor.fetchall()]
            query = query.filter(EvidenceItem.case_id.in_(assigned_case_ids))

        # Pagination
        total = query.count()
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

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
        "total_items": total,
        "page": page,
        "page_size": page_size,
        "evidence_items": rows,
        "chain_of_custody_statement": EVIDENCE_DISCLAIMER
    }


@router.post("/upload")
async def upload_evidence_artifact(
    request: Request,
    file: UploadFile = File(...),
    case_id: str = Form(..., max_length=64),
    source_type: str = Form("FORENSIC_EXAMINATION_EXPORT", max_length=64),
    classification: str = Form("RESTRICTED_SYNTHETIC_DEMO", max_length=64),
    claims: dict = Depends(require_authenticated_user)
):
    """Securely uploads an evidence binary object to S3/MinIO.

    SEC-013: Verifies case-level access before upload.
    SEC-021: Validates MIME type against allowlist.
    SEC-024: Object key is UUID-based, not derived from filename.
    """
    user_id = claims.get("sub")
    role = claims.get("role")
    client_ip = request.client.host if request.client else "127.0.0.1"
    correlation_id = getattr(request.state, "correlation_id", "")

    # SEC-013: Verify case access before accepting upload
    if not _verify_case_access(case_id, user_id, role):
        raise HTTPException(
            status_code=403,
            detail=f"Access Denied: You are not assigned to case '{case_id}'."
        )

    # SEC-021: Validate MIME type
    try:
        safe_mime = validate_mime_type(file.content_type or "application/octet-stream")
    except ValueError as e:
        raise HTTPException(status_code=415, detail=str(e))

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded evidence file is empty.")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds maximum evidence upload limit (50MB).")

    collector_id = user_id or "FORENSIC_OFFICER"
    # SEC-024: display_filename is stored for UI only; never used as storage key
    display_filename = (file.filename or "evidence.bin")[:256]

    res = EvidenceService.register_evidence(
        case_id=case_id,
        source_type=source_type,
        filename=display_filename,
        file_bytes=content,
        collector_id=collector_id,
        mime_type=safe_mime,
        classification=classification
    )
    return res


@router.get("/verify/{evidence_id}")
async def verify_evidence_endpoint(
    evidence_id: str,
    request: Request,
    claims: dict = Depends(require_roles([
        ForensicRole.SUPERVISORY_OFFICER,
        ForensicRole.LEAD_INVESTIGATOR,
        ForensicRole.FORENSIC_ANALYST
    ]))
):
    """Verifies evidence file integrity against recorded SHA-256 hash.

    Restricted to Forensic Analysts and above.
    """
    user_id = claims.get("sub")
    role = claims.get("role")
    client_ip = request.client.host if request.client else "127.0.0.1"
    correlation_id = getattr(request.state, "correlation_id", "")

    # Fetch the case_id first to enforce case access
    with db_session_context() as session:
        item = session.query(EvidenceItem).filter(EvidenceItem.id == evidence_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Evidence item '{evidence_id}' not found.")
        ev_case_id = item.case_id

    # SEC-013: Case access check
    if not _verify_case_access(ev_case_id, user_id, role):
        raise HTTPException(
            status_code=403,
            detail=f"Access Denied: You are not assigned to case '{ev_case_id}'."
        )

    res = EvidenceService.verify_evidence(evidence_id)
    if res.get("error") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail=f"Evidence item '{evidence_id}' not found.")

    append_audit_event(
        actor_id=user_id,
        role=role,
        action="EVIDENCE_INTEGRITY_VERIFICATION",
        resource=f"evidence:{evidence_id}",
        payload={
            "evidence_id": evidence_id,
            "case_id": ev_case_id,
            "integrity_status": res["integrity_status"]
        },
        ip_address=client_ip,
        correlation_id=correlation_id
    )

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
async def download_evidence_endpoint(
    evidence_id: str,
    request: Request,
    claims: dict = Depends(require_authenticated_user)
):
    """Downloads evidence object binary bytes from S3/MinIO object storage.

    SEC-007: MIME type validated against allowlist before serving.
    SEC-013: Case-level access verified before returning bytes.
    """
    user_id = claims.get("sub")
    role = claims.get("role")
    client_ip = request.client.host if request.client else "127.0.0.1"
    correlation_id = getattr(request.state, "correlation_id", "")

    with db_session_context() as session:
        item = session.query(EvidenceItem).filter(EvidenceItem.id == evidence_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Evidence item '{evidence_id}' not found.")

        ev_case_id = item.case_id
        object_key = item.object_key
        # SEC-007: Validate the stored MIME type against allowlist
        raw_mime = item.mime_type or "application/octet-stream"
        safe_mime = raw_mime if raw_mime in _SAFE_SERVE_TYPES else "application/octet-stream"
        # Sanitize filename for Content-Disposition — remove quotes and control chars
        display_filename = (item.filename or "evidence.bin").replace('"', '').replace('\n', '').replace('\r', '')

    # SEC-013: Case access check
    if not _verify_case_access(ev_case_id, user_id, role):
        raise HTTPException(
            status_code=403,
            detail=f"Access Denied: You are not assigned to case '{ev_case_id}'."
        )

    # Audit the download attempt
    append_audit_event(
        actor_id=user_id,
        role=role,
        action="EVIDENCE_DOWNLOAD",
        resource=f"evidence:{evidence_id}",
        payload={"evidence_id": evidence_id, "case_id": ev_case_id},
        ip_address=client_ip,
        correlation_id=correlation_id
    )

    storage = get_storage_client()
    try:
        data = storage.download_file(object_key)
    except (FileNotFoundError, PermissionError) as e:
        raise HTTPException(status_code=404, detail="Evidence file not found in storage.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve evidence file from storage.")

    return Response(
        content=data,
        media_type=safe_mime,
        headers={
            # Force download — never render in browser
            "Content-Disposition": f'attachment; filename="{display_filename}"',
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "no-store, no-cache, must-revalidate",
        }
    )


@router.get("/merkle-root")
async def get_merkle_evidence_root(claims: dict = Depends(require_authenticated_user)):
    """Constructs a genuine Binary Merkle Tree across all stored evidence SHA-256 hashes.

    SEC-022: Requires authentication. Previously unauthenticated.
    """
    return EvidenceService.get_merkle_root()
