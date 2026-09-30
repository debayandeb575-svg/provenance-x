import hashlib
import hmac
import os
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="Provenance-X Witness Service",
    version="1.0.0",
)


WITNESS_ID = os.getenv(
    "WITNESS_ID",
    "provenance-x-witness-01",
)

WITNESS_SECRET = os.getenv(
    "WITNESS_SECRET",
    "CHANGE_THIS_SECRET",
)


class WitnessRequest(BaseModel):
    evidence_id: str = Field(min_length=1)
    evidence_hash: str = Field(
        min_length=64,
        max_length=64,
    )
    statement: str = "Evidence hash witnessed"


class WitnessResponse(BaseModel):
    witness_id: str
    attestation_id: str
    evidence_id: str
    evidence_hash: str
    statement: str
    timestamp: datetime
    signature: str


def create_signature(
    evidence_id: str,
    evidence_hash: str,
    timestamp: str,
) -> str:

    message = "|".join(
        [
            evidence_id,
            evidence_hash,
            timestamp,
        ]
    )

    return hmac.new(
        WITNESS_SECRET.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()


@app.get("/health")
def health():

    return {
        "service": "witness-service",
        "status": "ok",
        "witness_id": WITNESS_ID,
    }


@app.post(
    "/attest",
    response_model=WitnessResponse,
)
def attest(
    request: WitnessRequest,
):

    timestamp = datetime.now(
        timezone.utc
    )

    timestamp_string = timestamp.isoformat()

    signature = create_signature(
        request.evidence_id,
        request.evidence_hash,
        timestamp_string,
    )

    return WitnessResponse(
        witness_id=WITNESS_ID,
        attestation_id=str(uuid.uuid4()),
        evidence_id=request.evidence_id,
        evidence_hash=request.evidence_hash,
        statement=request.statement,
        timestamp=timestamp,
        signature=signature,
    )


@app.post("/verify")
def verify_attestation(
    evidence_id: str,
    evidence_hash: str,
    timestamp: str,
    signature: str,
):

    expected = create_signature(
        evidence_id,
        evidence_hash,
        timestamp,
    )

    valid = hmac.compare_digest(
        expected,
        signature,
    )

    return {
        "valid": valid,
        "evidence_id": evidence_id,
        "witness_id": WITNESS_ID,
    }