from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    Text,
    ForeignKey,
    Boolean,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Evidence(Base):

    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True
    )

    original_name: Mapped[str] = mapped_column(
        String(255)
    )

    stored_name: Mapped[str] = mapped_column(
        String(255),
        unique=True
    )

    content_type: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True
    )

    size_bytes: Mapped[int] = mapped_column(
        Integer
    )

    sha256: Mapped[str] = mapped_column(
        String(64),
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="registered"
    )

    merkle_root: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True
    )

    merkle_index: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    signature: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    events = relationship(
        "ProvenanceEvent",
        back_populates="evidence",
        cascade="all, delete-orphan"
    )

    witnesses = relationship(
        "WitnessAttestation",
        back_populates="evidence",
        cascade="all, delete-orphan"
    )


class ProvenanceEvent(Base):

    __tablename__ = "provenance_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    evidence_id: Mapped[str] = mapped_column(
        ForeignKey("evidence.id"),
        index=True
    )

    event_type: Mapped[str] = mapped_column(
        String(60)
    )

    actor: Mapped[str] = mapped_column(
        String(120)
    )

    details: Mapped[str] = mapped_column(
        Text,
        default="{}"
    )

    event_hash: Mapped[str] = mapped_column(
        String(64),
        index=True
    )

    previous_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow
    )

    evidence = relationship(
        "Evidence",
        back_populates="events"
    )


class WitnessAttestation(Base):

    __tablename__ = "witness_attestations"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True
    )

    evidence_id: Mapped[str] = mapped_column(
        ForeignKey("evidence.id"),
        index=True
    )

    witness_name: Mapped[str] = mapped_column(
        String(120)
    )

    witness_type: Mapped[str] = mapped_column(
        String(60),
        default="independent"
    )

    statement: Mapped[str] = mapped_column(
        Text
    )

    attestation_hash: Mapped[str] = mapped_column(
        String(64)
    )

    signature: Mapped[str] = mapped_column(
        Text
    )

    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow
    )

    evidence = relationship(
        "Evidence",
        back_populates="witnesses"
    )