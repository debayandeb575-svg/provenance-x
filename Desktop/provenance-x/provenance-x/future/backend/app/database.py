from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import get_settings


settings = get_settings()


if settings.database_url.startswith("sqlite:///"):
    Path("./data").mkdir(
        parents=True,
        exist_ok=True
    )


engine = create_engine(
    settings.database_url,
    connect_args={
        "check_same_thread": False
    }
    if settings.database_url.startswith("sqlite")
    else {},
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()