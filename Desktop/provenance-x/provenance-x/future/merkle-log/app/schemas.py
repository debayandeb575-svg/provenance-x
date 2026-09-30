from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class MarkerCreate(BaseModel):
    evidence_id: str = Field(min_length=1, max_length=128)
    marker_type: str = Field(min_length=1, max_length=64)
    payload_hash: str = Field(min_length=64, max_length=64)
    actor: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MarkerResponse(BaseModel):
    id: int
    evidence_id: str
    marker_type: str
    payload_hash: str
    previous_hash: Optional[str]
    marker_hash: str
    created_at: datetime
    actor: Optional[str]

    class Config:
        from_attributes = True