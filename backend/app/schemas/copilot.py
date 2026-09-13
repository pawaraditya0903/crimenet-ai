from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class CopilotChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    case_id: Optional[str] = "c1"
    conversation_id: Optional[str] = None

class CopilotActionConfirmRequest(BaseModel):
    action_type: str = Field(..., pattern="^(ADVANCE_STAGE|ESCALATE_ALERT|ASSIGN_INVESTIGATOR|FLAG_ENTITY)$")
    case_id: str
    target_id: str
    parameters: Optional[Dict[str, Any]] = {}
