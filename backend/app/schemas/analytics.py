from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AnalyticsRunRequest(BaseModel):
    damping_factor: Optional[float] = Field(0.85, ge=0.1, le=0.99)
    louvain_resolution: Optional[float] = Field(1.0, ge=0.1, le=5.0)
    contamination_rate: Optional[float] = Field(0.05, ge=0.01, le=0.5)

class CDRBatchRequest(BaseModel):
    records: List[Dict[str, Any]] = Field(..., min_length=1)

class TrilaterationRequest(BaseModel):
    towers: Optional[List[Dict[str, Any]]] = None

class ShortestPathRequest(BaseModel):
    source: str
    target: str
    weighted: Optional[bool] = True
