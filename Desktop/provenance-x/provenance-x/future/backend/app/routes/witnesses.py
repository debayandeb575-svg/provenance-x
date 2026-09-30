from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from ..database import get_db

from ..models import (
    Evidence,
    WitnessAttestation,
)

from ..schemas import (
    WitnessCreate,
    WitnessResponse,
)

from ..services import make_witness


router = APIRouter(
    prefix="/api/witnesses",
    tags=["witnesses"]
)


@router.post(
    "/{evidence_id}",
    response_model=WitnessResponse
)
def create_witness(

    evidence_id: str,

    payload: WitnessCreate,

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

    witness = make_witness(
        db,
        evidence,
        payload
    )

    db.commit()

    db.refresh(witness)

    return witness


@router.get(
    "/{evidence_id}",
    response_model=list[WitnessResponse]
)
def list_witnesses(

    evidence_id: str,

    db: Session = Depends(get_db),
):

    if not db.get(
        Evidence,
        evidence_id
    ):

        raise HTTPException(
            status_code=404,
            detail="Evidence not found."
        )

    return (

        db.query(
            WitnessAttestation
        )

        .filter_by(
            evidence_id=evidence_id
        )

        .order_by(
            WitnessAttestation.created_at.desc()
        )

        .all()
    )