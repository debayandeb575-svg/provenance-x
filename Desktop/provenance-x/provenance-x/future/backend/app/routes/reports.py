import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from ..database import get_db

from ..models import (
    Evidence,
    ProvenanceEvent,
    WitnessAttestation,
)

from ..schemas import (
    ReportResponse,
    EvidenceResponse,
    EventResponse,
    WitnessResponse,
)

from ..services import verify_evidence


router = APIRouter(
    prefix="/api/reports",
    tags=["reports"]
)


@router.get(
    "/{evidence_id}",
    response_model=ReportResponse
)
def report(

    evidence_id: str,

    db: Session = Depends(get_db),
):

    evidence = db.get(
        Evidence,
        evidence_id
    )

    if not evidence:

        raise HTTPException(
            status_code=404,
            detail="Evidence not found."
        )

    events_db = (

        db.query(ProvenanceEvent)

        .filter_by(
            evidence_id=evidence_id
        )

        .order_by(
            ProvenanceEvent.id.asc()
        )

        .all()
    )

    witnesses_db = (

        db.query(WitnessAttestation)

        .filter_by(
            evidence_id=evidence_id
        )

        .order_by(
            WitnessAttestation.created_at.asc()
        )

        .all()
    )

    events = [

        EventResponse(

            id=event.id,

            evidence_id=event.evidence_id,

            event_type=event.event_type,

            actor=event.actor,

            details=json.loads(
                event.details
            ),

            event_hash=event.event_hash,

            previous_hash=event.previous_hash,

            created_at=event.created_at,
        )

        for event in events_db
    ]

    witnesses = [

        WitnessResponse.model_validate(
            witness
        )

        for witness in witnesses_db
    ]

    verification = verify_evidence(
        db,
        evidence
    )

    return ReportResponse(

        evidence=EvidenceResponse.model_validate(
            evidence
        ),

        verification=verification,

        events=events,

        witnesses=witnesses,
    )