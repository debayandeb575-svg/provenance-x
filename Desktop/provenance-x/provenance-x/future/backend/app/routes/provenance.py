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
)


router = APIRouter(
    prefix="/api/provenance",
    tags=["provenance"]
)


@router.get(
    "/{evidence_id}"
)
def provenance_timeline(

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

    events = (

        db.query(ProvenanceEvent)

        .filter_by(
            evidence_id=evidence_id
        )

        .order_by(
            ProvenanceEvent.id.asc()
        )

        .all()
    )

    return {

        "evidence_id":
            evidence_id,

        "sha256":
            evidence.sha256,

        "merkle_root":
            evidence.merkle_root,

        "events": [

            {

                "id":
                    event.id,

                "type":
                    event.event_type,

                "actor":
                    event.actor,

                "details":
                    json.loads(
                        event.details
                    ),

                "hash":
                    event.event_hash,

                "previous_hash":
                    event.previous_hash,

                "created_at":
                    event.created_at,
            }

            for event in events
        ],
    }