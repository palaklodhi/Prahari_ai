
"""Database engine + session helpers."""
from sqlmodel import SQLModel, Session, create_engine

from app.core.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    import app.models  # noqa: F401  ensure tables are registered on metadata
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
