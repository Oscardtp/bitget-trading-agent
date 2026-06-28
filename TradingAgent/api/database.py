"""Read-only database connection for the API."""
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

DB_DIR = Path(__file__).parent.parent
DB_PATH = DB_DIR / "trading_agent.db"

_engine = None
_SessionLocal = None


def get_readonly_engine():
    """Create a read-only SQLite engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            f"sqlite:///{DB_PATH}",
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )

        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return _engine


def get_readonly_session() -> Generator[Session, None, None]:
    """Get a read-only database session (FastAPI dependency)."""
    global _SessionLocal
    engine = get_readonly_engine()
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
