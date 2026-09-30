import hashlib
import json
import uuid

from pathlib import Path

from sqlalchemy.orm import Session

from .config import get_settings
from .models import (
    Evidence,
    ProvenanceEvent,
    WitnessAttestation,
)

from .crypto import (
    canonical_bytes,
    sign,
    verify_signature,
)

from .merkle import (
    merkle_root,
    proof,
    verify_proof,
)


settings = get_settings()


Path(
    settings.storage_dir
).mkdir(
    parents=True,
    exist_ok=True
)


def hash_file(path: Path) -> str:

    hasher = hashlib.sha256()

    with path.open("rb") as file:

        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):

            hasher.update(chunk)

    return hasher.hexdigest()


def add_event(
    db: Session,
    evidence: Evidence,
    event_type: str,
    actor: str,
    details: dict
):

    previous = (
        db.query(ProvenanceEvent)
        .filter_by(
            evidence_id=evidence.id
        )
        .order_by(
            ProvenanceEvent.id.desc()
        )
        .first()
    )

    previous_hash = (
        previous.event_hash
        if previous
        else None
    )

    serialized_details = json.dumps(
        details,
        sort_keys=True
    )

    payload = canonical_bytes(
        evidence.id,
        event_type,
        actor,
        serialized_details,
        previous_hash,
    )

    event_hash = hashlib.sha256(
        payload
    ).hexdigest()

    event = ProvenanceEvent(

        evidence_id=evidence.id,

        event_type=event_type,

        actor=actor,

        details=serialized_details,

        event_hash=event_hash,

        previous_hash=previous_hash,
    )

    db.add(event)

    db.flush()

    return event


def rebuild_merkle_for_all(
    db: Session
):

    items = (
        db.query(Evidence)
        .order_by(
            Evidence.created_at.asc(),
            Evidence.id.asc()
        )
        .all()
    )

    leaves = [
        item.sha256
        for item in items
    ]

    root = merkle_root(
        leaves
    )

    for index, item in enumerate(items):

        item.merkle_root = root

        item.merkle_index = index

    return root


def make_witness(
    db: Session,
    evidence: Evidence,
    payload
):

    witness_id = uuid.uuid4().hex

    attestation_hash = hashlib.sha256(

        canonical_bytes(
            evidence.id,
            payload.witness_name,
            payload.statement
        )

    ).hexdigest()

    signature = sign(
        canonical_bytes(
            evidence.id,
            attestation_hash
        )
    )

    witness = WitnessAttestation(

        id=witness_id,

        evidence_id=evidence.id,

        witness_name=payload.witness_name,

        witness_type=payload.witness_type,

        statement=payload.statement,

        attestation_hash=attestation_hash,

        signature=signature,

        verified=True,
    )

    db.add(witness)

    db.flush()

    return witness


def verify_evidence(
    db: Session,
    evidence: Evidence,
    file_hash: str | None = None,
):

    events = (
        db.query(ProvenanceEvent)
        .filter_by(
            evidence_id=evidence.id
        )
        .order_by(
            ProvenanceEvent.id.asc()
        )
        .all()
    )

    chain_valid = True

    previous = None

    for event in events:

        expected = hashlib.sha256(

            canonical_bytes(
                evidence.id,
                event.event_type,
                event.actor,
                event.details,
                event.previous_hash,
            )

        ).hexdigest()

        if (
            event.event_hash != expected
            or event.previous_hash != previous
        ):

            chain_valid = False

            break

        previous = event.event_hash

    all_items = (
        db.query(Evidence)
        .order_by(
            Evidence.created_at.asc(),
            Evidence.id.asc()
        )
        .all()
    )

    leaves = [
        item.sha256
        for item in all_items
    ]

    root = merkle_root(
        leaves
    )

    index = next(
        (
            i
            for i, item
            in enumerate(all_items)
            if item.id == evidence.id
        ),
        -1
    )

    merkle_proof = (
        proof(
            leaves,
            index
        )
        if index >= 0
        else []
    )

    merkle_ok = (

        index >= 0

        and evidence.merkle_root == root

        and verify_proof(
            evidence.sha256,
            merkle_proof,
            root
        )
    )

    witnesses = (
        db.query(WitnessAttestation)
        .filter_by(
            evidence_id=evidence.id
        )
        .all()
    )

    witnesses_ok = all(

        witness.verified

        and verify_signature(
            canonical_bytes(
                evidence.id,
                witness.attestation_hash
            ),
            witness.signature,
        )

        for witness in witnesses
    )

    signature_ok = (

        evidence.signature is not None

        and verify_signature(

            canonical_bytes(
                evidence.id,
                evidence.sha256,
                evidence.merkle_root,
            ),

            evidence.signature,
        )
    )

    hash_ok = (
        file_hash is None
        or file_hash == evidence.sha256
    )

    verified = all(
        [
            hash_ok,
            chain_valid,
            merkle_ok,
            witnesses_ok,
            signature_ok,
        ]
    )

    reason = (
        "All integrity checks passed."
        if verified
        else
        "One or more integrity checks failed."
    )

    return {

        "evidence_id":
            evidence.id,

        "exists":
            True,

        "file_hash_matches":
            hash_ok,

        "provenance_chain_valid":
            chain_valid,

        "merkle_valid":
            merkle_ok,

        "witnesses_valid":
            witnesses_ok,

        "signature_valid":
            signature_ok,

        "verified":
            verified,

        "reason":
            reason,
    }