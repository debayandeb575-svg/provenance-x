from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
)


class HealthResponse(BaseModel):

    status: str
    service: str
    version: str


class EvidenceResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: str
    original_name: str
    content_type: str | None
    size_bytes: int
    sha256: str
    status: str
    merkle_root: str | None
    merkle_index: int | None
    created_at: datetime


class EventCreate(BaseModel):

    event_type: str = Field(
        min_length=2,
        max_length=60
    )

    actor: str = Field(
        min_length=2,
        max_length=120
    )

    details: dict = Field(
        default_factory=dict
    )


class EventResponse(BaseModel):

    id: int
    evidence_id: str
    event_type: str
    actor: str
    details: dict
    event_hash: str
    previous_hash: str | None
    created_at: datetime


class WitnessCreate(BaseModel):

    witness_name: str = Field(
        min_length=2,
        max_length=120
    )

    witness_type: str = Field(
        default="independent",
        max_length=60
    )

    statement: str = Field(
        min_length=5,
        max_length=2000
    )


class WitnessResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: str
    evidence_id: str
    witness_name: str
    witness_type: str
    statement: str
    attestation_hash: str
    signature: str
    verified: bool
    created_at: datetime


class VerifyResponse(BaseModel):

    evidence_id: str
    exists: bool
    file_hash_matches: bool
    provenance_chain_valid: bool
    merkle_valid: bool
    witnesses_valid: bool
    signature_valid: bool
    verified: bool
    reason: str


class ReportResponse(BaseModel):

    evidence: EvidenceResponse
    verification: VerifyResponse
    events: list[EventResponse]
    witnesses: list[WitnessResponse]