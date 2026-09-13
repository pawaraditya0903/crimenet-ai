from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AlertReviewRequest(BaseModel):
    decision: str = Field(..., pattern="^(CONFIRMED_BY_INVESTIGATOR|SUPPRESSED_AS_FALSE_POSITIVE|ESCALATED_TO_SUPERVISOR|CLOSED)$")
    note: Optional[str] = ""
    investigator_id: Optional[str] = None

class AlertEscalateRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)

class SupervisorApproveRequest(BaseModel):
    decision: str = Field(..., pattern="^(SUPERVISOR_APPROVED|SUPERVISOR_REJECTED)$")
    comments: Optional[str] = Field(..., min_length=3, max_length=500)

class AlertResponse(BaseModel):
    id: str
    case_id: str
    entity_id: str
    entity_name: str
    anomaly_type: str
    anomaly_score: float
    severity: str
    algorithm: str
    confidence_level: str
    status: str
    plain_english_explanation: Optional[str] = None
    created_at: str
