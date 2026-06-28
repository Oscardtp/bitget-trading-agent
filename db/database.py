"""
Trading Agent - Database Configuration
SQLAlchemy engine with SQLite backend.
"""

from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from typing import Generator


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# Database path
DB_DIR = Path(__file__).parent.parent
DB_PATH = DB_DIR / "trading_agent.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"


def get_engine(echo: bool = False):
    """Create SQLAlchemy engine with SQLite optimizations."""
    engine = create_engine(
        DATABASE_URL,
        echo=echo,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )
    
    # Enable WAL mode for better concurrent read performance
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    return engine


# Global engine and session factory
_engine = None
_SessionLocal = None


def get_engine_global(echo: bool = False):
    """Get or create global engine."""
    global _engine
    if _engine is None:
        _engine = get_engine(echo=echo)
    return _engine


def get_session_factory(echo: bool = False):
    """Get or create session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine_global(echo=echo)
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Dependency injection for database sessions."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(echo: bool = False) -> None:
    """Initialize database - create all tables."""
    engine = get_engine_global(echo=echo)
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at: {DB_PATH}")


def reset_db() -> None:
    """Reset database - drop and recreate all tables."""
    engine = get_engine_global()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print(f"Database reset at: {DB_PATH}")


def get_db_info() -> dict:
    """Get database information."""
    return {
        "path": str(DB_PATH),
        "exists": DB_PATH.exists(),
        "size_bytes": DB_PATH.stat().st_size if DB_PATH.exists() else 0,
    }
