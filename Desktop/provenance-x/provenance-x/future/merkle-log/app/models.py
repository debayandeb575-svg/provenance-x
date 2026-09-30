from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Integer,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./marker_log.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


class Marker(Base):
    __tablename__ = "markers"

    id = Column(Integer, primary_key=True, index=True)

    evidence_id = Column(String(128), index=True, nullable=False)

    marker_type = Column(String(64), nullable=False)

    payload_hash = Column(String(64), nullable=False)

    previous_hash = Column(String(64), nullable=True)

    marker_hash = Column(String(64), unique=True, index=True, nullable=False)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    actor = Column(String(256), nullable=True)

    metadata_json = Column(Text, nullable=True)