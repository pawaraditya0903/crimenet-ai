from typing import Optional, List
from pydantic import BaseModel, Field

class CaseCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    description: str = Field(..., min_length=5, max_length=1000)
    stage: Optional[str] = "evidence"
    priority: Optional[str] = "high"
    squad: Optional[str] = "Cyber & Forensic Cell"
    suspects: Optional[List[str]] = []

class CaseUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    stage: Optional[str] = None
    priority: Optional[str] = None
    squad: Optional[str] = None

class CaseStageUpdateRequest(BaseModel):
    stage: str = Field(..., pattern="^(evidence|surveillance|warrant|trial|closed)$")

class CaseResponse(BaseModel):
    id: str
    title: str
    description: str
    stage: str
    priority: str
    lead_investigator_id: Optional[str] = None
    squad: str
    created_at: str
    updated_at: str
