"""
EchoAid database configuration.

Sets up the SQLAlchemy engine, session factory, and declarative base.
The database is initialized via init_db(), which is safe to call multiple times.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.config import settings

# connect_args is required for SQLite to allow the same connection across threads
# (FastAPI uses a thread-pool executor by default).
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.is_development,   # SQL logging in dev only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create all tables that do not yet exist.
    Safe to call on every application startup — SQLAlchemy skips existing tables.
    Import models before calling this so their metadata is registered.
    """
    # Import models here so their table metadata is registered on Base before
    # create_all is called.  The import is intentionally inside the function to
    # avoid circular-import issues at module load time.
    import backend.models  # noqa: F401  (side-effect import)

    Base.metadata.create_all(bind=engine)
