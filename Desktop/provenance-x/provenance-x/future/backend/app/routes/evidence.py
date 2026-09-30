import json
import uuid

from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    Query,
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db

from ..models import (
    Evidence,
    ProvenanceEvent,
)

from ..schemas import (
    EvidenceResponse,
    EventCreate,
    EventResponse,
    VerifyResponse,
)

from ..crypto import (
    canonical_bytes,
    sign,
)

from ..services import (
    hash_file,
    add_event,
    rebuild_merkle_for_all,
    verify_evidence,
)


router = APIRouter(
    prefix="/api/evidence",
    tags=["evidence"]
)


settings = get_settings()


@router.post(
    "/upload",
    response_model=EvidenceResponse
)
async def upload_evidence(

    file: UploadFile = File(...),

    actor: str = Query(
        default="web-user"
    ),

    db: Session = Depends(get_db),
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    evidence_id = uuid.uuid4().hex

    safe_name = Path(
        file.filename
    ).name

    stored_name = (
        f"{evidence_id}_{safe_name}"
    )

    destination = (
        Path(settings.storage_dir)
        / stored_name
    )

    total = 0

    max_bytes = (
        settings.max_upload_mb
        * 1024
        * 1024
    )

    try:

        with destination.open("wb") as output:

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                total += len(chunk)

                if total > max_bytes:

                    destination.unlink(
                        missing_ok=True
                    )

                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "Maximum upload size is "
                            f"{settings.max_upload_mb} MB."
                        ),
                    )

                output.write(chunk)

    except HTTPException:

        raise

    except Exception as exc:

        destination.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {exc}"
        )

    digest = hash_file(
        destination
    )

    evidence = Evidence(

        id=evidence_id,

        original_name=safe_name,

        stored_name=stored_name,

        content_type=file.content_type,

        size_bytes=total,

        sha256=digest,

        status="registered",
    )

    db.add(evidence)

    db.flush()

    add_event(

        db,

        evidence,

        "REGISTERED",

        actor,

        {
            "filename": safe_name,

            "content_type":
                file.content_type,

            "size_bytes":
                total,

            "sha256":
                digest,
        },
    )

    root = rebuild_merkle_for_all(
        db
    )

    evidence.signature = sign(

        canonical_bytes(
            evidence.id,
            evidence.sha256,
            root,
        )
    )

    db.commit()

    db.refresh(evidence)

    return evidence


@router.get(
    "",
    response_model=list[EvidenceResponse]
)
def list_evidence(

    limit: int = Query(
        50,
        ge=1,
        le=200
    ),

    db: Session = Depends(get_db),
):

    return (
        db.query(Evidence)
        .order_by(
            Evidence.created_at.desc()
        )
        .limit(limit)
        .all()
    )


@router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse
)
def get_evidence(

    evidence_id: str,

    db: Session = Depends(get_db),
):

    item = db.get(
        Evidence,
        evidence_id
    )

    if not item:

        raise HTTPException(
            status_code=404,
            detail="Evidence not found."
        )

    return item


@router.post(
    "/{evidence_id}/events",
    response_model=EventResponse
)
def create_event(

    evidence_id: str,

    payload: EventCreate,

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

    event = add_event(

        db,

        evidence,

        payload.event_type,

        payload.actor,

        payload.details,
    )

    db.commit()

    db.refresh(event)

    return {

        **event.__dict__,

        "details":
            json.loads(event.details),
    }


@router.get(
    "/{evidence_id}/events",
    response_model=list[EventResponse]
)
def list_events(

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

    return [

        {
            **event.__dict__,

            "details":
                json.loads(
                    event.details
                ),
        }

        for event in events
    ]


@router.post(
    "/{evidence_id}/verify",
    response_model=VerifyResponse
)
def verify(

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

    return verify_evidence(
        db,
        evidence
    )


@router.get(
    "/{evidence_id}/download"
)
def download(

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

    path = (
        Path(settings.storage_dir)
        / evidence.stored_name
    )

    if not path.exists():

        raise HTTPException(
            status_code=404,
            detail="Stored evidence file is missing."
        )

    return FileResponse(

        path,

        filename=evidence.original_name,

        media_type=(
            evidence.content_type
            or "application/octet-stream"
        ),
    )