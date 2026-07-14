"""Database engine and session dependency."""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# NeonDB (serverless Postgres) closes idle connections after a few minutes.
# Reusing a server-closed connection triggers a ProtocolViolation on the next
# operation (often the ROLLBACK during pool return). Guard against it:
#   - pool_pre_ping: test a connection before handing it out (checkout path)
#   - pool_recycle:  discard connections older than the idle window (return path)
#   - keepalives:    ask the OS/driver to keep the TCP socket alive
engine = create_engine(
    settings.sqlalchemy_url,
    pool_pre_ping=True,
    pool_recycle=180,  # recycle well under Neon's ~300s idle timeout
    pool_size=5,
    max_overflow=5,
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
    future=True,
)


@event.listens_for(engine, "connect")
def _set_search_path(dbapi_connection, _record):
    """Ensure every connection resolves this app's dedicated schema first."""
    with dbapi_connection.cursor() as cur:
        cur.execute(f'SET search_path TO "{settings.db_schema}", public')


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
