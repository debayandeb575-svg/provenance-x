import hashlib
import json
from typing import Optional

from sqlalchemy.orm import Session

from .models import Marker
from .schemas import MarkerCreate


def sha256(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def get_last_marker(
    db: Session,
    evidence_id: str,
) -> Optional[Marker]:

    return (
        db.query(Marker)
        .filter(Marker.evidence_id == evidence_id)
        .order_by(Marker.id.desc())
        .first()
    )


def create_marker(
    db: Session,
    data: MarkerCreate,
) -> Marker:

    previous = get_last_marker(
        db,
        data.evidence_id,
    )

    previous_hash = (
        previous.marker_hash
        if previous
        else None
    )

    metadata = (
        json.dumps(
            data.metadata,
            sort_keys=True,
            separators=(",", ":"),
        )
        if data.metadata
        else None
    )

    canonical = "|".join(
        [
            data.evidence_id,
            data.marker_type,
            data.payload_hash,
            previous_hash or "",
            data.actor or "",
            metadata or "",
        ]
    )

    marker_hash = sha256(canonical)

    marker = Marker(
        evidence_id=data.evidence_id,
        marker_type=data.marker_type,
        payload_hash=data.payload_hash,
        previous_hash=previous_hash,
        marker_hash=marker_hash,
        actor=data.actor,
        metadata_json=metadata,
    )

    db.add(marker)
    db.commit()
    db.refresh(marker)

    return marker


def verify_chain(
    db: Session,
    evidence_id: str,
) -> dict:

    markers = (
        db.query(Marker)
        .filter(Marker.evidence_id == evidence_id)
        .order_by(Marker.id.asc())
        .all()
    )

    if not markers:
        return {
            "valid": False,
            "evidence_id": evidence_id,
            "reason": "No markers found",
        }

    previous_hash = None

    for marker in markers:

        if marker.previous_hash != previous_hash:
            return {
                "valid": False,
                "evidence_id": evidence_id,
                "failed_marker": marker.id,
                "reason": "Previous hash mismatch",
            }

        canonical = "|".join(
            [
                marker.evidence_id,
                marker.marker_type,
                marker.payload_hash,
                marker.previous_hash or "",
                marker.actor or "",
                marker.metadata_json or "",
            ]
        )

        expected = sha256(canonical)

        if expected != marker.marker_hash:
            return {
                "valid": False,
                "evidence_id": evidence_id,
                "failed_marker": marker.id,
                "reason": "Marker hash mismatch",
            }

        previous_hash = marker.marker_hash

    return {
        "valid": True,
        "evidence_id": evidence_id,
        "marker_count": len(markers),
        "head": previous_hash,
    }