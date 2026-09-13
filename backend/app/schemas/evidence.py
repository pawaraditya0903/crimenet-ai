from typing import Optional
from pydantic import BaseModel, Field

class EvidenceItemResponse(BaseModel):
    id: str
    case_id: str
    source_type: str
    filename: str
    mime_type: str
    file_size: int
    collector_id: str
    ingested_at: str
    sha256_hash: str
    classification: str
    integrity_status: str

class EvidenceVerifyResponse(BaseModel):
    evidence_id: str
    filename: str
    expected_hash: str
    computed_hash: str
    integrity_status: str
    is_tampered: bool
    verification_statement: str
