from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .models import Base, engine, SessionLocal, Marker
from .schemas import MarkerCreate, MarkerResponse
from .service import create_marker, verify_chain


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Provenance-X Marker Log",
    version="1.0.0",
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {
        "service": "marker-log",
        "status": "ok",
    }


@app.post(
    "/markers",
    response_model=MarkerResponse,
)
def add_marker(
    data: MarkerCreate,
    db: Session = Depends(get_db),
):

    return create_marker(db, data)


@app.get(
    "/markers/{evidence_id}",
)
def list_markers(
    evidence_id: str,
    db: Session = Depends(get_db),
):

    markers = (
        db.query(Marker)
        .filter(
            Marker.evidence_id == evidence_id
        )
        .order_by(Marker.id.asc())
        .all()
    )

    return markers


@app.get(
    "/markers/{evidence_id}/verify",
)
def verify(
    evidence_id: str,
    db: Session = Depends(get_db),
):

    return verify_chain(db, evidence_id)